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

## certbot implementieren

## Alexa