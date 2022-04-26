import datetime
import os
from hashlib import sha256
from multiprocessing import Process

from fastapi import FastAPI
from ppadb import InstallError
from starlette.requests import Request
from starlette.templating import Jinja2Templates
from ppadb.client import Client as AdbClient

app = FastAPI()

templates = Jinja2Templates("templates")

# Have some global variables to set app to run, devices, adb stuff etc.

global started_state

client = AdbClient(host="127.0.0.1", port=5037)

def check_adb_running():
    try:
        devices = client.devices()
    except RuntimeError as e:
        if e.__str__().find("Is adb running on your computer?"):
            print("ADB Server not running, starting it now!")
            command = os.system("adb start-server")
            print(command)

@app.get("/")
async def home(request: Request):
    """
        View mainly responsible for handling the front end, since nothing will happen on the backend at this endpoint.
    :param request: the Request() object
    :return: a TemplateResponse object containing the homepage
    """
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/start")
async def start(request: Request):
    """
        Starts the experience on all devices through the adb shell commands.

    :param request: The Request parameter
    :return: dictionary of all device serial numbers
    """

    check_adb_running()

    client_list = client.devices()

    vr_app_name = "com.alturgames.BendingOaksVR/com.unity3d.player.UnityPlayerActivity"
    android_app_name = "com.amazon.calculator"

    try:
        for device in client_list:
            android_command = "monkey -p" + android_app_name + " -v 1"
            vr_command = "am start -n" + vr_app_name
            p = Process(target=device.shell, args=(android_command,))
            p.start()
            # device.shell("monkey -p" + app_name + " -v 1")
            # device.shell("am start -n" + "calculator")
    except RuntimeError as e:
        return {"success": False, "error": e.__str__()}

    return {"success": True}

@app.get("/load")
async def load(request: Request):
    """
        Installs the experience on all devices

    :param request: the Request parameter
    :return: a success dictionary signifying the operation was successful
    """

    check_adb_running()
    client_list = client.devices()

    apk_path = "apks/bendingoaks.apk"

    apk_name = apk_path[4:]
    apk_name = apk_name[:4]

    try:
        for device in client_list:
            device.install(apk_path)
    except InstallError as e:
        return {"success": False, "error": e.__str__()}

    return {"success": True, "loaded_app": apk_name}

@app.get("/stop")
async def stop(request: Request):
    """
        Stops the experience on all devices through ADB shell commands

    :param request: The Request parameter
    :return: a dictionary containing the success flag of the operation and any errors
    """

    client_list = client.devices()

    app_name = "com.amazon.calculator"

    try:
        for device in client_list:
            print(device.serial)
            command = "am force-stop " + app_name
            print(command)
            device.shell(command)
    except RuntimeError as e:
        return {"success": False, "error": e.__str__()}

    return {"success": True, "stopped_app": app_name}

BASE_PORT = 5555

@app.get("/connect")
async def connect(request: Request):
    """
        Connects a device wirelessly to the server on port 5555. After the device is connected, it can be unplugged from
        the USB.

    :param request: The Request parameter
    :return: a dictionary containing the success flag of the operation and any errors
    """

    global BASE_PORT

    check_adb_running()

    devices = client.devices()

    device_ip = devices[0].shell("ip addr show wlan0")

    device_ip = device_ip[device_ip.find("inet "):]

    device_ip = device_ip[:device_ip.find("/")]

    device_ip = device_ip[device_ip.find(" ")+1:]

    try:
        os.system("adb -s" + devices[0].serial + " tcpip " + str(BASE_PORT))
        working = client.remote_connect(device_ip, port=BASE_PORT)

        if working:
            print("Established connection with client " + device_ip + ":" + str(BASE_PORT))

            return {"success": True}

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

    check_adb_running()

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

