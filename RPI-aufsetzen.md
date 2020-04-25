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

