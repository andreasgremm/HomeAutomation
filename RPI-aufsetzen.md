# Raspberry PI für Homeautomation aufsetzen

## Raspbian Lite installieren und konfigurieren
* [Noobs](https://www.raspberrypi.org/downloads/noobs/) (aktuellste Version) herunterladen 
* SD-Karte formatieren
* Inhalt des NOOBS Verzeichnis, nachdem die heruntergeladene Datei entpackt wurde, auf die SD-Karte kopieren
* Eventuell ein USB-Stick (oder USB-Festplatte) >= 16GB bereithalten
* SD-Karte + USB-Stick in den Raspberry einlegen/einstecken
* Raspberry booten
* Im Noobs Screen die notwendigen Parameter einstellen
	* Sprache Deutsch
	* ev. WLAN verbinden
	* Installationsziel festlegen (/dev/sda bei USB-Stick)
	* RASPBIAN-Lite aussuchen (Desktop wird nicht benötigt)
	* Installation starten (ev. Wlan noch einmal selektieren, oder mehrfach versuchen, wenn der Download zuerst nicht funktioniert.

Nach der Installation sollte die durch DHCP vergebene **IP-Adresse** des Raspberry notiert werden (Konsolenoutput oder ```ifconfig```) und ein Update der installierten Pakete stattfinden.

```
sudo apt-get update
sudo apt-get full-upgrade
```

Nach der Installation sollten noch verschiedene Einstellungen getätigt werden, um das System vorzubereiten.

* raspi-config ausführen (sudo!)
	* den gewünschten Hostnamen einstellen
	* das gewünschte Passwort für den Benutzer **pi** einstellen
	* SSH aktivieren
	* Seriellen Konsolenausgang deaktivieren ABER
	* Serielle Schnittstelle aktivieren (aktiviert halten)
	* Zeitzone Europe/Berlin einstellen
	
Danach den Raspberry booten. ``` sudo reboot```.

Nach dem Reboot testen, ob der SSH Zugang ```ssh pi@<eingestellter hostname>.local```funktionert.

## SWAP vergrößern
Die Default-Einstellungen für SWAP sind nur 100MB, durch die Änderungen der Swap-Konfigurationsdatei **/etc/dphys-swapfile** setzen wir die doppelte Memorygröße als Swap-Size:

```
# /etc/dphys-swapfile - user settings for dphys-swapfile package
# author Neil Franklin, last modification 2010.05.05
# copyright ETH Zuerich Physics Departement
#   use under either modified/non-advertising BSD or GPL license

# this file is sourced with . so full normal sh syntax applies

# the default settings are added as commented out CONF_*=* lines


# where we want the swapfile to be, this is the default
#CONF_SWAPFILE=/var/swap

# set size to absolute value, leaving empty (default) then uses computed value
#   you most likely don't want this, unless you have an special disk situation
#CONF_SWAPSIZE=100

# set size to computed value, this times RAM size, dynamically adapts,
#   guarantees that there is enough swap without wasting disk space on excess
CONF_SWAPFACTOR=2

# restrict size (computed and absolute!) to maximally this limit
#   can be set to empty for no limit, but beware of filled partitions!
#   this is/was a (outdated?) 32bit kernel limit (in MBytes), do not overrun it
#   but is also sensible on 64bit to prevent filling /var or even / partition
#CONF_MAXSWAP=2048
```


## Serielle Schnittstelle konfigurieren

Folgende [Beschreibung](http://www.netzmafia.de/skripten/hardware/RasPi/RasPi_Serial.html) zeigt die Aktionen zur Konfiguration der seriellen Schnittstelle für verschiedene PI / Raspbian -Versionen auf.

Neben der Konfiguration der seriellen Schnittstelle während der Installation / Konfiguration mit **raspi-config** waren mit Raspbian-Buster noch folgende Befehle notwendig (sudo):

```
systemctl status serial-getty@ttyAMA0.service
systemctl stop serial-getty@ttyAMA0.service
systemctl disable serial-getty@ttyAMA0.service
systemctl status serial-getty@ttyS0.service
systemctl stop serial-getty@ttyS0.service
systemctl disable serial-getty@ttyS0.service
```
## Git Repository für HomeAutomation clonen
Git installieren und Repository clonen sowie die richtige Branch einstellen: 

```
sudo apt-get install git
git clone https://github.com/andreasgremm/HomeAutomation.git
git checkout MQTT_V2
```
## Docker installieren

[Sebastian Brosch](https://sebastianbrosch.blog/docker-auf-einem-raspberry-pi-installieren/) hat die Installation von Docker auf Raspbian-Buster gut beschrieben.

Mit den Befehlen

```
sudo curl -fsSL https://get.docker.com | sh
usermod -aG docker pi
``` 
wird Docker installiert und der Benutzer pi wird ermächtigt Container zu verwalten.

### Docker Images

Für die Installationen im HomeAutomation Umfeld werden verschiedene Docker-Images benötigt, deren Beschaffung und Nutzung in den jeweiligen README Dateien beschrieben ist. 

* [Grafana](DockerEnv/Grafana/README.md)
* [InfluxDB](DockerEnv/InfluxDB/README.md)
* [Mosquitto](DockerEnv/Mosquitto/README.md)
* [NGINX](DockerEnv/NGINX/README.md)

## Telegraf installieren
Für die Performance-Messung des Raspberry wird Telegraf verwendet. Die Beschreibung für das HomeAutomation Umfeld befindet sich [hier](DockerEnv/Telegraf/README.md).

## Backup auf die Synology vorbereiten
* /root/.ssh/authorized_keys bereitstellen
* ssh login von Synology interaktiv ausführen, um known_hosts zu ergänzen

## Login von Laptop/Workstation vorbereiten
* /home/pi/.ssh/authorized_keys bereitstellen

## Docker-Images für die HomeAutomation installieren
* [BASH_ImageDiff](DockerEnv/BASH_ImageDiff/README.md)
* [BASH_Pictures2Video](DockerEnv/BASH_Pictures2Video/README.md)
* [FSAPI](DockerEnv/FSAPI/README.md)
* [Hue](DockerEnv/Hue/README.md)
* [Mail](DockerEnv/Mail/README.md)
* [MQTT_AutoAlarmdetektor](DockerEnv/MQTT_AutoAlarmdetektor/README.md)
* [MQTT_Clientstatus2Slack](DockerEnv/MQTT_Clientstatus2Slack/README.md)
* [MQTT_Data2InfluxDB](DockerEnv/MQTT_Data2InfluxDB/README.md)
* [MQTT_HueController](DockerEnv/MQTT_HueController/README.md)
* [MQTT_Klatschschalter](DockerEnv/MQTT_Klatschschalter/README.md)
* [MQTT_Motiondetektor](DockerEnv/MQTT_Motiondetektor/README.md)
* [MQTT_RadioController](DockerEnv/MQTT_RadioController/README.md)
* [MQTT_Soundcontroller](DockerEnv/MQTT_Soundcontroller/README.md)
* [MQTT_TPLinkHS110](DockerEnv/MQTT_TPLinkHS110/README.md)
* [MJPEG-Streamer](DockerEnv/MJPEG-Streamer/README.md)

## MQTT - Programme (non Docker) installieren
Die Python-Programme laufen im Verzeichnis /home/pi/MQTT und werden über virtuelle Umgebungen voneinander unabhängig implementiert.
Hierzu muss das Python-Modul für virtuelle Umgebungen installiert werden.

```
sudo apt-get install python3-venv
```
* [MQTT_KameraController](MQTT/MQTT_KameraController/README.md)
* [MQTT_Managebuzzer](MQTT/MQTT_Managebuzzer/README.md)
* [MQTT_ReadXbeeserial](MQTT/MQTT_ReadXbeeserial/README.md)

## Security Volume/Verzeichnis
Die Security Informationen für die verschiedenen Programme liegen als Include-Dateien **NICHT** im GitHub. Innerhalb der Programme wird beschrieben wie damit umzugehen ist.

## Bash Skripte installieren
Für verschiedene Funktionen werden [BASH-Scripte](BASH-Skripte/README.md) benötigt.

Für die Ausführung der Batch-Skripte werden, wie oben beschrieben, Einträge in der **/etc/fstab** und weitere Security-Einstellungen zum Mounten der entsprechenden Verzeichnisse benötigt.
Folgende Befehle mittels sudo ausführen:

```
mkdir -p /mnt/synology
mkdir -p /mnt/mediencenter
apt-get install davfs2
# unpriviligierten Benutzern erlauben WebDav Ressourcen einzubinden!
usermod -a -G davfs2 pi
```
 
## Node-Red installieren / konfigurieren
**Todo: Node-Red in Docker Container laufen lassen**
[Beschreibung: Node-Red in Docker](https://nodered.org/docs/getting-started/docker)

In der für die Home-Automation genutzten Raspbian-Light Variante ist **Node-Red** nicht vorinstalliert.

[Installation von Node-Red](https://nodered.org/docs/getting-started/raspberrypi#installing-node-red):

```
sudo apt install build-essential git
bash <(curl -sL https://raw.githubusercontent.com/node-red/linux-installers/master/deb/update-nodejs-and-nodered)
```
Hierbei wird folgende Ausgabe generiert:

```
Running Node-RED install for user pi at /home/pi on raspbian


This can take 20-30 minutes on the slower Pi versions - please wait.

  Stop Node-RED                       ✔
  Remove old version of Node-RED      ✔
  Remove old version of Node.js       ✔
  Install Node.js LTS                 ✔   Node v12.16.3   Npm 6.14.4
  Clean npm cache                     ✔
  Install Node-RED core               ✔   1.0.6 
  Move global nodes to local          -
  Install extra Pi nodes              ✔
  Npm rebuild existing nodes          -
  Add shortcut commands               ✔
  Update systemd script               ✔
                                      

Any errors will be logged to   /var/log/nodered-install.log
All done.
  You can now start Node-RED with the command  node-red-start
  or using the icon under   Menu / Programming / Node-RED
  Then point your browser to localhost:1880 or http://{your_pi_ip-address}:1880

Started  So 3. Mai 19:01:11 CEST 2020  -  Finished  So 3. Mai 19:07:19 CEST 2020
```

In der Datei /var/log/nodered-install.log finden sich folgende Hinweise:

```
## You may also need development tools to build native addons:
     sudo apt-get install gcc g++ make
## To install the Yarn package manager, run:
     curl -sL https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
     echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
     sudo apt-get update && sudo apt-get install yarn

```

Auch für den automatischen Start ist Node-Red vorbereitet:

```
cp /library/systemd/system/nodered.service /etc/systemd/system/nodered.service
## /etc/systemd/system/nodered.service editieren:
#Environment="NODE_OPTIONS=--max-old-space-size=256"

systemctl status nodered
● nodered.service - Node-RED graphical event wiring tool
   Loaded: loaded (/etc/systemd/system/nodered.service; disabled; vendor preset: enabled)
   Active: inactive (dead)
     Docs: http://nodered.org/docs/hardware/raspberrypi.html
```

Installation weiterer Module:

```
cd .node-red
npm install node-red-dashboard
```
### Flows kopieren
Die Flows aus dem alten Node-Red System exportieren (All Flows) und im neuen System importieren. Dieses geht auch gut direkt über die Zwischenablage.

Die Sicherheitseinstellungen für MQTT müssen wieder eingerichtet werden.
Dieses wird [hier](https://nodered.org/docs/user-guide/runtime/securing-node-red) beschrieben.
### Security einstellen
* adminAuth einstellen
* httpRoot einstellen (/nodered)

[NGINX für Node-Red](https://gist.github.com/boneskull/d418b7c871d2248cfeba) konfigurieren.

```
    location /nodered/ui/ {
         proxy_pass http://localhost:1880/nodered/ui/;
         proxy_http_version 1.1;
         proxy_set_header Upgrade $http_upgrade;
         proxy_set_header Connection "upgrade";
	     auth_basic  "Node Red Dashboard";
    	  auth_basic_user_file   /etc/nginx/conf.d/.htpasswd;
    }

    location /nodered/ {
         proxy_pass http://localhost:1880/nodered/;
         proxy_http_version 1.1;
         proxy_set_header Upgrade $http_upgrade;
         proxy_set_header Connection "upgrade";
    }
```

## certbot in Docker implementieren
LetsEncrypt ist ein freier Service und in diesem Zusammenhang ermögicht Certbot es Zertifikate für die Domäne zu implementieren.

CertBot mit Nginx in Docker ist [hier](https://github.com/wmnnd/nginx-certbot) beschrieben.

Docker Image von Certbot für Raspbian herunterladen:
```
docker pull certbot/certbot:arm32v6-latest
```

Das dort vorgestellte Initialisierungsscript muss für die gewünschten DynDNS / DNS Domänen **UND** den lokalen Verzeichnisstrukturen angepasst werden. Die NGINX-Konfigurationsdateien müssen für SSL angepasst werden.

Docker Compose muss installiert werden:

```
# Install required packages
sudo apt update
sudo apt install -y python3-pip libffi-dev

sudo pip3 install docker-compose
```

Das Docker-Compose File:

```
version: '3'

services:
  nginx:
    image: nginx
    restart: unless-stopped
    volumes:
      - /usr/local/etc/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - /usr/local/etc/nginx/conf.d:/etc/nginx/conf.d:ro
      - /var/log/nginx:/var/log/nginx
      - /etc/localtime:/etc/localtime:ro
      - /etc/timezone:/etc/timezone:ro
      - /usr/local/etc/certbot/conf:/etc/letsencrypt
      - /usr/local/etc/certbot/www:/usr/share/nginx/certbot
    ports:
      - "80:80"
      - "443:443"
    network_mode: host
    command: "/bin/sh -c 'while :; do sleep 6h & wait $${!}; nginx -s reload; done & nginx -g \"daemon off;\"'"
  certbot:
    image: certbot/certbot:arm32v6-latest
    restart: unless-stopped
    volumes:
      - /usr/local/etc/certbot/conf:/etc/letsencrypt
      - /usr/local/etc/certbot/www:/var/www/certbot
    entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew; sleep 12h & wait $${!}; done;'"

```

## Alexa Integration eigener Skills
Für den [Alexa-Skill](Alexa/README.md) "Automation", der die Hue-Lampen kontrolliert, nutze ich einen uWSGI Server in Verbindung mit NGINX.

In den entsprechenden NGINX Konfigurationen muss folgender Eintrag ergänzt werden:

```
    location /alexa  {
        include uwsgi_params;
        uwsgi_pass localhost:3031;
    }

```

