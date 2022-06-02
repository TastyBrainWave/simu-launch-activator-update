# Introduction

This file showcases the setup of DNSMasq and nginx on the PIs to ensure the Raspberry PI acts as the DNS server for the router, as well as faking all the necessary connections for the Oculus Quest Headset.

# Prerequisites

In order to set both of those up, we need to install then by running:

` sudo apt-get install dnsmasq nginx -y `

After this, inside the TP-Link routers, we need to set the DNS server to point to the IP of the Raspberry PI where we install the DNS as follows:

![](docs/tp-link-dns.PNG)

After all of these steps were followed, we are ready to setup the PI.

# The dnsmasq setup

In order to configure the dnsmasq tool, we need to edit its configuration file found at `/etc/dnsmasq.conf`. In order to edit it, we can use nano:

```
sudo nano /etc/dnsmasq.conf
```

Inside the file, ensure that the domain-needed, bogus-priv and expand-hosts are commented out (should be by default).

Next, add the following lines to the file:

```
domain=story-starter.com
interface=wlan0
bind-dynamic
dhcp-range=192.168.1.100,192.168.1.200,255.255.255.0,12h
```

This ensures that DHCP will also be controlled by the Raspberry Pi.

However, in order to get the actual DNS server going, we need to edit `/etc/dhcpcd.conf` which we can open with nano as before:

```
sudo nano /etc/dhcpcd.conf
```

Then, we need to add the following line (there is a premade configuration commented, however copy-pasting this is gonna make it a lot easier):

```
interface eth0
static ip_address=192.168.1.100
static routers=192.168.1.1
static domain_name_servers=192.168.1.1 8.8.8.8
```

Finally, make sure you saave both files and then we need to reboot the system as follows:

``` 
sudo reboot
```

# The nginx setup

The nginx setup is fairly straight forward, as it will involve two parts: one, where we setup our actual server with the app, which by now it should have been setup as a service, to always run; and two, loads of proxies to fake connections for the Quest headsets.

## Part one

In order to setup the server routing for the app, which is mainly a redirect based on the hostname `app.story-starter.com`, we need to add it to the `/etc/hosts` file as follows:

```
sudo nano /etc/hosts
```

At the end of the file, add the following line. Remember to save and close!

```
192.168.1.100           app.story-starter.com
```

After this, we need to create the nginx configuration file as follows:

```
sudo nano /etc/nginx/conf.d/story-starter.conf
```

This will create a new configuration file where you need to paste the following lines:

```
server {
    listen 80;

    server_name app.story-starter.com;

    location / {
        proxy_pass http://192.168.1.100:8000/;
    }
}
```

This will essentially guide all the requests from the server name to the app IP:PORT server.


## Part two

This part is fairly similar to part one, but in this case we will fake the domains for Facebook, Google, Oculus and other bits, so that we can make the headset think it is connected to WiFi!

To do that, open the hosts file and add the following lines:

```
192.168.1.100           graph.oculus.com
192.168.1.100           facebook.com
192.168.1.100           connectivitycheck.gstatic.com
192.168.1.100           www.google.com
192.168.1.100           play.googleapis.com
192.168.1.100           time.facebook.com
192.168.1.100           edge-mqtt.facebook.com
192.168.1.100           mqtt-mini.facebook.com
192.168.1.100           graph.facebook.com
```

Now, we need to create nginx configurations for each of those domains, so we do the following 2 nginx configuration files, in the same way as the story-starter.conf file:

1. The Google configuration (google.conf)

    ```
    server {
        listen 80;

        server_name .gstatic.com .google.com .googleapis.com;

        location / {
                return 204;
        }
    }
    ```

2. The Facebook & Oculus configuration (facebook.conf)

    ```
    server {
            listen 80;

            server_name .facebook.com, .oculus.com;

            location / {
                    return 200;
            }
    }
    ```




