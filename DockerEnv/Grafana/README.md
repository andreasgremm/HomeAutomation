# Grafana

[Grafana](https://grafana.com) ist eine Open Source Visualisierungsplattform.

In einer Docker-Umgebung lässt sich Grafana sehr einfach und schnell implementieren.
Beispielsweise auf dem Raspberry mit ```docker pull grafana/grafana:master-ubuntu```

Wenn Persistence für die Grafana-Installation benötigt wird, sollten die Berechtigungen richtig gesetzt werden. Hierzu folgende [Information](https://grafana.com/docs/grafana/latest/installation/docker/) beachten.

```
mkdir -p /usr/local/etc/grafana
. init.inc

# in the container you just started:
chown -R root:root /etc/grafana && \
chmod -R a+r /etc/grafana && \
chown -R grafana:grafana /var/lib/grafana && \
chown -R grafana:grafana /usr/share/grafana
exit
```

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