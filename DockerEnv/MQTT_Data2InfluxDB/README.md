# MQTT Data2InfluxDB
Dieses Programm schreibt MQTT-Daten (Temperatur/Helligkeit/...) in eine InfluxDB.
## Installation
Clone: https://github.com/andreasgremm/HomeAutomation.git

In den Programmen dieser Home-Automation-Serie werden diverse Sicherheitseinstellungen u.a. für MQTT benötigt. Diese Einstellungen halte ich als Dateien in einem separaten Verzeichnis und natürlich nicht auf GitHub.

Die Verzeichnisstruktur ist entsprechend einem Python Modul ***Security*** aufgebaut, im Python-Code steht folgender Abschnitt der dieses Modul verwendet:

```
###
#
# Provide the following values
#
# DefaultMQTTPassword = "<mqtt password"
# DefaultMQTTUser = "<mqtt user"
from Security.InfluxDB import (DefaultInfluxDB, DefaultInfluxDBPassword,
                               DefaultInfluxDBUser)

from Security.MQTT import DefaultMQTTPassword, DefaultMQTTUser
```

Verzeichnisstruktur:

```
/non-git-local-includes/
	Security/
		__init__.py  # leere Datei
		MQTT.py      # Security Einstellungen für MQTT
		InfluxDB.py.  # Security Einstellungen für InfluxDB
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
docker cp Security temp:/non-git-local-includes/
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

## MQTT Klatschschalter Container erzeugen und starten
Im Dockerfile werden beim Start des Data2InfluxDB verschiedene Parameter benötigt, die im Python-Programm als Aufrufparameter mit Defaults belegt sind.


Ein Parameter der sicherlich auf jeden Fall zu ändern ist, ist die IP-Adresse des MQTT-Brokers. Diese sollte im Dockerfile richtig gesetzt werden.
Auch ein eventueller andere Name für den MQTT-Client ist für Testzwecke (falls der produktive Client selber noch läuft) notwendig.


### Voraussetzung

Sind die Parameter richtig gesetzt, kann das Image gebaut werden.

```
docker build --tag=data2influxdb:prod .
```
Soll die IP-Adresse des Brockers, InfluxDB und/oder der Client-Name erst während des Image Build gesetzt werden, kann folgender Befehl verwendet werden.

```
docker build --build-arg buildtime_IP_Brocker="<IP.Adresse>" \
   --build-arg buildtime_Client_Name="<Client-Name>" \
   --build-arg buildtime_InfluxDB_Host="<InfluxDB Host>" --tag=data2influxdb:prod .
```

Das Programm kann dann folgendermassen gestartet werden:

```
docker run -d  \
  --name=data2influxdb \
  --mount source=non-git-local-includes,destination=/non-git-local-includes,readonly \
  --restart unless-stopped \
  data2influxdb:prod
```

IP Adresse des Brockers, InfluxDB und/oder Client-Name können auch zur Laufzeit mittels der Umgebungsvariablen IP_Brocker, InfluxDB_Host oder Client_Name gesetzt werden.

```
docker run -d  \
  --name=data2influxdb -e "IP_Brocker=<IP.Adresse" -e "Client_Name=<Client-Name>" \
  -e "InfluxDB_Host=<InfluxDB Host>" \
  --mount source=non-git-local-includes,destination=/non-git-local-includes,readonly \
  --restart unless-stopped \
  data2influxdb:prod
```
