function transformFormData(){
            var myForm = document.getElementById('myForm');
            var qs = new URLSearchParams(new FormData(myForm)).toString();
            myForm.action = 'http://127.0.0.1:8000/submit?'+qs;
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
        status_global.classList.add("alert-success");
        status_global.innerHTML = "Experience has been uploaded. You may now load it on devices";
    }).catch(function (error) {
        status_global.classList.add("alert-danger");
        console.log(error);
        status_global.innerHTML = "Error uploading experience to server: " + error;
    });
}

status_global = document.getElementById("status");
selected_experience_global = document.getElementById("experience");
function remove_class(element) {
    var lastClass = element.attr('class').split(' ').pop();
    if (lastClass.includes("alert-")) {
        element.removeClass(lastClass)
    }
}
function startExperience() {
    document.getElementById("startButton").classList.add("disabled");
    fetch('/start', {
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
        status_global.classList.add("alert-success");
        status_global.innerHTML = "Experience has started on " + data["device_count"] + " devices!";
        document.getElementById("startButton").classList.remove("disabled");
    }).catch(function (error) {
        status_global.classList.add("alert-danger");
        status_global.innerHTML = "Error starting experience: " + error;
        document.getElementById("startButton").classList.remove("disabled");
    });
}

function loadExperience() {
    document.getElementById("loadButton").classList.add("disabled");

    const formElement = document.getElementById('loadForm')
    var formData = new FormData(formElement)

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

        status_global.classList.add("alert-success");
        status_global.innerHTML = "Experience has loaded on " + data["device_count"] + " devices!";
        document.getElementById("loadButton").classList.remove("disabled");
    }).catch(function (error) {
        status_global.classList.add("alert-danger");
        status_global.innerHTML = "Error loading experience: " + error;
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

        status_global.classList.add("alert-success");
        status_global.innerHTML = "Experience has been set! You may now start it!";
        document.getElementById("setRemoteButton").classList.remove("disabled");
    }).catch(function (error) {
        status_global.classList.add("alert-danger");
        status_global.innerHTML = "Error setting experience: " + error;
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

        status_global.classList.add("alert-success");
        status_global.innerHTML = "Experience has been added! You may now set it as the active experience";
        document.getElementById("addRemoteButton").classList.remove("disabled");
    }).catch(function (error) {
        status_global.classList.add("alert-danger");
        status_global.innerHTML = "Error adding experience: " + error;
        document.getElementById("addRemoteButton").classList.remove("disabled");
    });
}


function stopExperience() {
    document.getElementById("stopButton").classList.add("disabled");
    fetch('/stop', {
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
        status_global.classList.add("alert-success");
        status_global.innerHTML = "Experience has stopped on all devices!";
        document.getElementById("stopButton").classList.remove("disabled");
    }).catch(function (error) {
        status_global.classList.add("alert-danger");
        status_global.innerHTML = "Error stopping experience: " + error;
        document.getElementById("stopButton").classList.remove("disabled");
    });
}
function connectDevice() {
    document.getElementById("connectButton").classList.add("disabled");
    fetch('/connect', {
        method: 'POST',
    }).then(function (response) {
        if (!response.ok) {
            throw Error(response.error);
        }
        return response.json();
    }).then(function (data) {
        status_global.classList.add("alert-success");
        status_global.innerHTML = "Device connected with serial ID: " + data["serial"];
        document.getElementById("connectButton").classList.remove("disabled");
    }).catch(function (error) {
        status_global.classList.add("alert-danger");
        status_global.innerHTML = "Error connecting device: " + error;
        document.getElementById("connectButton").classList.remove("disabled");
    });
}
function stopServer() {
    document.getElementById("stopServerButton").classList.add("disabled");
    fetch('/exit-server', {
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
        status_global.classList.add("alert-success");
        status_global.innerHTML = "ADB server has stopped!";
        document.getElementById("stopServerButton").classList.remove("disabled");
    }).catch(function (error) {
        status_global.classList.add("alert-danger");
        status_global.innerHTML = "Error stopping server: " + error;
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
        status_global.classList.add("alert-success");
        status_global.innerHTML = "Screenshots have taken!";
        document.getElementById("screenshotButton").classList.remove("disabled");
    }).catch(function (error) {
        status_global.classList.add("alert-danger");
        status_global.innerHTML = "Error taking screenshots: " + error;
        document.getElementById("screenshotButton").classList.remove("disabled");
    });
}