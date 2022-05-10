import datetime
import os
from functools import partial

import sqlalchemy
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from helpers import launch_app, save_file, check_adb_running
from multiprocessing import Process, Pool, cpu_count
from typing import List

from fastapi import FastAPI, UploadFile, File, Depends
from fastapi import FastAPI, UploadFile, File, Form
from ppadb import InstallError
from starlette.requests import Request
from starlette.responses import StreamingResponse, FileResponse, RedirectResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
import tempfile
from ppadb.client import Client as AdbClient

from sql_app import models, schemas, crud
from sql_app.crud import get_all_apk_details
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

    print(simu_application_name)

    return templates.TemplateResponse("home.html",
                                      {
                                          "request": request,
                                          "choices": [item.apk_name for item in uploaded_experiences],
                                          "app_name": simu_application_name
                                      }
                                      )


@app.get("/start")
async def start(request: Request, db: Session = Depends(get_db)):
    """
        Starts the experience on all devices through the adb shell commands.

    :param db: the database dependency
    :param request: The Request parameter
    :return: dictionary of all device serial numbers
    """

    check_adb_running(client)

    client_list = client.devices()

    global simu_application_name

    item = jsonable_encoder(crud.get_apk_details(db, apk_name=simu_application_name))

    print(item)

    try:
        pool = Pool(cpu_count())
        launch_func = partial(launch_app, app_name=item["apk_name"], d_type=item["device_type"], command=item["command"])
        results = pool.map(launch_func, client_list)
        pool.close()
        pool.join()
    except RuntimeError as e:
        return {"success": False, "error": e.__str__()}

    return {"success": True, "device_count": len(client_list)}


@app.post("/upload")
async def upload(file: UploadFile = File(...), command: str = Form(...), db: Session = Depends(get_db)):

    try:
        contents = await file.read()
        save_file(file.filename, contents)

        global simu_application_name
        simu_application_name = file.filename

        device_type = 0 if command == "android" else 1

        item = APKDetailsBase(apk_name=file.filename, command="" if command == "android" else command, device_type=device_type)

        crud.create_apk_details_item(db=db, item=APKDetailsCreate.parse_obj(item.dict()))

        return {"success": True}
    except IOError as e:
        return {"success": False, "error": e.__str__()}

@app.post("/load")
async def load(load_choices: str = Form(...), db: Session = Depends(get_db)):
    """
        Installs the experience on all devices

    :param load_choices: the choice of experience specified by the user
    :param db: the DB session
    :param request: the Request parameter
    :return: a success dictionary signifying the operation was successful
    """

    check_adb_running(client)
    client_list = client.devices()

    apk_paths = os.listdir("apks")
    apk_path = "apks/"

    item = load_choices

    global simu_application_name
    simu_application_name = item

    print(item, simu_application_name)

    if item in apk_paths:
        apk_path += item
    else:
        return {"success": False, "error": "Cannot find the Experience APK in the directory. Make sure you uploaded it!"}

    try:
        for device in client_list:
            print("Installing " + apk_path + " on " + device.serial)
            p = Process(target=device.install, args=(apk_path,))
            p.start()
    except InstallError as e:
        return {"success": False, "error": e.__str__()}

    return {"success": True, "device_count": len(client_list)}

@app.post("/set-remote-experience")
async def set_remote_experience(set_choices: str = Form(...)):
    if set_choices:
        global simu_application_name
        simu_application_name = set_choices

        return {"success": True}

    return {"success": False}

@app.post("/add-remote-experience")
async def set_remote_experience(apk_name: str = Form(...), command: str = Form(...), db: Session = Depends(get_db)):
    try:
        device_type = 0 if command == "android" else 1

        item = APKDetailsBase(apk_name=apk_name, command="" if command == "android" else command,
                              device_type=device_type)

        crud.create_apk_details_item(db=db, item=APKDetailsCreate.parse_obj(item.dict()))

        return {"success": True}
    except SQLAlchemyError as e:
        return {"success": False, "error": e.__str__()}

@app.get("/stop")
async def stop(request: Request, db: Session = Depends(get_db)):
    """
        Stops the experience on all devices through ADB shell commands

    :param db:
    :param request: The Request parameter
    :return: a dictionary containing the success flag of the operation and any errors
    """

    client_list = client.devices()

    global simu_application_name

    item = jsonable_encoder(crud.get_apk_details(db, apk_name=simu_application_name))

    app_name = item["apk_name"] if not ".apk" in item["apk_name"] else item["apk_name"][:-4]

    try:
        for device in client_list:
            print(device.serial)
            command = "am force-stop " + app_name
            print(command)
            device.shell(command)
    except RuntimeError as e:
        return {"success": False, "error": e.__str__()}

    return {"success": True, "stopped_app": app_name}

@app.post("/connect")
async def connect(request: Request):
    """
        Connects a device wirelessly to the server on port 5555. After the device is connected, it can be unplugged from
        the USB.

    :param request: The Request parameter which is used to receive the device data.
    :return: a dictionary containing the success flag of the operation and any errors
    """

    global BASE_PORT

    check_adb_running(client)

    remote_address = request["remote_address"] if "remote_address" in request.keys() else ""

    devices = client.devices()

    if not remote_address:
        device_ip = devices[0].shell("ip addr show wlan0")
        device_ip = device_ip[device_ip.find("inet "):]
        device_ip = device_ip[:device_ip.find("/")]
        device_ip = device_ip[device_ip.find(" ")+1:]
    else:
        device_ip = remote_address

    try:
        os.system("adb -s" + devices[0].serial + " tcpip " + str(BASE_PORT))
        working = client.remote_connect(device_ip, port=BASE_PORT)

        if working:
            print("Established connection with client " + device_ip + ":" + str(BASE_PORT))

            return {"success": True, "serial": devices[0].serial}

        return {"success": False}
    except RuntimeError as e:
        return {"success": False, "error_log": e.__str__()}

@app.get("/exit-server")
async def exit_server(request: Request):
    """
        Kills the ADB server and all connections with devices. Essentially a system shutdown, where the FastAPI backend
        remains alive.
    :param request: the Request object
    :return: a dictionary containing the success flag
    """

    try:
        result = client.kill()
    except RuntimeError as e:
        return {"success": False, "errors": e.__str__()}

    return {"success": result}

@app.get("/screen-grab")
async def screen_grab(request: Request):
    """
        Gets a screenshot from every device.
    :param request: the Request object
    :return: a dictionary containing the success flag
    """

    check_adb_running(client)

    devices = client.devices()

    screen_caps_folder = "screenshots/"

    try:
        folder = screen_caps_folder + datetime.datetime.now().strftime("%m%d%Y%H%M%S") + "/"
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


@app.get("/screen/{device_serial}.png")
async def screen(request: Request, device_serial: str):
    im = my_devices[device_serial].screencap()

    with tempfile.NamedTemporaryFile(mode="w+b", suffix=".png", delete=False) as FOUT:
        FOUT.write(im)
        return FileResponse(FOUT.name, media_type="image/png")

my_devices = None

@app.get("/linkup")
async def linkup(request: Request):
    check_adb_running(client)
    global my_devices
    my_devices = {device.serial: device for device in client.devices()}
    return templates.TemplateResponse("htmx/devices.html", {"request": request, "devices": client.devices()})


