# Nginx
[Nginx](https://de.wikipedia.org/wiki/Nginx) ist unter anderem ein Reverse-Web-Proxy.
Dieses Verzeichnis enthält die notwendigen "Inlcude" Dateien um eine [Docker-Installation](https://hub.docker.com/_/nginx) zu initiieren und im Host-System die relevanten Verzeichnisse anzulegen.

* init.inc: Initialisiert die Verzeichnisstruktur  Desweiteren wird eine logrotate Konfiguration angelegt und die Konfigurationsdateien werden im Host-System hinterlegt.
* run.inc: Start des NGINX-Containers zur Nutzung

Die von init.inc erzeugte Verzeichnisstruktur unter /usr/local/etc/ muss durch die in diesem Verzeichnis hinterlegten Daten (Unterverzeichnis **usr\_local\_etc\_nginx** für die Home-Automation abgeglichen werden.

## Nutzung in Verbindung mit LetsEncrypt / CertBot
Bei der Nutzung in Verbindung mit [CertBot](../CertBot/README.md) wird das Script run.inc durch Docker-Compose ersetzt.

Die Konfigurationsdateien in ..../conf.d/ müssen für SSL sinnvoll angepasst werden.
Beispielsweise muss für den DynDNS-Domain-Eintrag der http Zugriff auf https umgelenkt werden und ein entsprechender **server** Eintrag für https Zugriff hinzugefügt werden.

Die Aufteilung der Zugriffe aus dem Intranet und dem Internet müssen entsprechend sein.

## Benutzerauthentifizierung / Authorisierung
Insbesondere wird ein Benutzerauthentifizierung für verschiedene Proxy-Pfade benötigt, z.B.: Openhab. Nodered-UI

Um die .httpasswd Datei anzulegen werden die Apache2 Utilities benötigt: 

```
apt-get install apache2-utils
cd <Directory für .htpasswd>
#1. Benutzer: -c erzeugt die Datei
htpasswd -c .htpasswd <Benutzer1>

#ab 2. Benutzer
htpasswd .htpasswd <Benutzer>

```
### Alternative (ToDo):
Eine Alternative zur Nutzung einer **.htpasswd** kann auch ein LDAP-Verzeichnisdienst integriert werden. Dieses scheint mir für 2 Anwender etwas überzogen zu sein. Für andere Anwendungsumgebungen kann es jedoch eine lohnenswerte Alternative sein.
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
Für Openhab muss ein virtueller neuer Host eingerichtet werden. Dieses inst in der NGINX - Konfiguration in **conf.d/homeautomation.conf** spezifiziert.

Dieser Hostname muss dem **localhost** in /etc/hosts hinzugefügt werden.
Weiterhin muss dieser im DNS auflösbar sein.





