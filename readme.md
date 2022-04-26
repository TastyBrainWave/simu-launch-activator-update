#Simu-Launch

## Install

To run this, you need to install all the dependencies in requirements.txt as follows:

`pip install -r requirements.txt`

Then, run the uvicorn command, which keeps the server running and refreshes it every time there is a change:

`uvicorn main:app --reload`

Note in PyCharm you can set up a configuration to manage the dev server. See https://stackoverflow.com/a/66787462/960471
![image](https://user-images.githubusercontent.com/595166/165240365-b7459e8c-eeca-41f8-8eb1-c835b5e77b64.png)


From then, it all should be working on the interface at http://127.0.0.1:8000/
