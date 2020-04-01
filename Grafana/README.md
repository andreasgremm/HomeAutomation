# Grafana

[Grafana](https://grafana.com) ist eine Open Source Visualisierungsplattform.

In einer Docker-Umgebung lässt sich Grafana sehr einfach und schnell implementieren.
Beispielsweise auf dem Raspberry mit ```docker pull grafana/grafana:master-ubuntu```

Wenn Persistence für die Grafana-Installation benötigt wird, sollten die Berechtigungen richtig gesetzt werden. Hierzu folgende [Information](https://grafana.com/docs/grafana/latest/installation/docker/) beachten.

```
mkdir /usr/local/etc/grafana
. init.inc

# in the container you just started:
chown -R root:root /etc/grafana && \
chmod -R a+r /etc/grafana && \
chown -R grafana:grafana /var/lib/grafana && \
chown -R grafana:grafana /usr/share/grafana
exit
```

Alles weitere findet sich unter der [Grafana Dokumentation](https://grafana.com/docs/grafana/latest/).
