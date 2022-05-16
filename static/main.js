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

// doing via object for reasons of clarity
// params = {
//  url: '',
//  method: default POST
//  body: '',
//  success: '',
//  problem: '',
//  start: '',
//  finally: '',
// }

function add_devices(obj) {
    if (!obj['devices']) obj['devices'] = ['a', 'b'];
}

function send(params) {
    if (!params['headers']) params['headers'] = {};
    params['headers']["Content-type"] = "application/json";
    if (!params['method']) params['method'] = 'POST';

    // inject universal info such as devices
    if (!params['body']) params['body'] = {}
    add_devices(params['body']);
    // console.log(111, params)


    if (params['start']) params['start']();

    fetch(params['url'], {
        method: params['method'],
        body: JSON.stringify(params['body']),
        headers: params['headers']
    }).then(function (response) {
        if (!response.ok) {
            throw Error(response.statusText);
        }
        if (params['success']) params['success'](response);
    }).catch(function (error) {
        if (params['problem']) params['problem'](error);
        else {
            console.log(error);
        }
    }).finally(function () {
        if (params['finally']) params['finally']();
    });
}

showStatus = (text = "The showStatus function was used incoorrectly and status text was not defined", isError = false) => {
    if (isError === true) {
        document.getElementById("statusToast").classList.add("bg-danger");
        document.getElementById("toastClose").classList.add("btn-close-white");
        status_global.classList.add("text-white");
    } else if (document.getElementById("statusToast").classList.contains("bg-danger")) {
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
    })
}

function remove_class(element) {
    var lastClass = element.attr('class').split(' ').pop();
    if (lastClass.includes("alert-")) {
        element.removeClass(lastClass)
    }
}

//BUTTON EVENTS
function startExperience() {

    send({
        start: function () {
            document.getElementById("startButton").classList.add("disabled");
        },
        body: {},
        url: '/start',
        success: function (data) {
            showStatus("Experience has started on " + data["device_count"] + " devices!");
        },
        problem: function (error) {
            showStatus("Error starting experience: " + error);
        },
        finally: function () {
            document.getElementById("startButton").classList.remove("disabled");
        }
    })


}

function loadExperience() {

    var experience = document.getElementById("load_choices_dropdown").value;


    send({
        url: '/load',
        start: function () {
            document.getElementById("loadButton").classList.add("disabled");
        },
        body: {
            'experience': experience
        },
        success: function (data) {
            $('#loadModal').modal('hide');
            selected_experience_global.innerHTML = "The following experience is currently selected: " + experience
            showStatus("Experience has loaded on " + data.json()["device_count"] + " devices!");

        },
        problem: function (error) {
            showStatus("Error loading experience: " + error);

        },
        finally: function () {
            document.getElementById("loadButton").classList.remove("disabled");
        }
    })
}

function setRemoteExperience() {

    var experience = document.getElementById("set_choices_dropdown").value;

    send({
        url: '/set-remote-experience',
        start: function () {
            document.getElementById("setRemoteButton").classList.add("disabled");
        },
        body: {
            'experience': experience
        },
        success: function (data) {
            $('#setExperienceModal').modal('hide');
            selected_experience_global.innerHTML = "The following experience is currently selected: " + experience
            showStatus("Experience has been set! You may now start it!");

        },
        problem: function (error) {
            showStatus("Error setting experience: " + error);

        },
        finally: function () {
            document.getElementById("setRemoteButton").classList.remove("disabled");
        }
    })
}

// function addRemoteExperience() {
//
//     const formElement = document.getElementById('addExperienceForm')
//     var formData = new FormData(formElement)
//
//     send({
//         url: '/add-remote-experience',
//         start: function () {
//             document.getElementById("addRemoteButton").classList.add("disabled");
//         },
//         body: formData,
//         success: function () {
//             $('#addExperienceModal').modal('hide');
//             showStatus("Experience has been added! You may now set it as the active experience");
//         },
//         finally: function () {
//             document.getElementById("addRemoteButton").classList.remove("disabled");
//         }
//     })
//
// }

function removeRemoteExperience() {

    var experience = document.getElementById("remove_choices_dropdown").value;


    send({
        url: '/remove-remote-experience',
        start: function () {
            document.getElementById("removeRemoteButton").classList.add("disabled");
        },
        body: {
            'experience': experience
        },
        success: function () {
            $('#removeExperienceModal').modal('hide');
            showStatus("Experience " + experience + " has been removed!");
        },
        finally: function () {
            document.getElementById("removeRemoteButton").classList.remove("disabled");
        }
    })

}


function stopExperience() {

    send({
        url: '/stop',
        start: function () {
            document.getElementById("stopButton").classList.add("disabled");
        },
        success: function () {
            showStatus("Experience has stopped on all devices!");
        },
        finally: function () {
            document.getElementById("stopButton").classList.remove("disabled");
        }
    })
}

function connectDevice() {


    send({
        url: '/connect',
        start: function () {
            document.getElementById("connectButton").classList.add("disabled");
        },
        headers: {
            "Content-type": "application/json"
        },
        success: function (data) {
            showStatus("Device connected with serial ID: " + data.json()["serial"]);

        },
        problem: function (error) {
            showStatus("Error connecting device: " + error, true);
        },
        finally: function () {
            document.getElementById("connectButton").classList.remove("disabled");
        }
    })
}

function disconnectDevice() {

    send({
        url: '/disconnect',
        headers: {
            "Content-type": "application/json"
        },

        start: function () {
            document.getElementById("disconnectButton").classList.add("disabled");
        },
        success: function () {
            showStatus("All devices have been disconnected");
        },
        problem: function (error) {
            showStatus("Error disconnecting devices: " + error);
        },
        finally: function () {
            document.getElementById("disconnectButton").classList.remove("disabled");
        }
    })
}

function stopServer() {

    send({
        url: '/exit-server',
        start: function () {
            document.getElementById("stopServerButton").classList.add("disabled");
        },
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        success: function () {
            showStatus("ADB server has stopped!");
        },
        problem: function (error) {
            showStatus("Error stopping server: " + error);
        },
        finally: function () {
            document.getElementById("stopServerButton").classList.remove("disabled");
        }
    })
}

function getScreenshots() {

    send({
        url: '/screen-grab',
        start: function () {
            document.getElementById("screenshotButton").classList.add("disabled");
        },
        method: 'GET',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        success: function () {
            showStatus("Screenshots have taken!");
            document.getElementById("screenshotButton").classList.remove("disabled");
        },
        problem: function (error) {
            showStatus("Error taking screenshots: " + error);
        },
        finally: function () {
            document.getElementById("screenshotButton").classList.remove("disabled");
        }
    })
}

//DEVICE CARDS
class DeviceCard extends HTMLElement {
    constructor(image, deviceId, selected) {
        super();
        this.attachShadow({mode: 'open'});
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


window.addEventListener('load', function () {

    var slider = $('#volume');

    slider.on('change', function (ev) {
        var volume = parseInt(slider.val());

        send({
            url: 'volume',
            body: {'volume': volume},
            success: function () {
                console.log('changed volume to ' + volume);
            },
            problem: function () {
                console.log('could not change volume to ' + volume);
            },
            finally: '',
        });

    });

})
