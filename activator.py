import requests
import os
import time
import datetime
import RPi.GPIO as GPIO

high = GPIO.HIGH
low = GPIO.LOW

# Pins based on BCM pinout as opposed to Pi pinout - https://pinout.xyz/
button = 4
os_loaded = 27
connect_attempt = 10
connect_success = 0
connect_fail = 6
battery_low = 26

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(button, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

GPIO.setup(os_loaded, GPIO.OUT, initial = high) # If the Pi is operational and this script is running, illuminates 'os_ready' LED
GPIO.setup(connect_attempt, GPIO.OUT, initial = low)
GPIO.setup(connect_success, GPIO.OUT, initial = low)
GPIO.setup(connect_fail, GPIO.OUT, initial = low)
GPIO.setup(battery_low, GPIO.OUT, initial = low)

standby = true
battery_check_count = 0

while True:
    GPIO.output(connect_success, low)
    GPIO.output(connect_fail, low)

    while standby == True:
        if GPIO.input(button) == high:
            standby = False
            while GPIO.input(button) == GPIO.HIGH:  # In the event the user holds down the button, stops the Pi from flicking standby true/false repeatedly
                time.sleep(0.01)                    # This should help to debounce the switch, can also be done in hardware though
            break
        if ((int(time.thread_time()) % 60) == 0) and not second_skip: 
            battery_check = os.popen("dmesg | grep -i 'under-voltage detected'").read()
            second_skip = true
        if battery_check is None:
            continue
        else:
            GPIO.output(battery_low, high)

        if second_skip and ((int(time.thread_time()) % 60) != 0):
            second_skip = false


    if (GPIO.input(button) == high) and standby == False:
        standby = True
        while GPIO.input(button) == high:
            time.sleep(0.01)


    time_only = datetime.datetime.now().strftime("%H:%M:%S")
    ip_address = os.popen("adb shell ip route").read()
    print(f"{time_only} { ip_address}")
    if ip_address:
        GPIO.output(connect_attempt, high)
        ip_address = ip_address.split(" ")[8]
        print(ip_address)

        os.system("adb tcpip 5555")

        payload = {
            'remote_address': ip_address
        }
        print('restarting in tcpip mode... waiting 3 seconds')
        time.sleep(3)
        print('letting storystarter know about Quest...')
        outcome = os.popen("""adb shell "printf 'GET /connect HTTP/1.1\r\n http://192.168.0.155 \r\n\r\n' | nc 192.168.0.155 8000""").read()
        print(outcome, 222)

        print("Finished")
        GPIO.output(connect_attempt, low)
        GPIO.output(connect_success, high)

    elif ip_address is None:
        GPIO.output(connect_fail, high)

    battery_check_count += 1
    time.sleep(5)

    if count == 15:
        battery_check = os.popen("dmesg | grep -i 'under-voltage detected'").read()
        if battery_check is None:
            continue
        else:
            GPIO.output(battery_low, high)
        battery_check_count = 0