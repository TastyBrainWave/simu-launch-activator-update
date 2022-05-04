status_global = document.getElementById("status");
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
    fetch('/load', {
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
        status_global.innerHTML = "Experience has loaded on " + data["device_count"] + " devices!";
        document.getElementById("loadButton").classList.remove("disabled");
    }).catch(function (error) {
        status_global.classList.add("alert-danger");
        status_global.innerHTML = "Error loading experience: " + error;
        document.getElementById("loadButton").classList.remove("disabled");
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
        status_global.innerHTML = "Experience has stopped on all decives!";
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
        method: 'GET',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
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