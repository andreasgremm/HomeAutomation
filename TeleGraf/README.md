# TeleGraf

Telegraf is an agent written in Go for collecting metrics and writing them into InfluxDB or other possible outputs. 

Die Kombination mit InfluxDB und Grafana ist gut geeignet Messdaten zu erfassen, aufzuzeichnen und darzustellen.

Telegraf lässt sich sehr schnell und einfach in einer Docker-Umgebung implementieren.

Hierzu einfach ```docker pull telegraf``` ausführen und per ```docker run --rm telegraf telegraf config > /usr/local/etc/telegraf.conf``` die Basiskonfiguration sichern.

Diese kann dann nach den eigenen Anforderungen modifiziert werden und Telegraf wird dann gestartet.

```
docker run -d --name telegraf \
   -v /usr/local/etc/telegraf.conf:/etc/telegraf/telegraf.conf:ro telegraf
```

## Messung von Systemdaten

Eine Anwendung ist die Messung von Systemdaten der Raspberries. Bei dieser Anwendung eignet sich eine Docker-Implementierung von Telegraf leider nicht, da hier ein Zugriff auf viele Systeminformationen notwendig ist.

Auf [dieser](https://devconnected.com/how-to-setup-telegraf-influxdb-and-grafana-on-linux/#c_Install_Telegraf_as_a_service) und [dieser](https://angristan.xyz/2018/04/monitoring-telegraf-influxdb-grafana/) Webseite befindet sich Beschreibungen dieses Use-Cases.

In der diesem Git beigefügten telegraf.conf sind folgende Werte anzupassen:

In [global_tags]:

* **dc = "<?????>"**

In [agent] eventuell den Hostnamen setzen:

* **hostname = ""**
 
In [[outputs.influxdb]], auf Basis der Implementierung der InfluxDB. Ich habe bei mir die Authentifizierung mit Username/Password eingestellt.

* **urls = ["http://????:8086"]**
* **username = "telegraf"** (HTTP Basic Auth)
* **password = "????"** (HTTP Basic Auth)

In der Verbindung mit Grafana gibt es ein vorgefertigtes [Dashboard](https://grafana.com/grafana/dashboards/10578)

Das beigefügte Include-File [lokale_installation.inc](lokale_installation.inc) ermöglicht die automatisierte Installation auf Raspbian (Stretch und Buster). Dabei sollte die telegraf.conf bereits angepasst sein.


### Raspberry: Model & Co.
Unabhängig vom Anwendungsfall:
Folgende Befehle ermöglichen die Information über Raspberry Modellinforationen.

```
pinout # Ausgabe diverser Hardware-Informationen
cat /sys/firmware/devicetree/base/model # Ausgabe des Modells
```
