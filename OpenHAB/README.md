# OpenHAB

## Vorbereitungen

Basis für die Installation von OpenHAB in Docker ist folgende [Beschreibung](https://www.openhab.org/docs/installation/docker.html).

Auf dem Raspberry Pi: ```vi ~/.profile```
Am Ende dann folgende Zeile einfügen:
**export COMPOSE\_HTTP\_TIMEOUT=240**


## OpenHAB Installation
[OpenHAB](https://www.openhab.org) ist eine Home-Automation Software mit vielen Schnittstellen (Bindings) zu diversen Systemen.

Auf dem System **openhab.local (192.168.1.114)** läuft eine [OpenHAB Docker Implementierung](https://hub.docker.com/r/openhab/openhab) auf einem [Hypriot](https://blog.hypriot.com) basierten Raspberry PI System.

Vor dem ersten Start ist der OpenHAB Benutzer zu konfigurieren (als root):

```
groupadd -g 9001 openhab
useradd -u 9001 -g openhab -r -s /sbin/nologin openhab
usermod -a -G openhab pirate
```

Das genutzte OpenHAB Compose File für die Milestone Version 2.5.0.M1:

```
version: '2.2'

services:
  openhab:
    image: "openhab/openhab:2.5.0.M1"
    restart: unless-stopped
    network_mode: host
    volumes:
      - "/etc/localtime:/etc/localtime:ro"
      - "/etc/timezone:/etc/timezone:ro"
      - "/var/OpenHAB/openhab_addons:/openhab/addons"
      - "/var/OpenHAB/openhab_conf:/openhab/conf"
      - "/var/OpenHAB/openhab_userdata:/openhab/userdata"
    environment:
      OPENHAB_HTTP_PORT: "8080"
      OPENHAB_HTTPS_PORT: "8443"
      EXTRA_JAVA_OPTS: "-Duser.timezone=Europe/Berlin"
```

Start OpenHAB per ```docker-compose up -d```.

## OpenHAB Persistence

Für die Speicherung von Zuständen wird in OpenHAB die Persistence verwendet.

In dieser Installation wird MySQL genutzt und ebenfalls per Docker gestartet.

Um die OpenHAB Persistence mit MySQL einzurichten wird vom Docker Hub eine entsprechende Version für den Raspberry benötigt. Hier bietet sich die [Hypriot MySQL](https://hub.docker.com/r/hypriot/rpi-mysql/) Implementierung an.

Für die Einrichtung der Funktionalität ist es sinnvoll die Datenbank erst einmal zu pullen und dann zu starten. 
Mit ```docker pull hypriot/rpi-mysql```wird der Container in die lokale Installation heruntergeladen.

Für den Start verwendete ich folgendes docker-compose-db.yaml

```
version: '2.2'

services:
  # Database
  db:
    image: hypriot/rpi-mysql
    volumes:
      - "/etc/localtime:/etc/localtime:ro"
      - "/etc/timezone:/etc/timezone:ro"
      - /var/lib/mysql:/var/lib/mysql
    restart: unless-stopped
    environment:
      MYSQL_ROOT_PASSWORD: mysqlfun
      MYSQL_DATABASE: OpenHAB
      MYSQL_USER: openhab
      MYSQL_PASSWORD: openhab
    ports:
      - 3306:3306
```

Da die Leistung des Raspberry für den erstmaligen Start nicht ausreicht läuft der start mit ```docker-compose -f docker-compose-db.yaml -p db -d up``` auf einen Timeout. Auch der zweite Startversuch läuft in der Ausgabe auf einen Timeout, aber mit ```docker ps```sieht es gut aus - die Datenbank läuft.

Mittels ```docker exec -it db_db_1 bash``` kann eine Verbindung aufgebaut werden und mit ```mysql -p``` und der anschliessenden Eingabe des MYSQL\_ROOT\_PASSWORD erzeugt ein ```show databases;``` das erwartete Ergebnis:

```
+--------------------+
| Database           |
+--------------------+
| information_schema |
| OpenHAB            |
| mysql              |
| performance_schema |
+--------------------+
4 rows in set (0.00 sec
```

mittels ```use OpenHAB;```wird auf die Datenbank OpenHAB umgeschaltet und ein ```show tables;```zeigt aktuell keine Tabellen an.


In PaperUI wird dann die **MYSQL_Persistence** installiert und anschliessend im conf Unterverzeichnis *services* die Datei mysql.conf erzeugt:

```
# the database url like 'jdbc:mysql://<host>:<port>/<database>' (without quotes)
url=jdbc:mysql://127.0.0.1:3306/OpenHAB?useJDBCCompliantTimezoneShift=true&useLegacyDatetimeCode=false&serverTimezone=Europe/Berlin

# the database user
user=openhab

# the database password
password=openhab
```
Anschliessend zeigt ```show tables;```in *mysql* bereits eine Tabelle namens **Items**.

Nach der Konfiguration der Datei mysql.persist im conf Unterverzeichnis *persistence* erscheinen weitere Tabellen **Item1** .. **Itemn** für die persistierten Items.


## Backup mit Synology implementieren

- Authorized Keys in /root/.ssh 
- ssh von Synology um Known-Hosts auf Synology zu implementieren
- rsync installieren