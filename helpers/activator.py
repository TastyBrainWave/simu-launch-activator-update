import requests
import os

ip_address = os.popen("adb shell ip route").read()
print(ip_address)
ip_address = ip_address.split(" ")[8]
print(ip_address)

os.system("adb tcpip 5555")

payload = {
	'remote_address': ip_address
}

success = False

response = requests.post("http://192.168.1.100:8000/connect", data=payload)
print(response)
success = response.json()["success"]
	
print("Finished")



