
//GLOBAL VARS
var status_global = document.getElementById("status");
var statusToast = new bootstrap.Toast(document.getElementById('statusToast'));
var selected_experience_global = document.getElementById("experience");

//HELPER FUNCTIONS
function transformFormData() {
    var myForm = document.getElementById('myForm');
    var qs = new URLSearchParams(new FormData(myForm)).toString();
    myForm.action = 'http://127.0.0.1:8000/submit?' + qs;
}
showStatus = (text = "The showStatus function was used incoorrectly and status text was not defined", isError = false) => {
    if (isError === true) {
        document.getElementById("statusToast").classList.add("bg-danger");
        document.getElementById("toastClose").classList.add("btn-close-white");
        status_global.classList.add("text-white");
    }
    else if (document.getElementById("statusToast").classList.contains("bg-danger")) {
        document.getElementById("statusToast").classList.remove("bg-danger");
        document.getElementById("toastClose").classList.remove("btn-close-white");
        status_global.classList.remove("text-white");
    }
    status_global.innerHTML = text;
    statusToast.show();
}
function uploadAPKForm() {
    const formElement = document.getElementById('uploadForm')
    var formData = new FormData(formElement)

    fetch('/upload', {
        method: 'POST',
        body: formData
    }).then(function (response) {
        if (!response.ok) {
            throw Error(response.statusText);
        }

        $('#uploadModal').modal('hide')

        return response.json();
    }).then(function (data) {
        showStatus("Experience has been uploaded. You may now load it on devices");
    }).catch(function (error) {
        console.log(error);
        showStatus("Error uploading experience to server: " + error);

    });
}
function remove_class(element) {
    var lastClass = element.attr('class').split(' ').pop();
    if (lastClass.includes("alert-")) {
        element.removeClass(lastClass)
    }
}

//BUTTON EVENTS
function startExperience() {
    document.getElementById("startButton").classList.add("disabled");

    var formData = new FormData()
    var devices = []
    devices.push(connected_devices[0])
    formData.append("devices", devices.toString())

    fetch('/start', {
        method: 'POST',

    }).then(function (response) {
        if (!response.ok) {
            throw Error(response.statusText);
        }
        return response.json();
    }).then(function (data) {
        showStatus("Experience has started on " + data["device_count"] + " devices!");
        document.getElementById("startButton").classList.remove("disabled");
    }).catch(function (error) {
        showStatus("Error starting experience: " + error);
        document.getElementById("startButton").classList.remove("disabled");
    });
}

function loadExperience() {
    document.getElementById("loadButton").classList.add("disabled");

    const formElement = document.getElementById('loadForm')
    var formData = new FormData(formElement)
    formData.append("devices", "[]")

    fetch('/load', {
        method: 'POST',
        body: formData
    }).then(function (response) {
        if (!response.ok) {
            throw Error(response.statusText);
        }

        $('#loadModal').modal('hide');

        return response.json();
    }).then(function (data) {
        selected_experience_global.innerHTML = "The following experience is currently selected: " + formData.get("load_choices")
        showStatus("Experience has loaded on " + data["device_count"] + " devices!");
        document.getElementById("loadButton").classList.remove("disabled");
    }).catch(function (error) {

        showStatus("Error loading experience: " + error);
        document.getElementById("loadButton").classList.remove("disabled");
    });
}

function setRemoteExperience() {
    document.getElementById("setRemoteButton").classList.add("disabled");

    const formElement = document.getElementById('setRemoteExperienceForm')
    var formData = new FormData(formElement)

    fetch('/set-remote-experience', {
        method: 'POST',
        body: formData
    }).then(function (response) {
        if (!response.ok) {
            throw Error(response.statusText);
        }

        $('#setExperienceModal').modal('hide');

        return response.json();
    }).then(function (data) {
        selected_experience_global.innerHTML = "The following experience is currently selected: " + formData.get("set_choices")


        showStatus("Experience has been set! You may now start it!");
        document.getElementById("setRemoteButton").classList.remove("disabled");
    }).catch(function (error) {

        showStatus("Error setting experience: " + error);
        document.getElementById("setRemoteButton").classList.remove("disabled");
    });
}

function addRemoteExperience() {
    document.getElementById("addRemoteButton").classList.add("disabled");

    const formElement = document.getElementById('addExperienceForm')
    var formData = new FormData(formElement)

    fetch('/add-remote-experience', {
        method: 'POST',
        body: formData
    }).then(function (response) {
        if (!response.ok) {
            throw Error(response.statusText);
        }

        $('#addExperienceModal').modal('hide');

        return response.json();
    }).then(function (data) {


        showStatus("Experience has been added! You may now set it as the active experience");
        document.getElementById("addRemoteButton").classList.remove("disabled");
    }).catch(function (error) {

        showStatus("Error adding experience: " + error);
        document.getElementById("addRemoteButton").classList.remove("disabled");
    });
}


function stopExperience() {
    document.getElementById("stopButton").classList.add("disabled");
    fetch('/stop', {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    }).then(function (response) {
        if (!response.ok) {
            throw Error(response.statusText);
        }
        return response.json();
    }).then(function (data) {

        showStatus("Experience has stopped on all devices!");
        document.getElementById("stopButton").classList.remove("disabled");
    }).catch(function (error) {

        showStatus("Error stopping experience: " + error);
        document.getElementById("stopButton").classList.remove("disabled");
    });
}
function connectDevice() {
    document.getElementById("connectButton").classList.add("disabled");
    fetch('/connect', {
        method: 'POST',
        headers: {
            "Content-type": "application/json"
        },
    }).then(function (response) {
        if (!response.ok) {
            throw Error(response.error);
        }
        return response.json();
    }).then(function (data) {

        showStatus("Device connected with serial ID: " + data["serial"]);
        document.getElementById("connectButton").classList.remove("disabled");
    }).catch(function (error) {

        showStatus("Error connecting device: " + error, true);
        document.getElementById("connectButton").classList.remove("disabled");
    });
}
function disconnectDevice() {
    document.getElementById("disconnectButton").classList.add("disabled");
    fetch('/disconnect', {
        method: 'POST',
        headers: {
            "Content-type": "application/json"
        },
    }).then(function (response) {
        if (!response.ok) {
            throw Error(response.error);
        }
        return response.json();
    }).then(function (data) {

        showStatus("All devices have been disconnected");
        document.getElementById("disconnectButton").classList.remove("disabled");
    }).catch(function (error) {

        showStatus("Error disconnecting devices: " + error);
        document.getElementById("disconnectButton").classList.remove("disabled");
    });
}
function stopServer() {
    document.getElementById("stopServerButton").classList.add("disabled");
    fetch('/exit-server', {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    }).then(function (response) {
        if (!response.ok) {
            throw Error(response.statusText);
        }
        return response.json();
    }).then(function (data) {

        showStatus("ADB server has stopped!");
        document.getElementById("stopServerButton").classList.remove("disabled");
    }).catch(function (error) {

        showStatus("Error stopping server: " + error);
        document.getElementById("stopServerButton").classList.remove("disabled");
    });
}
function getScreenshots() {
    document.getElementById("screenshotButton").classList.add("disabled");
    fetch('/screen-grab', {
        method: 'GET',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    }).then(function (response) {
        if (!response.ok) {
            throw Error(response.statusText);
        }
        return response.json();
    }).then(function (data) {

        showStatus("Screenshots have taken!");
        document.getElementById("screenshotButton").classList.remove("disabled");
    }).catch(function (error) {

        showStatus("Error taking screenshots: " + error);
        document.getElementById("screenshotButton").classList.remove("disabled");
    });
}
//DEVICE CARDS
class DeviceCard extends HTMLElement {
    constructor(image, deviceId, selected) {
        super();
        this.attachShadow({ mode: 'open' });
        var bootstrapStyles = document.createElement('link')
        bootstrapStyles.rel = 'stylesheet'
        bootstrapStyles.href = 'static/bootstrap-5.0.2-dist/css/bootstrap.css'
        this.shadowRoot.appendChild(bootstrapStyles);
        this.shadowRoot.appendChild(document.querySelector("#device-card").content.cloneNode(true));
        this.image = image;
        this.deviceId = deviceId;
        this.selected = selected;
        var checkbox = this.shadowRoot.getElementById("cardSelect");
        checkbox.addEventListener('change', () => {
            if (checkbox.checked) {
                this.selected = true;
                this.shadowRoot.getElementById("main-card").classList.add("shadow");
            } else {
                this.selected = false;
                this.shadowRoot.getElementById("main-card").classList.remove("shadow");
            }

        })

    }
    updateImage(image) {
        this.image = image;
        this.shadowRoot.querySelector("img").src = image;
    }
    connectedCallback() {
        this.shadowRoot.querySelector("img").src = this.image;
        this.shadowRoot.querySelector("#device-name").innerHTML = this.deviceId;

    }
}
window.customElements.define('device-card', DeviceCard);

testingarr = ["42345325", "654645", "65476", "746535", "23432432", "12315465"]
var cardList = []
connected_devices.forEach((device) => {
    //var card = document.querySelector("#device-card").content.cloneNode(true);
    //card.querySelector("#device-name").textContent = device;
    //console.log(card);
    //document.querySelector("#main-container").appendChild(card);
    var card = new DeviceCard("https://picsum.photos/200", device, false);
    document.querySelector("#main-container").appendChild(card);
    cardList.push(card);
});