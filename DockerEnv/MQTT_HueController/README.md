# MQTT Hue Controller
Dieses Programm dient als Mittler zwischen MQTT Messages und der Steuerung der Hue Lampen.

## Installation
Clone: https://github.com/andreasgremm/HomeAutomation.git

In den Programmen dieser Home-Automation-Serie werden diverse Sicherheitseinstellungen u.a. für MQTT und Hue benötigt. Diese Einstellungen halte ich als Dateien in einem separaten Verzeichnis und natürlich nicht auf GitHub.

Die Verzeichnisstruktur ist entsprechend einem Python Modul ***Security*** aufgebaut, im Python-Code steht folgender Abschnitt der dieses Modul verwendet:

```
###
#
# Provide the following values
#
# DefaultHueUser = "<hue api key"
# DefaultMQTTPassword = "<mqtt password"
# DefaultMQTTUser = "<mqtt user"

from Security.Hue import DefaultHueUser
from Security.MQTT import DefaultMQTTUser, DefaultMQTTPassword
```

Verzeichnisstruktur:

```
/non-git-local-includes/
	Security/
		__init__.py  # leere Datei
		MQTT.py      # Security Einstellungen für MQTT
		Hue.py.  # Security Einstellungen für Slacker
		...          # weitere Dateien für andere Programme
```

Um dieses Konzept auch in den Dockercontainern zu nutzen, müssen diese Dateien daher als Volume bereitgestellt werden.



Erzeugung eines Docker Volumes:

```
docker volume create non-git-local-includes

docker volume ls
DRIVER              VOLUME NAME
local               non-git-local-includes
```

Als nächster Schritt werden die benötigten "Include" Dateien mit den Security-Einstellungen für das Python-Programm in das erzeugte Volume kopiert.
Hierfür wird ein Container benötigt. Wier bauen einen kleinen leichtgewichtigen Container auf.

### Temporärer Container Alternative 1
In einem leeren Verzeichnis erzeugen wir folgendes Dockerfile:

```

# Small lightweight container to manage volumes:

FROM scratch
CMD
```

Mit folgenden Befehlen bauen wir einen kleinen Container und mounten das Volume.
```
docker build -t nothing .
docker container create --name temp --mount source=non-git-local-includes,destination=/non-git-local-includes nothing
```

### Temporärer Container Alternative 2
Bei dieser Alternative verwenden wir ein fertiges kleines Image (Busybox) aus dem Docker Hub.

```
docker container create --name temp --mount source=non-git-local-includes,destination=/non-git-local-includes busybox
```

### Daten in Volume kopieren.
In einem temporären leeren Verzeichnis er Filetansfer die bereitliegende Datenstruktur für **non-git-local-includes** in dem Unterverzeichnis **Security** bereitstellen.

Dieses Unterverzeichnis wird dann in den temporären Container kopiert.
#### Copy to Volume

```
docker cp Security temp:/non-git-local-includes/Security/
```
#### Info 1: Copy from Volume

```
docker cp temp:/non-git-local-includes/Security/ <some Directory>
```

#### Info 2: Test bei Bedarf
```
docker run --rm -it --mount source=non-git-local-includes,destination=/non-git-local-includes busybox
# ...  # Linux - Befehle im Container
# exit # Container beenden
```

#### Aufräumen des temporären Containers

```
docker rm temp
```

## MQTT HueController Container erzeugen und starten
Im Dockerfile werden beim Start des Hue Controllers verschiedene Parameter benötigt, die im Python-Programm als Aufrufparameter mit Defaults belegt sind.


Ein Parameter der sicherlich auf jeden Fall zu ändern ist, ist die IP-Adresse des MQTT-Brokers. Diese sollte im Dockerfile richtig gesetzt werden.
Auch ein eventueller andere Name für den MQTT-Client ist für Testzwecke (falls der produktive Client selber noch läuft) notwendig.

### Voraussetzung 
Als Basis für das HueController-Image dient das HueModule-Image mit dem Tag [huemodule:prod](../Hue). Dieses sollte vorher fertiggestellt sein.

Sind die Parameter richtig gesetzt, kann das Image gebaut werden.

```
docker build --tag=huecontroller:prod .
```
Soll die IP-Adresse des Brockers und/oder der Client-Name erst während des Image Build gesetzt werden, kann folgender Befehl verwendet werden.

```
docker build --build-arg buildtime_IP_Brocker="<IP.Adresse>" --build-arg buildtime_Client_Name="<Client-Name>" --tag=huecontroller:prod .
```

Das Programm kann dann folgendermassen gestartet werden:

```
docker run -d  \
  --name=huecontroller \
  --mount source=non-git-local-includes,destination=/non-git-local-includes,readonly \
  --restart unless-stopped \
  huecontroller:prod
```

IP Adresse des Brockers und/oder Client-Name können auch zur Laufzeit mittels der Umgebungsvariablen IP_Brocker oder Client_Name gesetzt werden.

```
docker run -d  \
  --name=huecontroller -e "IP_Brocker=<IP.Adresse" -e "Client_Name=<Client-Name>" \
  --mount source=non-git-local-includes,destination=/non-git-local-includes,readonly \
  --restart unless-stopped \
  huecontroller:prod
```
