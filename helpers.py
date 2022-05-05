import os

def check_adb_running(client):
    try:
        devices = client.devices()

    except RuntimeError as e:
        if e.__str__().find("Is adb running on your computer?"):
            print("ADB Server not running, starting it now!")
            command = os.system("adb start-server")
            print(command)


def launch_app(device, app_name, d_type: bool = False):
    """
      Launches an app on the specified device based on the device type and application name
      :param device: the Device object for ppadb
      :param app_name: the application name, ie: com.simu-launch.calculator
      :param d_type: the device type, True = Quest, False = Android
      """

    if ".apk" in app_name:
        app_name = app_name[:-4]

    command = "am start -n" + app_name + "/" + app_name + ".UnityPlayerActivity" if d_type else "monkey -p " + app_name \
                                                                                                + " -v 1"
    print(command)

    device.shell(command)

def save_file(filename, data):

    delete_old = "apks/" + os.listdir("apks")[0]
    os.remove(delete_old)

    with open("apks/" + filename, 'wb') as f:
        f.write(data)

