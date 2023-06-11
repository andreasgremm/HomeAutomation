# HomeAutomation Pictures2Video
Im Rahmen der Homeautomation werden diverse Kameraaufnahmen abgespeichert.

Im Rahmen der allgemeinen Überwachung ist es die Überwachungskamera IPC-100A im Dachgeschoss, die per Bewegungserkennung regelmäßige Bilder auf die Synology DS215J per FTP sendet.

Im Rahmen der Hausalarmanlage ist es die WebCam am Raspberry im Wohnzimmer, die bei einer Bewegungserkennung über den [MQTT KameraController](../../MQTT/MQTT_KameraController/) gestartet wird und Bilder auf die Magenta-Cloud sendet.

Diese Bilder sind jedoch oft statisch, d.h sie enthalten kaum Änderungen. Ausser es findet tatsächlich eine entsprechende Bewegung statt. [ImageDiff](../BASH_ImageDiff/) vergleicht aufeinanderfolgende Bilder in einem Quellverzeichnis und speichert nur Bilder im Zielverzeichnis wenn eine merkliche Bildänderung stattgefunden hat.

Um die Anzahl der Dateien zu reduzieren, kann aus den Bildern ein Video erstellt werden.

Pictures2Video verarbeitet Eingangsbilder im Eingabeverzeichnis und erzeugt daraus einen Film im Ausgabeverzeichnis.

## Docker Image bauen
Das Dockerimage wird wie üblich gebaut:

```
docker build --tag=pictures2video:prod .
```

## Docker Image aufrufen
Die Quell- und Zielverzeichnisse müssen auf der lokalen Maschine vorhanden sein. Dieses kann auch durch das "mounten" von einer externen Maschine passieren.

Der Aufruf lautet:

```
docker run \
	-it --rm 
	--user `id -u`:`id -g` \
	-v "<Quellverzeichnis>":"/mnt/pictures_input" \
	-v "<Zielverzeichnis>":"/mnt/video_output" \
	pictures2video:prod 
```

Um eine interaktive Shell im Image aufzurufen, kann folgender Befehl verwendet werden:

```
docker run -it --rm --entrypoint=bash \
	--user `id -u`:`id -g`\
	-v "<Quellverzeichnis>":"/mnt/pictures_input" \
	-v "<Zielverzeichnis>":"/mnt/video_output" \
	pictures2video:prod
```

Innerhalb der Shell kann dann die Bild-zu-Video Konvertierung interaktiv gestartet werden:

```
/home/appuser/pictures2video.bash /mnt/pictures_input /mnt/video_output
```

