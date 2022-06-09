var itemList = []
//class DeviceTable extends HTMLElement {
//    constructor(devices)
//}
class DeviceItem extends HTMLTableRowElement {
    constructor(device, selected) {
        super();
        this.attachShadow({ mode: 'open' });
        var bootstrapStyles = document.createElement('link')
        bootstrapStyles.rel = 'stylesheet'
        bootstrapStyles.href = 'static/bootstrap-5.2.0-beta1-dist/css/bootstrap.css'
        this.shadowRoot.appendChild(bootstrapStyles);
        this.shadowRoot.appendChild(document.querySelector("#device-list-item").content.cloneNode(true));

        this.deviceId = device['id'];
        this.device_icon = device['icon'];
        this.selected = selected;
        this.updateMessage(device['message']);
        var checkbox = this.shadowRoot.getElementById("itemSelect");

        checkbox.addEventListener('change', () => {
            if (checkbox.checked) {
                this.updateSelected(true)
            } else {
                this.updateSelected(false)
            }
        })

        if (this.device_icon) {
            var el = this.shadowRoot.getElementById('setIcon');
            $(el).children('svg').remove();

            var col = this.device_icon['col'];
            var icon = this.device_icon['icon'];
            var my_id = '#' + col + '-' + icon;

            $('.icon-set').each(function () {
                if ($(this).data('col') === col && $(this).data('icon') === icon) {
                    var found = $(this).parent().find('svg')
                    var cloned_icon = $(found).clone();
                    cloned_icon.css('color', col);
                    $(el).append(cloned_icon);
                }
            });
        }


        var check_battery_mins_wait = 5;
        this.getBatteryPercentage()
        this.batteryInterval = setInterval(() => {
            this.getBatteryPercentage()
        }, check_battery_mins_wait * 60 * 1000);

    }

    kill() {
        clearInterval(this.batteryInterval);
    }

    update_icon(icon) {
        var find_icon = this.shadowRoot.getElementById("setIcon");
        var svg_parent = $(find_icon).find('svg').parent()
        $(svg_parent).children('svg').remove();
        $(svg_parent).append(icon);
    }

    updateSelected(selected) {
        if (selected === true) {
            this.selected = true;
            checkSelected();
        } else {
            this.selected = false;
            checkSelected();
        }
    }

    getBatteryPercentage() {

        fetch("/battery/" + this.deviceId).then(response => {
            return response.json()
        }).then(data => {
            if (data >= 60) {
                this.shadowRoot.getElementById("batteryBadge").classList.add("text-bg-success")
                this.shadowRoot.getElementById("batteryBadge").classList.remove("text-bg-danger")
                this.shadowRoot.getElementById("batteryBadge").classList.remove("text-bg-warning")
            } else if (data < 60 && data >= 30) {
                this.shadowRoot.getElementById("batteryBadge").classList.add("text-bg-warning")
                this.shadowRoot.getElementById("batteryBadge").classList.remove("text-bg-success")
                this.shadowRoot.getElementById("batteryBadge").classList.remove("text-bg-danger")
            } else {
                this.shadowRoot.getElementById("batteryBadge").classList.add("text-bg-danger")
                this.shadowRoot.getElementById("batteryBadge").classList.remove("text-bg-success")
                this.shadowRoot.getElementById("batteryBadge").classList.remove("text-bg-warning")

            }
            this.shadowRoot.getElementById("batteryPercent").innerHTML = data + "%";
        })
    }

    updateMessage(str) {
        var el = this.shadowRoot.getElementById("message");
        if (str.length > 0) {
            el.hidden = false;
        } else {
            el.hidden = true;
        }
        el.innerHTML = str;
    }
}

var deselectAll = function () {
    selectedItems().forEach(function (item) {
        item.updateSelected(false);
        item.shadowRoot.querySelector("input").checked = false
    })
}
var selectAll = function () {
    itemList.forEach(function (item) {
        item.updateSelected(true);
        item.shadowRoot.querySelector("input").checked = true
    })
}
window.customElements.define('device-element', DeviceItem);

testingarr = ["42345325", "654645", "65476", "746535", "23432432", "12315465"]

var devices_manager = function () {
    var api = {};

    var item_map = {}; // {device_name: {'item': my_item, 'poll': my_poll}

    var image_height = defaults.screen_height;
    var rate = defaults.screen_updates * 1000;

    api.refresh_devices = function () {
        location.reload();
    }

    api.set_icon = function (device_id, icon) {
        var device = item_map[device_id];
        device.update_icon(icon);
    }

    api.wifi_connect = function (el) {
        var device_id = el.getAttribute('device_id');
        var orig_text = el.innerHTML;
        el.innerHTML = 'please wait';
        el.classList.add('disabled');
        fetch("connect/" + device_id)
            .then(function (response) {
                return response.json()
            })
            .then(function (json) {
                if (json['success']) {
                    remove_item(device_id);
                } else {
                    showStatus(json['error']);
                }
            })
            .catch(function () {
                console.log('error with wifi connecting device ' + device_id);
            })
            .finally(function () {
                el.innerHTML = orig_text;
                el.classList.remove('disabled');
            });
    }

    api.refresh_image = function (el) {
        var device = el.getAttribute('device_id');
        fetch("device-screen/" + rate + "/" + image_height + "/" + device)
            .then(function (response) {
                return response.json()
            })
            .then(function (json) {
                if (json['base64_image']) {
                    var b64_image = json['base64_image'];
                    item_map[device].updateImage64(b64_image);
                }
            })
            .catch(function () {
                console.log('error with polling for device ' + device)
            });

    }

    function screengrab_polling(device, on) {

        if (on === undefined) on = true;

        // let's always remove existing polling
        if (item_map[device]['poll']) {
            clearTimeout(item_map[device]['poll']);
            item_map[device]['poll'] = undefined;
        }

        if (on) {
            setTimeout(function () {
                poll();
                item_map[device]['poll'] = setTimeout(poll, rate);
            }, Math.random() * 1000);

        }

        var lock = false;

        function poll(do_timeout) {
            if (do_timeout === undefined) do_timeout = true;
            if (lock) {
                return
            }
            lock = true
            fetch("device-screen/" + rate + "/" + image_height + "/" + device)
                .then(function (response) {
                    return response.json()
                })
                .then(function (json) {
                    if (json['base64_image']) {
                        var b64_image = json['base64_image'];
                        item_map[device].updateImage64(b64_image);
                    } else if (json['device-offline']) {
                        remove_item(device);
                    }
                })
                .catch(function () {
                    console.log('error with polling for device ' + device)
                    //api.refresh_devices()
                })
                .finally(function () {
                    if (item_map[device]) {
                        if (do_timeout) item_map[device]['poll'] = setTimeout(poll, rate);
                    }
                    lock = false;
                })
        }
    }

    function remove_item(item_id) {
        screengrab_polling(item_id, false);
        var item = item_map[item_id];
        item.kill();
        delete item_map[item_id];
        var i = itemList.indexOf(item_id);
        itemList.splice(i, 1);
        document.querySelector("#main-container").removeChild(item);
    }

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
                var devices_so_far = Object.keys(item_map);

                for (var device of json['devices']) {
                    var device_id = device['id'];
                    var found_at = devices_so_far.indexOf(device_id)
                    if (found_at === -1) {
                        var item = new DeviceItem(device, false);
                        item.classList.add('col')
                        itemList.push(item);
                        document.querySelector("#main-container").prepend(item);
                        item_map[device_id] = item
                        screengrab_polling(device_id, true);
                    } else {
                        item_map[device_id].updateMessage(device['message']);
                        devices_so_far.splice(found_at, 1);
                    }
                }
                for (var d_missing of devices_so_far) {
                    remove_item(d_missing)
                }

            })
            .catch(function (error) {
                console.log(error);
            })
    }

    get_devices();
    setInterval(get_devices, defaults.check_for_new_devices_poll);


    api.devices = function () {
        return item_map.keys;
    }

    return api;
}
    ();

var checkSelected = () => {
    if (selectedItems().length !== 0) {

    } else {

    }
}

var selectedItems = () => {
    var count = [];
    itemList.forEach((item) => {
        if (item.selected) {
            count.push(item);
        }
    })
    return count;
}
function set_icon(el) {
    var icon_modal = $('#setIconModal');
    var device_id = el.getAttribute('device_id');
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
            devices_manager.set_icon(device_id, cloned_icon);

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
            })
        }
    }

    $('.icon-set').on("click", icon_modal_helper);
}