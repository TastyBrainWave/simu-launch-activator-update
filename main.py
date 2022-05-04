import datetime
import os
from functools import partial
from helpers import launch_app, save_file, check_adb_running
from multiprocessing import Process, Pool, cpu_count

from fastapi import FastAPI, UploadFile, File, Form
from ppadb import InstallError
from starlette.requests import Request
from starlette.responses import StreamingResponse, FileResponse, RedirectResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
import tempfile
from ppadb.client import Client as AdbClient

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# Have some global variables to set app to run, devices, adb stuff etc.

simu_application_name = ""
device_type = False # False for Android, True for Quest

client = AdbClient(host="127.0.0.1", port=5037)


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

    check_adb_running(client)

    client_list = client.devices()

    global simu_application_name
    global device_type

    try:
        pool = Pool(cpu_count())
        launch_func = partial(launch_app, app_name=simu_application_name, d_type=device_type)
        results = pool.map(launch_func, client_list)
        pool.close()
        pool.join()
    except RuntimeError as e:
        return {"success": False, "error": e.__str__()}

    return {"success": True, "device_count": len(client_list)}



@app.post("/upload")
async def upload(file: UploadFile = File(...), device: str = Form(...)):
    try:
        contents = await file.read()
        save_file(file.filename, contents)

        global simu_application_name
        simu_application_name = file.filename

        global device_type
        device_type = True if device == "quest" else False

        print(device_type, simu_application_name)

        return {"success": True}
    except IOError as e:
        return {"success": False, "error": e.__str__()}

@app.get("/load")
async def load(request: Request):
    """
        Installs the experience on all devices

    :param request: the Request parameter
    :return: a success dictionary signifying the operation was successful
    """

    check_adb_running(client)
    client_list = client.devices()

    apk_path = "apks/" + os.listdir("apks")[0]

    print(apk_path)

    apk_name = apk_path[4:]
    apk_name = apk_name[:4]

    try:
        for device in client_list:
            print("Installing " + apk_path + " on " + device.serial)
            p = Process(target=device.install, args=(apk_path,))
            p.start()
    except InstallError as e:
        return {"success": False, "error": e.__str__()}

    return {"success": True, "device_count": len(client_list)}

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

    check_adb_running(client)

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


