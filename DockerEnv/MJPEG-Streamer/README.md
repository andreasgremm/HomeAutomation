# MJPEG Streamer
[MJPEG-Streamer](https://github.com/jacksonliam/mjpg-streamer) wird genutzt, um Bilder einer Web-Kamera über das Intranet Verfügbar zu machen.

Gegenüber dem Clone des genannten Repositories ist das Dockerfile verändert, um den Bedingungen der HomeAutomation zu genügen.

In der Home-Automation wird der MJPEG-Streamer vom [MQTT_KameraController](../../MQTT/MQTT_KameraController/README.md) gestartet.

## Docker Image 

```
docker build --tag=mjpegstreamer:prod .
docker run -d --name mjpegstreamer  \
    -v /mnt/mediencenter/Hochgeladen:/mnt/pictures_out \
    --device /dev/video0  -p 8080:8080 mjpegstreamer:prod
```

## Start des MJPG Prozesses mit Docker
Bei der Umstellung des MJPEG-Streamers auf Docker die Steuerung per **systemctl** anzupassen. Eine gute Beschreibung findet sich [hier](https://blog.container-solutions.com/running-docker-containers-with-systemd).

