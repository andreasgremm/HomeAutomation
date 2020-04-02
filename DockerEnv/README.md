# Verschiedenes
In diesem Verzeichnis liegen die Dockerprogramme. Dieses sind einmal MQTT Python Programme aber auch die notwendigen Systemprogramme.

Desweiteren möchte ich hier einige Hinweise und Hilfmitel zur Dokumentation hinterlegen.

# Zeiteinstellungen in Docker Containern

Auf [dieser](https://bobcares.com/blog/change-time-in-docker-container/) Webseite lassen sich die Zeiteinstellungen in Containern auf eine bestimmte Zeitzone einstellen.


# Cleanup von Python Programmen
Python Cleanup wird durch die Python utilities **black** und **isort** erledigt.
Beide können mit **pip install** lokal installiert werden.

Auf [dieser](https://leemendelowitz.github.io/blog/remove-carriage-return-control-character.html) Webseite werden verschiedene Möglichkeiten der Zeilen-Ende Konvertierung beschreiben. Beispielsweise Windows->Unix mit: 

```
tr -d '\r' < Windows.file > Unix.file
```

Innerhalb des VI kann, wie [hier](https://vim.fandom.com/wiki/Converting_tabs_to_spaces) beschrieben, mittels des **:retab** Kommandos die Umwandlung von ***Tabs*** in ***Spaces*** erfolgen.

# AVAHI
AVAHI dient der lokalen Namensauflösung und kann beispielsweise auf dem Mac folgendermaßen abgerufen werden:

```
dns-sd -B
dns-sd -L OpenHAB _http
Lookup OpenHAB._http._tcp.local
DATE: ---Wed 01 Jan 2020---
19:26:31.693  ...STARTING...
19:26:31.729  OpenHAB._http._tcp.local. can be reached at OpenHAB.local.:8080 (interface 5)
 path=/

dns-sd -B _services._dns-sd._udp
```

# Logrotate
Logrotate wird über /etc/crontab aufgerufen, die Konfigurationsdateien liegen in /etc/logrotate.d.

