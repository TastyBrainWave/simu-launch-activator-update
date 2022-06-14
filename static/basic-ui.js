var current_devices = []
var masterList = ["app.lawnchair"]
class DeviceTable extends HTMLElement {
    constructor(deviceList) {
        super();
        this.deviceList = deviceList;
        this.attachShadow({ mode: 'open' });
        var bootstrapStyles = document.createElement('link')
        bootstrapStyles.rel = 'stylesheet'
        bootstrapStyles.href = 'static/bootstrap-5.2.0-beta1-dist/css/bootstrap.css'
        this.shadowRoot.appendChild(bootstrapStyles);
        this.tableGenerator(deviceList);
        this.classList.add("w-100");
        this.classList.add("p-0");


    }
    connectedCallback() {
    }
    tableGenerator(deviceList) {
        this.shadowRoot.appendChild(document.querySelector("#devices-table-template").content.cloneNode(true));
        var tableBody = this.shadowRoot.querySelector("#body-container");
        deviceList.forEach(device => {
            tableBody.appendChild(this.itemGenerator(device));
            this.getBatteryPercentage(device.id);
            this.getCurrentExperience(device.id);
        });
    }
    itemGenerator(device) {
        let row = document.querySelector("#device-list-item").content.cloneNode(true)
        row.querySelector("tr").setAttribute("id", device.id)
        if (device.icon) {

            var col = device.icon.col
            var icon = device.icon.icon


            $('.icon-set').each(function () {
                if ($(this).data('col') === col && $(this).data('icon') === icon) {
                    var found = $(this).parent().find('svg')
                    var cloned_icon = $(found).clone();
                    cloned_icon.css('color', col);

                    row.querySelector("#setIcon").innerHTML = cloned_icon[0].outerHTML;

                }
            });
        }
        if (device.ip === false) {
            row.querySelector("#deviceConnection").innerHTML = "Wired"
            row.querySelector("#deviceConnection").classList.remove("text-success")
            row.querySelector("#deviceConnection").classList.add("text-warning")
        }
        return row;
    }
    getBatteryPercentage(id) {

        fetch("/battery/" + id).then(response => {
            return response.json()
        }).then(data => {
            if (data >= 60) {
                this.shadowRoot.getElementById(id).querySelector("#batteryBadge").classList.add("text-bg-success")
                this.shadowRoot.getElementById(id).querySelector("#batteryBadge").classList.remove("text-bg-danger")
                this.shadowRoot.getElementById(id).querySelector("#batteryBadge").classList.remove("text-bg-warning")
            } else if (data < 60 && data >= 30) {
                this.shadowRoot.getElementById(id).querySelector("#batteryBadge").classList.add("text-bg-warning")
                this.shadowRoot.getElementById(id).querySelector("#batteryBadge").classList.remove("text-bg-success")
                this.shadowRoot.getElementById(id).querySelector("#batteryBadge").classList.remove("text-bg-danger")
            } else {
                this.shadowRoot.getElementById(id).querySelector("#batteryBadge").classList.add("text-bg-danger")
                this.shadowRoot.getElementById(id).querySelector("#batteryBadge").classList.remove("text-bg-success")
                this.shadowRoot.getElementById(id).querySelector("#batteryBadge").classList.remove("text-bg-warning")

            }
            this.shadowRoot.getElementById(id).querySelector("#batteryPercent").innerHTML = data + "%";

        })
    }
    getCurrentExperience(id) {
        fetch("/current-experience/" + id).then(response => {
            return response.json()
        }).then(data => {
            this.shadowRoot.getElementById(id).querySelector("#deviceCurrentExperience").innerHTML = data.current_app;

        })
    }
    checkLoadedExperiences(id) {
        fetch("/loaded-experiences/" + id).then(response => {
            return response.json()
        }).then(data => {
            //this.shadowRoot.getElementById(id).querySelector("#deviceLoadedExperiences").innerHTML = data.length;
            let package_list = []
            data.forEach(experience => {
                let expid = experience.package
                package_list.push(expid)
            })
            let includesall = masterList.every(element => package_list.indexOf(element) > -1);
            if (includesall) {
                this.shadowRoot.getElementById(id).querySelector("#deviceExperiencesStatus").classList.add("text-success")
                this.shadowRoot.getElementById(id).querySelector("#deviceExperiencesStatus").classList.remove("text-danger")
                this.shadowRoot.getElementById(id).querySelector("#deviceExperiencesStatus").innerHTML = "Loaded"
            } else {
                this.shadowRoot.getElementById(id).querySelector("#deviceExperiencesStatus").innerHTML = "Not Loaded"
                this.shadowRoot.getElementById(id).querySelector("#deviceExperiencesStatus").classList.add("text-danger")
                this.shadowRoot.getElementById(id).querySelector("#deviceExperiencesStatus").classList.remove("text-success")
            }

        })
    }
    updateStatus(list) {
        list.forEach(device => {
            this.getCurrentExperience(device.id);
            this.getBatteryPercentage(device.id);
            this.checkLoadedExperiences(device.id);
        })
    }
    getSelected() {
        let selected = []
        this.shadowRoot.querySelector("#body-container").querySelectorAll("input").forEach(check => {
            if (check.checked) {
                selected.push(check.parentElement.parentElement.id)
            }
        })
        return selected
    }
    selectAll() {
        this.shadowRoot.querySelector("#body-container").querySelectorAll("input").forEach(check => {
            check.checked = true
        })
    }
    deselectAll() {
        this.shadowRoot.querySelector("#body-container").querySelectorAll("input").forEach(check => {
            check.checked = false
        })
    }
    overrideSelected() {
        if (this.shadowRoot.querySelector("#selectControl").checked === true) {
            this.selectAll()
        }
        else {
            this.deselectAll()
        }
    }
    updateSelected(el) {

        if (el.checked === false) {
            this.shadowRoot.querySelector("#selectControl").checked = false
        }
    }
}
customElements.define('device-table', DeviceTable);


function get_devices() {
    console.log('polling for new devices')
    fetch('devices', {
        method: 'GET',
    })
        .then(function (response) {
            if (!response.ok) {
                throw Error(response.statusText);
            }
            return response.json()
        })
        .then(function (json) {
            var devices_count = json['devices'].length;


            if (JSON.stringify(json['devices']) != JSON.stringify(current_devices)) {
                document.getElementById("main-container").innerHTML = "";
                var devicetable = new DeviceTable(json['devices'])
                document.getElementById("main-container").appendChild(devicetable);

                current_devices = json['devices'];
                devicetable.updateStatus(devicetable.deviceList);
            }
            document.querySelector("device-table").updateStatus(document.querySelector("device-table").deviceList);
            if (devices_count == 0) {
                document.getElementById("main-container").innerHTML = `<h2 class="w-100 text-center p-3" id="no-devices">No Devices Connected.</h2>`

            }

        })
        .catch(function (error) {
            console.log(error);
        })

}
function set_icon(el) {
    var icon_modal = $('#setIconModal');
    var device_id = el.getAttribute('id');
    $(icon_modal).modal('show');

    function icon_modal_helper() {
        // put your default event here
        $(icon_modal).modal('hide');
        var selected = $("input[type='radio'][name='icon-options']:checked");
        if (selected) {
            var col = $(selected[0]).data('col');
            var icon = $(selected[0]).data('icon');
            var cloned_icon = $(selected.parent().find('svg')[0]).clone();
            cloned_icon.css('color', col);


            fetch('set-device-icon/' + device_id, {
                method: 'POST',
                body: JSON.stringify({ 'col': col, 'icon': icon }),
                headers: { "Content-type": "application/json" }
            }).then(function (response) {
                if (!response.ok) {
                    throw Error(response.statusText);
                }
                return response.json();
            }).then((response) => {

            }).catch(function (error) {

            }).finally(function () {
                $('.icon-set').off("click", icon_modal_helper);
                location.reload();
            })
        }
    }

    $('.icon-set').on("click", icon_modal_helper);
}
get_devices();
setInterval(get_devices, 1000);
