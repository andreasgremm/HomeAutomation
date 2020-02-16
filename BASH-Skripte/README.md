# HomeAutomation Videoüberwachung
Im Rahmen der Homeautomation werden diverse Kameraaufnahmen abgespeichert.

Im Rahmen der allgemeinen Überwachung ist es die Überwachungskamera IPC-100A im Dachgeschoss, die per Bewegungserkennung regelmäßige Bilder auf die Synology DS215J per FTP sendet.

Im Rahmen der Hausalarmanlage ist es die WebCam am Raspberry im Wohnzimmer, die bei einer Bewegungserkennung über den [MQTT KameraController](../../MQTT/MQTT_KameraController/) gestartet wird und Bilder auf die Magenta-Cloud sendet.

Diese Bilder sind jedoch oft statisch, d.h sie enthalten kaum Änderungen. Ausser es findet tatsächlich eine entsprechende Bewegung statt. [ImageDiff](../BASH_ImageDiff/) vergleicht aufeinanderfolgende Bilder in einem Quellverzeichnis und speichert nur Bilder im Zielverzeichnis wenn eine merkliche Bildänderung stattgefunden hat.

Um die Anzahl der Dateien zu reduzieren und den benötigten Plattenplatz zu optimieren, kann aus den Bildern ein Video erstellt werden.

Pictures2Video verarbeitet Eingangsbilder im Eingabeverzeichnis und erzeugt daraus einen Film im Ausgabeverzeichnis.

ImageDiff und Pictures2Video sind allgemeingültig, daher werden sie über Skripte aufgerufen um die Ein- und Ausgabeverzeichnisse bereitzustellen.

## Installation
Die Bash-Skripte aus diesem Verzeichnis sollten in das Verzeichnis ```/usr/local/bin``` der aktuellen Maschine kopiert werden. 

## Run ImageDiff

### IPC-100A im Studio
Die Ausgaben der IPC-100A im Studio werden regelmäßig per FTP auf das Verzeichnis ```/home/FTP``` geschrieben.

Das Ergebnis der Differenzbildung wird im Verzeichnis ```/home/IPC100A_Diffs``` abgelegt.


/etc/fstab - Eintrag:

```
//192.168.1.241/home /mnt/synology  cifs rw,user,noauto,uid=pi,gid=pi,credentials=/home/pi/.cifs/secrets,vers=2.1 0 0
```

Die Datei /home/pi/.cifs/secrets enthält den Benutzernamen und das Passwort für den SMB-Mount des entsprechenden verzeichnisses.
Wenn sich der genutzte Benutzername auf dem Raspberry Pi ändert, wird sich natürlich auch die Lage der **secrets** Datei ändern.

```
username=<user>
password=<password>
```


### WebCam im Wohnzimmer
Die Ausgaben der WebCam im Wohnzimmer werden per WebDav-Mount auf das Verzeichnis ***Hochgeladen*** in der Magenta-Cloud abgelegt.

/etc/fstab - Eintrag:

```
https://webdav.magentacloud.de /mnt/mediencenter davfs rw,noexec,noauto,user,async,_netdev,uid=pi,gid=pi 0 0
```

Die Berechtigungen werden in der Datei $home/.davfs2/secrets hinterlegt.

```
/mnt/mediencenter <MagentaCloud User> <MagentaCloud User password>
```

## Run Pictures2Video
Pictures2Video mounted die Quellverzeichnisse der Bilder und das Ausgabeverzeichnis der Videos (/home/andreas/video) und konvertiert anschliessend die Bilder in ein Video und löscht die Quellbilder.

Das Video ist von der Größe her durch die .mp4-Kompression wesentlich kleiner als die Summer der Ursprungsbilder.

