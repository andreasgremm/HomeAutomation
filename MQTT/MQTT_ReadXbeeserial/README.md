# MQTT ReadXbee Serial
Dieses Programm dient als Mittler zwischen den ZigBee / Xbees und der Home-Automation.
Der als Controller konfigurierte Xbee ist per serieller Leitung an einem Kleinrechner (Raspberry - Homeautomation) an /dev/ttyAMA0 angeschlossen und läuft im API-Mode.

ReadXbee Serial liest und interpretiert die Meldungen auf der seriellen Leitung und gibt die relevanten Informationen als MQTT-Messages weiter.


## Installation
Clone: https://github.com/andreasgremm/HomeAutomation.git

In den Programmen dieser Home-Automation-Serie werden diverse Sicherheitseinstellungen u.a. für MQTT und Slack benötigt. Diese Einstellungen halte ich als Dateien in einem separaten Verzeichnis und natürlich nicht auf GitHub.

Die Verzeichnisstruktur ist entsprechend einem Python Modul ***Security*** aufgebaut, im Python-Code steht folgender Abschnitt der dieses Modul verwendet:

```
###
#
# Provide the following values
#
# DefaultMQTTPassword = "<mqtt password"
# DefaultMQTTUser = "<mqtt user"
from Security.MQTT import DefaultMQTTPassword, DefaultMQTTUser
```

Verzeichnisstruktur:

```
/non-git-local-includes/
	Security/
		__init__.py  # leere Datei
		MQTT.py      # Security Einstellungen für MQTT
		Slacker.py.  # Security Einstellungen für Slacker
		...          # weitere Dateien für andere Programme
```

### Installationsverzeichnis erstellen und vorbereiten

```
cp -R $HOME/HomeAutomation/MQTT $HOME/MQTT
cd $HOME/MQTT/MQTT_ReadXbeeserial
python3 -m venv pythonenv
. pythonenv/bin/activate
pip install --upgrade pip
pip install --upgrade setuptools
pip install -r requirements.txt
deactivate

sudo cp readxbeeserial.start_stop /etc/systemd/system/readxbeeserial.service
sudo systemctl enable readxbeeserial
sudo systemctl start readxbeeserial
```


