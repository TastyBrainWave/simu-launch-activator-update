import base64
import datetime
import json
import os
from functools import partial

import cv2
import numpy as np
import sqlalchemy
from fastapi.encoders import jsonable_encoder
from ppadb.device import Device
from ppadb.device_async import DeviceAsync
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from helpers import launch_app, save_file, BASE_DIR
from multiprocessing import Process, Pool, cpu_count
from typing import List

from fastapi import FastAPI, UploadFile, File, Depends, Body
from fastapi import FastAPI, UploadFile, File, Form
from ppadb import InstallError
from starlette.requests import Request
from starlette.responses import StreamingResponse, FileResponse, RedirectResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
import tempfile
from ppadb.client import Client as AdbClient

from models_pydantic import Volume, Devices, Experience
from sql_app import models, schemas, crud
from sql_app.crud import get_all_apk_details, get_apk_details
from sql_app.database import engine, SessionLocal
from sql_app.schemas import APKDetailsCreate, APKDetails, APKDetailsBase

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

client = AdbClient(host="127.0.0.1", port=5037)

def check_adb_running(func):

    def wrapper(*args, **kwargs):
        try:
            devices = client.devices()

        except RuntimeError as e:
            if e.__str__().find("Is adb running on your computer?"):
                print("ADB Server not running, starting it now!")
                command = os.system("adb start-server")
                print(command)
        func(*args, **kwargs)

    return wrapper


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

    print([device.serial for device in client.devices()])

    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "choices": [item.apk_name for item in uploaded_experiences],
            "app_name": simu_application_name,
            "devices_connected": [device.serial for device in client.devices()],
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

    client_list = (
        client.devices()
        if not payload.devices
        else [Device(client, device) for device in payload.devices]
    )

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

    client_list = (
        client.devices()
        if not payload.devices
        else [Device(client, device) for device in payload.devices]
    )

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
    :param set_choices: the form field of choices
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
async def add_remote_experience(
        apk_name: str = Form(...), command: str = Form(...), db: Session = Depends(get_db)
):
    """
        Adds a new experience, which has either been previously installed or is available on the device already.
    :param apk_name: the name of the APK which includes the .apk extension
    :param command: the command that the experience needs to execute
    :param db: the database dependency
    :return: a success dictionary signifying the operation was successful
    """

    try:
        device_type = 0 if command == "android" else 1

        item = APKDetailsBase(
            apk_name=apk_name,
            command="" if command == "android" else command,
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

    :param devices: a list of devices to stop the experience on
    :param db: the database dependency
    :return: a dictionary containing the success flag of the operation and any errors
    """

    client_list = (
        client.devices()
        if not payload.devices
        else [Device(client, device) for device in payload.devices]
    )

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

        while not working and i < 3:
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
async def disconnect(devices: list = Form(...)):
    """
        Disconnects devices from the server.

    :devices: a list of devices to disconnect from
    :return: a dictionary containing the success flag of the operation and any errors
    """

    global BASE_PORT

    client_list = (
        client.devices()
        if not devices
        else [Device(client, device) for device in devices]
    )

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
    for device in client.devices():
        outcome = device.shell(f'media volume --stream 3 --set {payload.volume}')

    return {"success": True}


my_devices = None
screen_shots_cache = {}


def check_image(device_serial, refresh_ms, size):
    def gen_image():

        with tempfile.NamedTemporaryFile(mode="w+b", suffix=".png", delete=False) as FOUT:
            try:
                device: Device = my_devices[device_serial]
            except TypeError:
                return False

            im = device.screencap()
            image = cv2.imdecode(np.frombuffer(im, np.uint8), cv2.IMREAD_COLOR)

            # cv2.imshow("", image)
            # cv2.waitKey(0)

            image = image[0:image.shape[0], 0: int(image.shape[1] * .5)]

            height = image.shape[0]
            width = int(image.shape[1] / height * 320)
            height = 320

            dsize = (width, height)
            output = cv2.resize(image, dsize)

            cv2.imwrite(FOUT.name, output)

            return FOUT.name

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
            print(1)
            screen_shots_cache[device_serial][size]['file_id'] = gen_image()
            print(2)
        except RuntimeError:
            return False
    return True


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


@check_adb_running
@app.get("/device-screen/{refresh_ms}/{size}/{device_serial}")
async def devicescreen(request: Request, refresh_ms: int, size: str, device_serial: str):
    success = check_image(device_serial, refresh_ms, size)

    if not success:
        return templates.TemplateResponse("htmx/device.html", {"request": request,
                                                               "device_serial": device_serial,
                                                               'err': 'lost connection'})
    image = screen_shots_cache[device_serial][size]['file_id']
    err = None
    try:
        with open(image, "rb") as img_file:
            base64_image = base64.b64encode(img_file.read()).decode('utf-8')

    except TypeError:
        base64_image = None
        err = 'issue'

    return templates.TemplateResponse("htmx/device.html", {"request": request,
                                                           "device_serial": device_serial,
                                                           'base64_image': base64_image,
                                                           'err': err})


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


