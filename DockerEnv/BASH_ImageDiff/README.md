# HomeAutomation ImageDiff
Im Rahmen der Homeautomation werden diverse Kameraaufnahmen abgespeichert.

Im Rahmen der allgemeinen Überwachung ist es die Überwachungskamera IPC-100A im Dachgeschoss, die per Bewegungserkennung regelmäßige Bilder auf die Synology DS215J per FTP sendet.

Im Rahmen der Hausalarmanlage ist es die WebCam am Raspberry im Wohnzimmer, die bei einer Bewegungserkennung über den [MQTT KameraController](../../MQTT/MQTT_KameraController/) gestartet wird und Bilder auf die Magenta-Cloud sendet.

Diese Bilder sind jedoch oft statisch, d.h sie enthalten kaum Änderungen. Ausser es findet tatsächlich eine entsprechende Bewegung statt. ImageDiff vergleicht aufeinanderfolgende Bilder in einem Quellverzeichnis und speichert nur Bilder im Zielverzeichnis wenn eine merkliche Bildänderung stattgefunden hat.

## Docker Image bauen
Das Dockerimage wird wie üblich gebaut:

```
docker build --tag=imagediff:prod .
```

## Docker Image aufrufen
Die Quell- und Zielverzeichnisse müssen auf der lokalen Maschine vorhanden sein. Dieses kann auch durch das "mounten" von einer externen Maschine passieren.

Der Aufruf lautet:

```
docker run \
	-it --rm \
	--user `id -u`:`id -g` \
	-v "<Quellverzeichnis>":"/mnt/camera_input" \
	-v "<Zielverzeichnis>":"/mnt/reduced_output" \
	imagediff:prod 
```

Um eine interaktive Shell im Image aufzurufen, kann folgender Befehl verwendet werden:

```
docker run -it --rm --entrypoint=bash \
    --user `id -u`:`id -g` \
	-v "<Quellverzeichnis>":"/mnt/camera_input" \
	-v "<Zielverzeichnis>":"/mnt/reduced_output" \
	imagediff:prod
```

Innerhalb der Shell kann dann die Differenzbildung interaktiv gestartet werden:

```
/home/appuser/Image_diff.bash /mnt/camera_input /mnt/reduced_output
```

