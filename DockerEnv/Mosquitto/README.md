# Mosquitto
[Mosquitto](https://mosquitto.org) ist ein MQTT-Brocker und wird für die Programm-Programm Kommunikation genutzt.

Dieses Verzeichnis enthält die notwendigen "Inlcude" Dateien um eine [Docker-Installation](https://hub.docker.com/_/eclipse-mosquitto) zu initiieren und im Host-System die relevanten Verzeichnisse anzulegen.

* init.inc: Initialisiert die Verzeichnisstruktur. Desweiteren wird eine logrotate Konfiguration angelegt und die Konfigurationsdateien werden im Host-System hinterlegt. Achtung, vor der Nutzung von Docker muss ein Passwort-File als /etc/mosquitto/pwfile abgelegt werden. Siehe hierzu das Manual von [mosquitto_passwd](https://mosquitto.org/man/mosquitto_passwd-1.html). Über die Include-datein **run-sh.inc** kann eine interaktive Session mit dem Mosquitto-Container gestartet werden um diese Aufgabe durchzuführen.
* run-sh.inc: Interaktive Session mit dem Mosquitto-Container
* run.inc: Start des Mosquitto-Containers zur Nutzung


