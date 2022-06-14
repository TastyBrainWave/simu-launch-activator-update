class DeviceTable extends HTMLElement {
    constructor(deviceList) {
        super();
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
            //row.querySelector("#icon").appendChild(document.createElement("img")).setAttribute("src", "static/" + device.icon.icon)

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
            console.log(data)
        })
    }
    getCurrentExperience(id) {
        fetch("/current-experience/" + id).then(response => {
            return response.json()
        }).then(data => {
            this.shadowRoot.getElementById(id).querySelector("#deviceCurrentExperience").innerHTML = data.current_app;
            console.log(data)
        })
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
            if (devices_count > 0) {
                var found = document.getElementById('no-devices');
                if (found) found.remove();
            }


            document.getElementById("main-container").innerHTML = "";
            document.getElementById("main-container").appendChild(new DeviceTable(json['devices']));
            console.log(json['devices'])
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
//setInterval(get_devices, 8000);