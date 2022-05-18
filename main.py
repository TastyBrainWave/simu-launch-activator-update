import base64
import datetime
import os
from functools import partial

import cv2
import numpy as np
from fastapi.encoders import jsonable_encoder
from ppadb.client import Client as AdbClient
from ppadb.client_async import ClientAsync as AdbClientAsync
from ppadb.device import Device
from ppadb.device_async import DeviceAsync
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from multiprocessing import Process, Pool, cpu_count
from fastapi import FastAPI, UploadFile, File, Form, Depends

from ppadb import InstallError
from starlette.requests import Request
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from helpers import launch_app, save_file, process_devices
from models_pydantic import Volume, Devices, Experience, NewExperience
from sql_app import models, crud
from sql_app.crud import get_all_apk_details, get_apk_details
from sql_app.database import engine, SessionLocal
from sql_app.schemas import APKDetailsCreate, APKDetailsBase

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

simu_application_name = ""


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


BASE_PORT = 5555

client: AdbClient = AdbClient(host="127.0.0.1", port=5037)
client_async: AdbClientAsync = AdbClientAsync(host="127.0.0.1", port=5037)


def check_adb_running(func):
    def wrapper(*args, **kwargs):
        try:
            client.devices()
        except RuntimeError as e:
            if e.__str__().find("Is adb running on your computer?"):
                print("ADB Server not running, starting it now!")
                command = os.system("adb start-server")
                print(command)
        func(*args, **kwargs)

    return wrapper


@check_adb_running
@app.get("/devices")
async def devices():
    devices = []
    errs = []

    try:
        device: Device
        for device in client.devices():
            devices.append(str(device.serial))
    except RuntimeError as e:
        errs.append(str(e))
    return {'devices': devices, 'errs': errs}


@check_adb_running
@app.get("/")
async def home(request: Request, db: Session = Depends(get_db)):
    """
        View mainly responsible for handling the front end, since nothing will happen on the backend at this endpoint.
    :param db: the DB dependency
    :param request: the Request() object
    :return: a TemplateResponse object containing the homepage
    """

    uploaded_experiences = get_all_apk_details(db)

    for item in uploaded_experiences:
        print(item.apk_name)

    global simu_application_name

    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "choices": [item.apk_name for item in uploaded_experiences],
            "app_name": simu_application_name,
        },
    )


@check_adb_running
@app.post("/start")
async def start(payload: Devices, db: Session = Depends(get_db)):
    """
        Starts the experience on all devices through the adb shell commands.

    :param payload: a list of devices which the experience will start on. Not providing any will start the experience on all devices
    :param db: the database dependency
    :return: dictionary of all device serial numbers
    """
    client_list = process_devices(client, payload)

    global simu_application_name

    item = jsonable_encoder(crud.get_apk_details(db, apk_name=simu_application_name))

    try:
        if item is None:
            return {
                "success": False,
                "error": "Could not start experience. Are you sure you selected one?",
            }

        print(
            "Starting experience "
            + simu_application_name
            + " on "
            + str(len(client_list))
            + " devices"
        )

        pool = Pool(cpu_count())
        launch_func = partial(
            launch_app,
            app_name=item["apk_name"],
            d_type=item["device_type"],
            command=item["command"],
        )
        results = pool.map(launch_func, client_list)
        pool.close()
        pool.join()
    except RuntimeError as e:
        return {"success": False, "error": e.__str__()}

    return {"success": True, "device_count": len(client_list)}


@app.post("/upload")
async def upload(
        file: UploadFile = File(...),
        command: str = Form(...),
        db: Session = Depends(get_db),
):
    try:
        contents = await file.read()
        save_file(file.filename, contents)

        global simu_application_name
        simu_application_name = file.filename

        device_type = 0 if command == "android" else 1

        item = APKDetailsBase(
            apk_name=file.filename,
            command="" if command == "android" else command,
            device_type=device_type,
        )

        crud.create_apk_details_item(
            db=db, item=APKDetailsCreate.parse_obj(item.dict())
        )

        return {"success": True}
    except IOError as e:
        return {"success": False, "error": e.__str__()}


@check_adb_running
@app.post("/load")
async def load(payload: Experience):
    """
        Installs the experience on selected or all devices.

    :param payload: the choice of experience specified by the user
    :return: a success dictionary signifying the operation was successful
    """

    client_list = process_devices(client, payload)

    apk_paths = os.listdir("apks")
    apk_path = "apks/"

    global simu_application_name
    simu_application_name = payload.experience

    if payload.experience in apk_paths:
        apk_path += payload.experience
    else:
        return {
            "success": False,
            "error": "Cannot find the Experience APK in the directory. Make sure you uploaded it!",
        }

    try:
        for device in client_list:
            print("Installing " + apk_path + " on " + device.serial)
            p = Process(target=device.install, args=(apk_path,))
            p.start()
    except InstallError as e:
        return {"success": False, "error": e.__str__()}

    return {"success": True, "device_count": len(client_list)}


@app.post("/set-remote-experience")
async def set_remote_experience(payload: Experience):
    """
        Sets the active experience
    :param payload: containing the experience to set remotely
    :return: a success dictionary signifying the operation was successful
    """
    if payload.experience:
        global simu_application_name
        simu_application_name = payload.experience

        return {"success": True}

    return {"success": False}


@check_adb_running
@app.post("/remove-remote-experience")
async def remove_remote_experience(payload: Experience, db: Session = Depends(get_db)):
    try:
        if payload.experience:
            db.delete(get_apk_details(db, apk_name=payload.experience))
            db.commit()
            return {"success": True}

        return {"success": False}
    except SQLAlchemyError as e:
        return {"success": False, "error": e.__str__()}


@check_adb_running
@app.post("/add-remote-experience")
async def add_remote_experience(payload: NewExperience, db: Session = Depends(get_db)):
    """
        Adds a new experience, which has either been previously installed or is available on the device already.

    :param payload:
    :param db: the database dependency
    :return: a success dictionary signifying the operation was successful
    """

    try:
        device_type = 0 if payload.command == "android" else 1

        item = APKDetailsBase(
            apk_name=payload.apk_name,
            command="" if payload.command == "android" else payload.command,
            device_type=device_type,
        )

        crud.create_apk_details_item(
            db=db, item=APKDetailsCreate.parse_obj(item.dict())
        )

        print("Remote experience added!")

        return {"success": True}
    except SQLAlchemyError as e:
        return {"success": False, "error": e.__str__()}


@check_adb_running
@app.post("/stop")
async def stop(payload: Devices, db: Session = Depends(get_db)):
    """
        Stops the experience on all devices through ADB shell commands

    :param payload: a list of devices to stop the experience on
    :param db: the database dependency
    :return: a dictionary containing the success flag of the operation and any errors
    """

    client_list = process_devices(client, payload)

    global simu_application_name

    item = jsonable_encoder(crud.get_apk_details(db, apk_name=simu_application_name))

    if item is None:
        return {
            "success": False,
            "error": "No application to stop, make sure there is one running!",
        }

    app_name = (
        item["apk_name"] if ".apk" not in item["apk_name"] else item["apk_name"][:-4]
    )

    try:
        for device in client_list:
            print("Stopped experience on device " + device.serial)
            command = "am force-stop " + app_name
            device.shell(command)
    except RuntimeError as e:
        return {"success": False, "error": e.__str__()}

    return {"success": True, "stopped_app": app_name}


@check_adb_running
@app.post("/connect")
async def connect(request: Request):
    """
        Connects a device wirelessly to the server on port 5555. After the device is connected, it can be unplugged from
        the USB.

    :param request: The Request parameter which is used to receive the device data.
    :return: a dictionary containing the success flag of the operation and any errors
    """

    global BASE_PORT

    json = await request.json() if len((await request.body()).decode()) > 0 else {}

    remote_address = json["remote_address"] if "remote_address" in json else ""

    devices = client.devices()

    if not remote_address:
        device_ip = devices[0].shell("ip addr show wlan0")
        device_ip = device_ip[device_ip.find("inet "):]
        device_ip = device_ip[: device_ip.find("/")]
        device_ip = device_ip[device_ip.find(" ") + 1:]
    else:
        device_ip = remote_address

    try:
        if not remote_address:
            os.system("adb -s" + devices[0].serial + " tcpip " + str(BASE_PORT))
        working = False
        i = 0

        # Attempt connection 3 times

        while not working or i < 3:
            working = client.remote_connect(device_ip, port=BASE_PORT)
            i += 1

        if working:
            print(
                "Established connection with client " + device_ip + ":" + str(BASE_PORT)
            )

            return {"success": True, "serial": device_ip}

        return {"success": False}
    except RuntimeError as e:
        return {"success": False, "error_log": e.__str__()}


@check_adb_running
@app.post("/disconnect")
async def disconnect(payload: Devices):
    """
        Disconnects devices from the server.

    :devices: a list of devices to disconnect from
    :return: a dictionary containing the success flag of the operation and any errors
    """

    global BASE_PORT

    client_list = process_devices(client, payload)

    try:
        for device in client_list:
            print("Disconnecting device " + device.serial + " from server!")
            working = client.remote_disconnect(device.serial)
            if not working:
                print(1)
                return {
                    "success": False,
                    "error": "Encountered an error disconnecting device with ID/IP: "
                             + device.serial,
                }

        return {"success": True}
    except RuntimeError as e:
        return {"success": False, "error_log": e.__str__()}


@app.post("/exit-server")
async def exit_server():
    """
        Kills the ADB server and all connections with devices. Essentially a system shutdown, where the FastAPI backend
        remains alive.


    :return: a dictionary containing the success flag
    """

    try:
        result = client.kill()
    except RuntimeError as e:
        return {"success": False, "errors": e.__str__()}

    return {"success": result}


@check_adb_running
@app.get("/screen-grab")
async def screen_grab(request: Request):
    """
        Gets a screenshot from every device.
    :param request: the Request object
    :return: a dictionary containing the success flag
    """

    devices = client.devices()

    screen_caps_folder = "screenshots/"

    try:
        folder = (
                screen_caps_folder + datetime.datetime.now().strftime("%m%d%Y%H%M%S") + "/"
        )
        os.makedirs(folder)
        i = 0
        for device in devices:
            result = device.screencap()
            with open(folder + "screen" + str(i) + ".png", "wb") as fp:
                fp.write(result)
            i += 1
    except RuntimeError as e:
        return {"success": False, "errors": e.__str__()}

    return {"success": True}


@check_adb_running
@app.post("/volume")
async def volume(payload: Volume):
    client_list = process_devices(client, payload)

    fails = []
    for device in client_list:
        try:
            outcome = device.shell(f'media volume --stream 3 --set {payload.volume}')
        except RuntimeError as e:
            fails.append(e)

    if fails:

        return {"success": False, "fails": str(fails)}

    return {"success": True}


my_devices = None
screen_shots_cache = {}


def check_image(device_serial, refresh_ms, size):
    async def gen_image():

        my_width = 192
        my_height = 108

        device: DeviceAsync = await client_async.device(device_serial)
        device_sync: Device = client.device(device)
        device_sync.shell(f'adb shell setprop debug.oculus.capture.width {my_width}')
        device_sync.shell(f'adb shell setprop debug.oculus.capture.height {my_height}')
        im = await device.screencap()

        image = cv2.imdecode(np.frombuffer(im, np.uint8), cv2.IMREAD_COLOR)
        image = image[0:image.shape[0], 0: int(image.shape[1] * .5)]

        _, encoded_img = cv2.imencode('.png', image)
        return base64.b64encode(encoded_img).decode("utf-8")

    timestamp = datetime.datetime.now()

    if device_serial not in screen_shots_cache:
        screen_shots_cache[device_serial] = {}
    if size not in screen_shots_cache[device_serial]:
        ancient = datetime.datetime.now() - datetime.timedelta(hours=10)
        screen_shots_cache[device_serial][size] = {'timestamp': ancient, 'file_id': None}
    if screen_shots_cache[device_serial][size]['timestamp'] + datetime.timedelta(
            milliseconds=refresh_ms) < timestamp:
        screen_shots_cache[device_serial][size]['timestamp'] = timestamp
        try:
            screen_shots_cache[device_serial][size]['file_id'] = gen_image()
        except RuntimeError as e:
            return False

    return True


@check_adb_running
@app.get("/device-screen/{refresh_ms}/{size}/{device_serial}")
async def devicescreen(request: Request, refresh_ms: int, size: str, device_serial: str):

    success = check_image(device_serial, refresh_ms, size)

    if not success:
        return {'success': False}

    image = screen_shots_cache[device_serial][size]['file_id']
    err = None
    return {'base64_image': image}


@app.get("/devices-modal-start")
async def devices_start(request: Request):
    return templates.TemplateResponse("htmx/devices_modal.html", {"request": request})


@check_adb_running
@app.get("/linkup")
async def linkup(request: Request):
    global my_devices
    devices = client.devices()
    my_devices = {device.serial: device for device in devices}

    for device in devices:
        device.shell('adb shell setprop debug.oculus.capture.width 192')
        device.shell('adb shell setprop debug.oculus.capture.height 108')

    return templates.TemplateResponse("htmx/devices.html", {"request": request, "devices": client.devices()})


@check_adb_running
@app.get("/device-button/{device_serial}/{button}")
async def device_button(request: Request, device_serial: str, button: str):
    commands = {'power': ['/dev/input/event2 1 74 1', '/dev/input/event2 0 0 0'],
                'vol-up': ['/dev/input/event2 1 73 1', '/dev/input/event2 0 0 0'],
                'vol-down': ['/dev/input/event2 1 72 1', '/dev/input/event2 0 0 0']}
    [button_down, button_up] = commands.get(button)
    print(button_down, button_up, 2233)
    device: Device = my_devices[device_serial]
    print(0, device.shell("chmod 666 /dev/input/event0"))
    print(0, device.shell("chmod 666 /dev/input/event1"))
    print(11, device.shell('sendevent ' + button_down), 159)
    print(11, device.shell('sendevent ' + button_up), 222)
    print(11, device.shell('sendevent ' + button_down), 1591)
    print(11, device.shell('sendevent ' + button_up), 2221)
    print(411, device.shell('adb shell media volume --stream 3 --set 15'), 2221)

    pass