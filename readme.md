#Simu-Launch

## Install

To run this, you need to install all the dependencies in requirements.txt as follows:

`pip install -r requirements.txt`

Then, run the uvicorn command, which keeps the server running and refreshes it every time there is a change:

`uvicorn main:app --reload`

From then, it all should be working on the interface at http://127.0.0.1:8000/