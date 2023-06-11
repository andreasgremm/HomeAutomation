# Grafana

[Grafana](https://grafana.com) ist eine Open Source Visualisierungsplattform.

In einer Docker-Umgebung lässt sich Grafana sehr einfach und schnell implementieren.
Beispielsweise auf dem Raspberry mit ```docker pull grafana/grafana:master-ubuntu```

Wenn Persistence für die Grafana-Installation benötigt wird, sollten die Berechtigungen richtig gesetzt werden. Hierzu folgende [Information](https://grafana.com/docs/grafana/latest/installation/docker/) beachten.

```
. init_0.inc
###
#
#  In einer weiteren Session aus dem Container das Verzeichnis /etc/grafana in das lokale Dateisystem kopieren
#
#  docker cp grafana:/etc/grafana /usr/local/etc
#

. init_1.inc

# in the container you just started:
chown -R root:root /etc/grafana && \
chmod -R a+r /etc/grafana && \
chown -R grafana:root /var/lib/grafana && \
chown -R grafana:root /usr/share/grafana
exit
```
Beim ersten Aufruf von Grafana über den Web-Browser wird für den Benutzer admin (initiales Passwort: admin) ein neues Passwort gesetzt.

Alles weitere findet sich unter der [Grafana Dokumentation](https://grafana.com/docs/grafana/latest/).

## Grafana hinter einem Reverse-Proxy
Wenn Grafana hinter einem Reverse-Proxy konfiguriert wird, müssen verschiedene Anpassungen erfolgen.

In nginx.conf muss eventuell ein **resolver** eingetragen werden, hierzu im Abschnitt http folgenden Eintrag einbringen:

```
   resolver <DNS-Server>;
```

Desweiteren sind in der grafana.ini folgende Einträge zu aktivieren:

```
[server]
domain = <servername in nginx>
enforce_domain = false
root_url = %(protocol)s://%(domain)s:%(http_port)s/grafana/
serve_from_sub_path = true
```

Die zugehörige NGINX Konfiguration z.B.::


```
server {
    listen       80;
    server_name  <servername>;
    ...
    
location /grafana/ {
         proxy_pass http://raspberrypi:3000/grafana/;
    }
    
    ....
}
```

## Fehler : Database locked
Es werden für diverse Grafana Versionen über "database locked"-Fehler berichtet.

Eine Korrekturmöglichkeit ist die SqLite-DB auf den **journal_mode=WAL** zu setzen.
Hierzu muss Sqlite3 installiert und der Journal-Mode gesetzt werden:

```
apt-get update
apt-get install sqlite3
docker stop grafana
cp <Grafana.db> <Grafana.db>.backup
sqlite3 <Grafana.db>
PRAGMA journal_mode=WAL;
.exit
docker start grafana
```
