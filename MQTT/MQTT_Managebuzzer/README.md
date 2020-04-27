# MQTT Manage Controller
Dieses Programm dient als Mittler zwischen MQTT Clients und dem Start einer Buzzerfunktion.
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
cd $HOME/MQTT/MQTT_Managebuzzer
python3 -m venv pythonenv
. pythonenv/bin/activate
pip install --upgrade pip
pip install --upgrade setuptools
pip install -r requirements.txt
deactivate

sudo cp managebuzzer.start_stop /etc/systemd/system/managebuzzer.service
sudo systemctl enable managebuzzer
sudo systemctl start managebuzzer
```

