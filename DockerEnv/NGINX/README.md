# Nginx
[Nginx](https://de.wikipedia.org/wiki/Nginx) ist unter anderem ein Reverse-Web-Proxy.
Dieses Verzeichnis enthält die notwendigen "Inlcude" Dateien um eine [Docker-Installation](https://hub.docker.com/_/nginx) zu initiieren und im Host-System die relevanten Verzeichnisse anzulegen.

* init.inc: Initialisiert die Verzeichnisstruktur und die Konfigurationsdateien werden im Host-System hinterlegt.
* run.inc: Start des NGINX-Containers zur Nutzung


Die von init.inc erzeugte Verzeichnisstruktur unter /usr/local/etc/ muss durch die in diesem Verzeichnis hinterlegten Daten (Unterverzeichnis **usr\_local\_etc\_nginx** für die Home-Automation abgeglichen werden.

Insbesondere wird ein Benutzerauthentifizierung für verschiedene Proxy-Pfade benötigt, z.B.: Openhab.

Um die .httpasswd Datei anzulegen werden die Apache Utilities benötigt: ```apt-get install apache-utils```.

## Grafana Proxy
In der Datei **grafana.ini** müssen folgende Änderungen durchgeführt werden:

```
#################################### Server ####################################
        # Aenderungen in grafana.ini
        #[server]
        # domain = <grafana server name>
        # enforce_domain = false
        # root_url = %(protocol)s://%(domain)s:%(http_port)s/grafana/
        # serve_from_sub_path = true
```

## Openhab Proxy
Für Openhab muss ein virtueller neuer Host eingerichtet werden. Dieses inst in der NGINX - Konfiguration in **conf.d/default** spezifiziert.

Dieser Hostname muss dem **localhost** in /etc/hosts hinzugefügt werden.




