# HomeAutomation

## Komponenten
Die Heimautomation besteht aus mehreren Elementen.

* [dedizierten Controllern](#dedizierte-controller)
* [steuerbare Endgeräten](#steuerbare-endgeräte)
* [Sensoren](#sensoren)
* [Alexa](#alexa)
* [Klein-Computern mit aktiven Programmen](#klein-computer)

### <a name="dedizierte-controller"></a>Dedizierte Controller

* **SpeedPort W921V** Telekom Internet-WLAN-Router
* **Hue** als Controller für programmierbare Lampen
* **Somfy - Tahoma** als Controller für die Rolläden und Rauchmelder
* **Synology DS215j** Network Attached Storage
	* File-Store
	* git (Quellcode-Verwaltung, Versionskontrollsystem)
	* Backup für Raspberries
	* Surveillance-Station (Bewegungserkennung über Kamera)
	* FTP-Server

### <a name="steuerbare-endgeräte"></a>Steuerbare Endgeräte

* programmierbare Lampen

  Hue Lampen
	* Wohnzimmer1
	* Wohnzimmer2
	* Wohnzimmer3
* Rolläden
	* Arbeitszimmer Links
	* Arbeitszimmer Rechts
	* Küche Links
	* Küche Rechts
	* Wohnzimmer Links
	* Wohnzimmer Rechts
	* Wohnzimmer Terasse
* FS Internetradio
	* Küche
* Web Kamera
	* Studio
	* Gästezimmer

### <a name="sensoren"></a>Sensoren

* [**Klatschschalter**](#klatschschalter) im Wohnzimmer
	* Klatschdetektor
	* Bewegungsmelder
	* Temperatursensor
	* Lichtsensor
* [**Auto-Alarmanlage**](#auto-alarmanlage)
	* Bewegungsmelder
	* Temperatursensor
	* Lichtsensor
	* Spannungssensor
* [**RFID Reader**](#rfid-reader) ESP8266 im Flur
	* Mifare RFID Kartenleser

### <a name="alexa"></a>Alexa

* Küche
* Arbeitszmmer
* Schlafzimmer

### <a name="klein-computer"></a>Klein-Computer

* [**Homeautomation**] (#homeautomation) Raspberry Pi
* [OpenHAB](OpenHAB) Raspberry Pi
* **OpenElec** Raspberry Pi im Schlafzimmer

## Konzepte 
### Endbenutzerschnittstelle
Die Endbenutzerschnittstelle ist bei den meisten Systemen als "WebSeite" aufgebaut.   
Diese Webseite läuft entweder lokal auf den Systemen oder als Cloud-Anwendung bei einem Anbieter. Der Endanwender greift per Web-Browser mit dem HTTP oder HTTPS Protokoll auf die Anwendung zu.

###Anwendungsprogrammierschnittstellen (API)
Heutzutage werden zur Kommunikation zwischen Programmen sogenannte Anwendungsprogrammierschnittstellen (Application Programming Interfaces, API) genutzt.   
APIs basieren häufig ebenfalls auf dem HTTP/S Protokoll und können somit auch teilweise von einem Browser aufgerufen werden.

### Nachrichten (Messaging)
Nachrichten werden ebenfalls zur Kommunikation verwendet, unterliegen aber häufig einer anderen Intention als Endbenutzerschnittstellen oder APIs.
Der Empfang der Nachrichten ist häufig nicht synchron mit der Versendung und es liegt ein Vermittler (Broker) im Kommunikationsweg.
Desweiteren können Nachrichten auch an mehrere Empfänger versendet werden.
#### Endanwenderinformation
Um aus der Heimautomatiesierung heraus Nachrichten an einen oder mehreren Endanwendern zu versenden wird [**SLACK**] (https://slack.com/intl/de-de/) verwendet.

#### Kommunikation zwischen Programmen
Um innerhalb der Heimautomatisierung Nachrichten von einem Element zu anderen Elementen zu senden, wird [**MQTT**] (https://de.wikipedia.org/wiki/MQTT) verwendet.

### Kommunikationsnetzwerke
Kommunikationsnetzwerke bilden die Basis für Kommunikation zwischen Geräten. Zwei oder mehrere Geräte können miteinander kommunizieren wenn sie durch ein Kommunikationsnetzwerk miteinander verbunden sind. Geräte in unterschiedlichen Netzwerken benötigen Vermittler um zueinander zu finden.
In der gleichen Netzwerk-Art dienen **Router** als Vermittler, in unterschiedlichen Netzwerk-Arten dienen **Gateways** als Vermittler.
Router sprechen auf "beiden Seiten" das gleiche Protokoll. Gateways vermitteln zwischen unterschiedlichen Protokollen.

Kommunikationsnetzwerke bestehen aus mehreren [Schichten](https://de.wikipedia.org/wiki/OSI-Modell). 

#### Wide Area Network (WAN)
Das Wide Area Network bezeichnet ein Netzwerk welches auf einer globalen Ebene agiert. Das Internet ist so ein Wide-Area-Network, in früheren Zeiten wurden durch Telekommunikationsprovider auch Firmenstandorte vernetzt. Bekannt ist vermutlich das X.25 Protokoll.
Heutige Verbindungsarten sind typischerweise DSL (in unterschiedlichen Ausprägungen) und Glasfaser auf einer unteren Netzwerkschicht.

Zur Kommunikation auf einer höheren Netzwerkschicht wird heute fast ausschliesslich die Internet-Technologie das Internet-Protokoll (IP) verwendet, die auch für "private Wide Area Networks", welche nicht mit dem Internet verbunden sind genutzt wird. Der WAN-Anschluss stellt somit die Verbindung zum Internet her.
Die Teilnehmer am Internet werden mittels eines Routers am Internet angeschlossen. Diese Router werden entweder vom Provider (Telekom, UnityMedia, 1+1 ..) bereitgestellt oder durch den Endanwender gekauft (z.B.: Fritzbox). Auf der WAN Seite bedient der Router z.B.: DSL oder Glasfaser auf der untersten Protokolebene und IP auf Level 3 der Netzwerkschicht.
#### Mobilfunk
Mobilfunk basiert auf unterschiedlichen Technologien. Mobilfunkgeräte melden sich in sogenannten Zellen an und werden durch eine "Telefon-Nummer" identifiziert. Die Validierung basiert auf SIM-Karten, die bei dem Anbieter der Wahl erstanden werden. Über den Mobilfunk können mehrere Funktionlitäten genutzt werden.
Unterschiedliche Generationen der Mobilfunkprotokolle ermöglichen unterschiedliche Verbindungsgeschwindigkeiten.
Begriffe wie Edge, 3G, UMTS, LTE, 5G sind als Mobilfunkverbindung bekannt.

##### Sprache / SMS
Über den Mobilfunk werden insbesondere Sprache und Text (SMS) übertragen. Seit der Verbreitung von Smart-Phones werden auch Datendienste genutzt. 
##### mobile Daten
Eine weitere Verbindungsart für mobile Geräte ist die Datenverbindung auch als mobile Daten bekannt. Diese Datenverbindung wird vom Telekommunikationsbetreiber über ein Gateway mit dem Internet verbunden. Dieses ermöglicht die Nutzung von Internet Diensten (Web, Mail, ..) vom mobilen Gerät.
#### Local Area Network (LAN)
Ein Local Area Network bezeichnet ein Netzwerk inerhalb eines eingeschränkten, abgegrenzten Bereichs. Beispiele hierfür sind Firmengelände, Hochschulcampus oder eine Wohnung.
Ein LAN ist typischerweise "verkabelt" und ermöglicht so den Transport von Daten mit einer bestimmten Geschwindigkeit und einem oder mehreren Kommunikationsprotokollen.
Heutzutage wird IP als Kommunikationsprotokoll in typischen LAN Umgebungen verwendet.
Als Kabeltechnologie dienen häufig Ethernet-Kabel oder Glasfaser-Kabel.
#### Wireless LAN (WLAN)
In Zeiten von Laptops, Tablets, Smartphones entstand der Bedarf nicht nur per Kabel im LAN eingebunden zu werden. Die Wireless-LAN Technologie bindet Geräte über eine Funkschnittstelle in das Local Area Network ein.
Häufig werden durch den WAN-Router des Telekommunikationsbetreibers sowohl LAN Schnittstellen als auch WLAN bereitgestellt.

#### Analogtelefonie
Analoge Telefone sind schnurgebundene Telefone, die über eine 2-Draht-Leitung mit der Telefon-Vermittlungsstelle verbunden sind.
Bei einem Analoganschluss kann immer nur ein Gerät gleichzeitig genutzt werden.
Im Rahmen der Ausbreitung des Internet werden heutzutage keine analogen Telefonanschlüsse mehr von den Telekommunikationsanbietern bereitgestellt. 
Im Internet-Router wird die analoge Telefonie in Voice-Over-IP umgesetzt.
#### ISDN
Das ISDN Protokoll diente dem Anschluss von 2 Datenkanälen und einem Steuerkanal. Hierdurch konnten 2 Geräte gleichzeitig genutzt werden.
Die Internet-Router besitzen häufig einen ISDN-Basisanschluss, so dass bestehende ISDN Geräte angeschlossen werden können. Der Router verbindet dann die ISDN-Telefone mit Voice-over-IP.
#### DECT
Mit den Mobiltelefonen im Heimbereich wurde das DECT Protokoll eingeführt. DECT Basisstationen dienen als Gateway vom analogen Telefonanschluss zum mobilen Gerät.
Heutzutage werden die Internet-Router bereits mit einer DECT Basisstation ausgeliefert und übersetzen dann in Voice-over-IP.
#### ZigBee
[ZigBee] (https://de.wikipedia.org/wiki/ZigBee) ist ein eigenständiges Protokoll zur Verbindung von Sensoren und Aktoren mit geringen Datenraten und gößeren Reichweiten als WLAN.

### IP Protokoll
Das IP Protokoll besteht im Wesentlichen aus 3 unterschiedlichen Kommunikationsarten.

* TCP: Verbindungsorientiertes Protokoll. Die Kommunikationspartner haben eine 1:1 Verbindung. Im Rahmen der Netzwerkschichten wird die Auslieferung der Datenpakete sichergestellt.
* UDP: Verbinduntsloses Protokoll. Die Kommunikationspartner haben keine Verbindung. Der Sender schickt Datenpakete heraus und innerhalb der Programmierung muss die Auslieferung der Datenpakete sichergestellt werden.
* ICMP: Auf einer niedrigeren Protokollebene sind Funktionalitäten realisiert, die sich auf die Verbindung von Systemen konzentrieren.

Um am IP Protokoll teilzunehmen benötigen Systeme eine eindeutige IP-Adresse. Es gibt IP Version 4 und IP Version 6 Adressen. Der IP V4 Adressraum ist sehr beschränkt, der IP V6 Adressraum dagegen ist unendlich.
Mehrere IP-Adressen teilen sich ein sogenanntes IP-Netzwerk. Innerhalb dieses Netzwerks können sich die Systeme gegenseitig sehen. Unterschiedliche Netze müssen über Gateways/Router miteinander verbunden werden.

In der Home-Automation spielen im IP V4 Adressraum die "privaten" Adressen eine besondere Bedeutung.
Eine IP V4 Adresse wird per Quadrupel (a.b.c.d) und einer Netzwerk-Unterteilung bestimmt. Die Bezeichner a, b, c, d können Werte zwischen 0 und 255 einnehmen. 
Ein "privates" Netz ist im Internet nicht routbar weil es von vielen Netzwerken genutzt werden kann. 
Privat werden häufig die Netze im Bereich 192.168.x.y mit einer einer Netzmaske von 255.255.255.0.
In diesem Konstrukt teilen sich alle Rechner im Adressraum 192.168.x ein gemeinsames Netz. Ein konkreteres Beispiel: 
Die IP-Adresse: 192.168.1.254/255.255.255.0 ist mit der IP-Adresse: 192.168.1.1/255.255.255.0 in einem gemeinsamen Netz. 
Die IP-Adresse: 192.168.1.255/255.255.255.0 ist eine Broadcast-Adresse und ermöglicht die Versendung von Nachrichten an allen Rechnern im Netz.
Die Netzmaske /255.255.255.0 wird auch oft mit /24 abgekürzt, da die ersten 24 Bit das Netz bestimmen und die nächsten 8 Bit die spezifische Adressierung eines Gerätes ist.

Eine IP-Kommunikation benötigt neben der IP-Adresse zusätzlich noch einen sogenannten Port auf dem jeweiligen Gerät. Diese Kombination beschreibt einen Kommunikationsanschluss (Socket) vollständig.

Der Router des Telekommunikationsanbieters bekommt auf der WAN-Seite eine offizielle IP-Adresse und auf der LAN-Seite werden private IP-Adressen verwendet. Über eine "Network-Address-Translation (NAT)" werden die internen Adressen gegen eine externe IP-Adresse mit einem entsprechenden Port umgesetzt.

Zu den Ports:
Es gibt sogenannte ["Well known Ports"] (https://de.wikipedia.org/wiki/Liste_der_standardisierten_Ports), diese sind z.B.: für HTTP Server der Port 80 oder bei Nutzung von HTTP-Secure (HTTPS) der Port 443. SSH Server hören standardmäß9g auf den Port 22.

Clients verbinden sich mit einem Port auf dem Zielrechner und öffenen dafür einen Quellport auf dem eigenen System.
Beispiel: Web-Verbindung von Rechner a auf den Rechner b.
a(192.168.1.1, 55001) <-> b(192.168.1.241, 80)

Zu den Hostnamen:
Die Verwendung von IP-Adressen ist für Systeme "natürlich", für Menschen jedoch nicht sehr gut handhabbar.
Hier hilft das Konzept der "Hostnamen". Ein weltweiter Dienst namens **Domain Name Service** enthält ein Verzeichnis von Hostnamen zu IP Adressen. 

Neben den Hostnamen gibt es noch die Domain-Namen, die sich per "." an den Hostnamen anreihen.
Das Konstrukt www.google.de besteht aus einem Rechnernamen (wwww) und dem Domainnamen (google.de). Zusammen ergibt sich ein Fully-Qualified-Domain-Name (FQDN) von www.google.de.

Ein Beispiel für die Auflösung von www.google.de zu einer IP-Adresse, hierzu wird der Befehl **nslookup** verwendet.

```
C02WJ15LHV2Q:~ grean11$ nslookup www.google.de
Server:		127.0.0.1
Address:	127.0.0.1#53

Non-authoritative answer:
Name:	www.google.de
Address: 172.217.17.227
```

Bei jedem Aufruf eines Dienstes mit einem Hostnamen (z.B: https://www.google.de) wird per Domain-Namensauflösung eine IP-Adresse abgerufen mit der dann die finale Verbindung erfolgt.
Der Befehl **netstat -na** listet die aktuellen Verbindungen auf.

```
C02WJ15LHV2Q:~ grean11$ netstat -na | more
Active Internet connections (including servers)
Proto Recv-Q Send-Q  Local Address          Foreign Address        (state)    
....
tcp4       0      0  192.168.1.179.56486    172.217.17.227.443     ESTABLISHED
```

Der Domain-Name-Service ist ein hierarchisches System, in dem die Informationen zwischengespeichert (gecached) werden. Die Internet-Router der Telekommunikationsprovider werden so konfiguriert, dass sie einen DNS-Server im Internet ansprechen und selber einen DNS-Server darstellen. Die internen Rechner in einem Lan werden so konfiguriert, dass sie diesen internen DNS Server befragen, der dann wiederum die Informationen aus dem Internet holt.

Neben dem Domain-Name-Service gibt es weitere Namensauflösungen die im Bereich der Home-Automation relevant sind, sogenannte Local DNS Server.

Systeme können so konfiguriert werden, dass sie einen Namen oder Dienste in der Domäne "local" bekanntgeben. Diese Namen lassen sich oft leichter merken als die vergebenen IP-Adressen der Rechner.
Der Befehl **ping** prüft, ob ein Rechner verfügbar ist.

```
C02WJ15LHV2Q:~ grean11$ ping homeautomation.local
PING homeautomation.local (192.168.1.237): 56 data bytes
64 bytes from 192.168.1.237: icmp_seq=0 ttl=64 time=6.259 ms
64 bytes from 192.168.1.237: icmp_seq=1 ttl=64 time=3.719 ms
```


## Systemdetails

### Hue
Die Hue-Lampen werden durch die [Phillips-Hue-Bridge] (http://192.168.1.127) im Wohnzimmerschrank gesteuert.
Für die Steuerung kann die Hue-App des Handy genutzt werden. 
Es lassen sich sowohl die Lampen Wohnzimmer1 bis Wohnzimmer3 einzeln steuern als auch Szenen einrichten.
Aktuell sind drei Szenen eingerichtet: Wohnen1, Wohnen2 und Wohnen3.

Die Hue-Bridge ist neben der Steuerung durch die Hue-App auch über ein API steuerbar. Dieses API wird von Alexa und Programmen auf den Raspberries Homeautomation und OpenHAB genutzt.

Die Lampen selber werden von der Hue-Bridge über das ZigBee Protokoll gesteuert.

###<a name="homeautomation"></a>Homeautomation 
Auf dem Raspberry PI [Homeautomation] (http://192.168.1.237) laufen verschiedene Programme mit folgenden Funktionalitäten.

* MQTT Broker (Port 1883) als zentrale Schaltstelle für MQTT Nachrichten.
* MySQL Datenbank zur Speicherung von Informationen
* Apache WebServer 
	* [Informationsanzeige zu Sensoren] (http://192.168.1.237/wsgi/showtemperature/index)
 	* [MySql phpMyAdmin] (http://192.168.1.237/phpmyadmin/)
* NodeRed System (Port 1880) zur Darstellung und Steuerung verschiedener Funktionen
* Python Programme die sich per MQTT unterhalten:
	* HueController
	* Alarmdetektor
	* Motiondetektor
	* Klatschschalter
	* RadioController
	* ReadXbeeserial
	* Managebuzzer
	* Clientstatus2Slack
	* TplinkHS110Monitor (veraltet)

Über folgenden Mechanismus lässt sich der Status der Python-Programme kontrollieren:
Hierzu muss eine Terminal (SSH) Verbindung zu Homeautomation als Benutzer *pi* aufgebaut werden:
`ssh pi@192.168.1.237`

Mit folgendem Befehl werden alle relevanten Python-Programme aufgelistet `ps -ef  | grep MQTT`

```
root       318     1  0 Mai12 ?        00:24:57 /usr/bin/python3 /home/pi/MQTT/MQTT_HueController.py
root       320     1  0 Mai12 ?        00:26:51 /usr/bin/python3 /home/pi/MQTT/MQTT_Alarmdetektor.py
root       326     1  0 Mai12 ?        00:25:21 /usr/bin/python3 /home/pi/MQTT/MQTT_Clientstatus2Slack.py
root       332     1  0 Mai12 ?        01:08:31 /usr/bin/python3 /home/pi/MQTT/MQTT_ReadXbeeserial.py
root       336     1  0 Mai12 ?        00:29:19 /usr/bin/python3 /home/pi/MQTT/MQTT_Motiondetektor.py
root       346     1  0 Mai12 ?        00:25:27 /usr/bin/python3 /home/pi/MQTT/MQTT_Managebuzzer.py
root       349     1  0 Mai12 ?        00:25:26 /usr/bin/python3 /home/pi/MQTT/MQTT_RadioController.py
root       351     1  0 Mai12 ?        00:38:56 /usr/bin/python /home/pi/MQTT/MQTT_TplinkHS110Monitor.py
root     12900     1  0 Mai21 ?        00:25:27 /usr/bin/python3 /home/pi/MQTT/MQTT_Klatschschalter.py
pi       27834 27814  0 17:14 pts/1    00:00:00 grep --color=auto MQTT
```
Die obige Liste zeigt, dass zumindest alle Programme gestartet sind.
Manchmal hängen sich einzelne Programme leider auch auf. 

Gestartet werden die Programme als Systemdienst mittels  **systemctl** Kommando. 

Anmerkung: Das Kommando **systemctl** muss als Benutzer *root* ausgeführt werden. Dieses erreicht man, indem die Befehlszeile mit **sudo** gestartet wird. Beispiel aus einer Terminalsitzung:

```
pi@homeautomation:~ $ sudo systemctl status klatschschalter
● klatschschalter.service - MQTT Klatschschalter Service
   Loaded: loaded (/etc/systemd/system/klatschschalter.service; enabled; vendor preset: enabled)
   Active: active (running) since Tue 2019-05-21 20:23:34 CEST; 1 months 2 days ago
 Main PID: 12900 (python3)
   CGroup: /system.slice/klatschschalter.service
           └─12900 /usr/bin/python3 /home/pi/MQTT/MQTT_Klatschschalter.py

Warning: Journal has been rotated since unit was started. Log output is incomplete or unavailable.
```

Die Kontrolldateien liegen im Verzeichnis `/etc/systemd/system` und lassen sich mit `ls /etc/systemd/system`auflisten:

```
alarmdetektor.service               getty.target.wants       mysqld.service               sockets.target.wants
autologin@.service                  getty@tty1.service.d     mysql.service                sysinit.target.wants
bluetooth.target.wants              halt.target.wants        network-online.target.wants  syslog.service
dbus-fi.w1.wpa_supplicant1.service  huecontroller.service    poweroff.target.wants        systemmonitor.service
dbus-org.bluez.service              klatschschalter.service  radiocontroller.service      timers.target.wants
dbus-org.freedesktop.Avahi.service  managebuzzer.service     rc-local.service.d           tplinkmonitor.service
default.target                      mjpgstreamer.service     readxbeeserial.service
dhcpcd5.service                     motiondetektor.service   reboot.target.wants
display-manager.service             multi-user.target.wants  remote-fs.target.wants
```
Aus der obigen Liste werden die Zusammenhänge zwischen den Namen der Systemdienste und den Programmnamen deutlich.

Wenn z.B.: die Klatschschalter Funktion zur Steuerung der Hue-Lampen nicht funktioniert, kann dieses an zwei Komponenten liegen.

* Programm welches über die serielle Schnittstelle am Xbee angeschlossen ist.
* Programm "Klatschschalter" 
* Programm "Huecontroller"

Mit dem Befehl `sudo systemctl restart klatschschalter` wird beispielsweise der Systemdienst Klatschschalter neu gestartet, dieser beendet das Program MQTT_Klatschschalter.py und startet es danach neu.

In gleicher Form lassen sich die anderen Dienste wie **readxbeeserial** oder **huecontroller** neu starten.

###<a name="klatschschalter"></a>Klatschschalter
Der Klatschschalter ist eine elektronische Schaltung in einem Gehäuse mit den Funktionen

* Klatschdetektor
* Temperaturfühler
* Lichtsensor
* Bewegungsmelder

Die Daten werden per ZigBee - Protokoll übertragen. Die einzelnen Sensoren sind an Kontakten eines XBees angeschlossen. Ein Xbee ist ein Sender/Empfänger der sich programmieren lässt und mit anderen Xbees vernetzt.

Der Homeautomation Rechner dient als ZigBee Gateway. Hier ist über die serielle Schnittstelle ebenfalls ein Xbee angeschlossen. Über das Programm **MQTT_ReadXbeeserial.py** werden die Informationen gelesen und in Ausgangssignale an den IO-Pins des angeschlossenen Xbees umgesetzt bzw. in einer MySQL Datenbank gespeichert.
Die Ausgangssignale des angeschlossenen Xbees sind in einer elektronischen Schaltung mit Kontakten (IO-Pins) des Raspberry verbunden.
####Klatschdetektor
Der Klatschschalter sendet mit jedem erkannten Klatsch ein einzelnes Signal über das ZigBee Protokoll.
Dieses führt zu einzelnen Signalen an dem IO-Pin des Raspberries.
Der relevante Pin (GPIO 18) wird vom Programm **MQTT_Klatschschalter.py** gelesen und in Klatschsequenzen umgewandelt.

* 2 Klatscher schalten die Hue-Szenen Wohnen1 bis ..3 wechselweise.
* 3 Klatscher schalten die Lampen aus
* Bei ausgeschalteten Lampen: 3 Klatscher zeigen den Status der "Auto-Alarmanlage" an. 
	* grün: eingeschaltet
	* rot: ausgeschaltet

Die Steuerung erfolgt über MQTT - Nachrichten an das Programm **MQTT_HueController.py** welches wiederum das API der Hue-Bridge zur Steuerung der Lampen anspricht. 

Klatschschalter -(ZigBee)-> MQTT_ReadXbeeserial -(GPIO 18)-> MQTT_Klatschschalter -(MQTT)-> MQTT_HueController -(API)-> Hue-Bridge

####Bewegungsmelder
Wie bei dem Klatschschalter wird auch das Signal des Bewegungsmelders über das ZigBee-Gateway umgesetzt und als Signal an den Raspberry IO Pin 23 gesendet.

In Abhängigkeit des Status der Wohnzimmer-Alarmanlage führt das Signal zu folgenden Aktivitäten.

* über den **MQTT_HueController.py** wird eine Hue Leuchte (Wohnzimmer2) eingeschaltet, wenn es bereits nach Sonnenuntergang ist.
* der Dienst **mjpgstreamer** wird gestartet. Dieser nimmt Bilder über die am Raspberry angeschlossene WebCam auf und sendet diese auf die Magenta-Cloud.
* über Slack und Email wird eine Nachricht versendet. Diese enthält einen Link auf eine WebSeite mit dem Stream der WebCam (mjpgstreamer).

Wird keine Bewegung mehr erkannt, werden die Aktionen nach zwei Minuten wieder beendet.

* Hue-Lampe wird ausgeschaltet
* Der Dienst **mjpgstreamer** wird gestoppt

Bewegungsmelder -(ZigBee)-> MQTT_ReadXbeeserial -(GPIO 23)-> MQTT_Motiondetektor -(MQTT)-> MQTT_HueController -(API)-> Hue-Bridge

Die Wohnzimmer-Alarmanlage kann über den RFID Reader oder die WebSeite <http://192.168.1.237/wsgi/showtemperature/index> aktiviert werden. Bei der Aktivierung über der WebSeite wird aktuell der Status auch in der Datenbank geändert, so dass bei einem Neustart der Status persistent ist. 

#### Temperatur und Licht
Die Daten zu Temperatur und Licht werden in der MySQL Datenbank gespeichert.

###<a name="auto-alarmanlage"></a>Auto Alarmanlage
Im Auto ist eine selbstbebaute Alarmanlage installiert die folgende Sensoren beinhaltet:

* Bewegungsmelder
* Temperatur
* Licht
* Spannung

Die Sensoren sind an einem Xbee Sender angeschlossen und dieser nutzt das ZigBee Protokoll um die Daten an das ZigBee-Gateway zu senden. Dieses wird wie beschrieben umgesetzt und als Signal an den Raspberry IO Pin 4 gesendet.

In Abhängigkeit vom Status der Auto-Alarmanlage wird folgende Aktivität gestartet:

* Buzzer am Raspberry Homeautomation wird auf SOS Morsecode gesetzt.

Bewegungsmelder Auto -(ZigBee)-> MQTT_ReadXbeeserial -(GPIO 4)-> MQTT_Alarmdetektor -(MQTT)-> MQTT_Managebuzzer

Die Spannung für die Auto-Alarmanlage wird über eine Powerbank bereitgestellt, die während der Autofahrten aus der Netzspannung im Auto geladen wird. Diese hält ca. 3 Tage.

Temperatur, Licht und Spannungswerte werden in der MySQL-Datenbank gespeichert.

Die Auto-Alarmanlage kann über den RFID Reader oder die WebSeite <http://192.168.1.237/wsgi/showtemperature/index> aktiviert werden. Bei der Aktivierung über der WebSeite wird aktuell der Status auch in der Datenbank geändert, so dass bei einem Neustart der Status persistent ist. 

###<a name="rfid-reader"></a>RFID Reader
Der [**RFid_Reader**] (http://rfid_reader.local) besteht aus einem ESP8266 an dem ein RFID Kartenleser und ein Bewegungsmelder angeschlossen ist.

Aktuell werden folgende Karten für folgende Informationen genutzt:

* Ein- und Ausschalten der Wohnzimmer-Alarmanlage (Dauerlicht grüne LED)
* Ein- und Ausschalten der Auto-Alarmanlage (Dauerlicht rote LED)

Wenn die Wohnzimmer-Alarmanlage eingeschaltet ist, wird bei Bewegungserkennung ein Buzzer-Signal aktiviert. Dieses soll auf die eingeschaltete Anlage hinweisen.

Der RFID Leser agiert per MQTT Nachrichten mit der Umwelt.
Werden die Alarmfunktionen per Webseite geändert, wird dieses auch in den LEDs des RFID-Readers wiedergespiegelt.












