#Simu-Launch

## Install

To run this, you need to install all the dependencies in requirements.txt as follows:

`pip install -r requirements.txt`

Note in PyCharm you can set up a configuration to manage the dev server. See https://stackoverflow.com/a/66787462/960471
![image](https://user-images.githubusercontent.com/595166/165240365-b7459e8c-eeca-41f8-8eb1-c835b5e77b64.png)


## local dev
Run the uvicorn command, which keeps the server running and refreshes it every time there is a change:

`uvicorn main:app --reload`

From then, it all should be working on the interface at http://127.0.0.1:8000/


## Production (raspberry pi)
On a raspberry pi, to allow other devices besides the pi accessing the server, run the below. Note that the host 0.0.0.0 allows the server to be accessible to other devices

`uvicorn main:app --reload --port 8000 -- host "0.0.0.0"`


Find out the ip address of the raspberry pi, perhaps via this command:

`ifconfig wlan0 | grep inet | awk '{ print $2 }'`

To access the server from other devices, just enter this ip address into your browser