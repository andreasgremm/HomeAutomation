# InfluxDB
InfluxDB ist auf die Speicherung von Zeitserien optimiert. Zeitstempel sind immer in Relation zur Zeitzone zu sehen. Siehe hierzu auch [RFC 3339](https://www.ietf.org/rfc/rfc3339.txt). Dieser [Artikel](https://medium.com/easyread/understanding-about-rfc-3339-for-datetime-formatting-in-software-engineering-940aa5d5f68a) beschreibt es ganz gut.

Für die Arbeit mit InfluxDB ist es daher wichtig Zeitstempel in UTC umzurechnen, bevor diese in der InfluxDB gespeichert werden. 

## InfluxDB Installation

InfluxDB gibt es in verschiedenen Ausprägungen (OpenSource, Commercial) auf [DockerHub](https://hub.docker.com/_/influxdb?tab=description).

Nach dem "Pullen" der richtigen Version können initial die Datenbank, Admin- und Datenbankbenutzer initialisiert werden.

Für die Persistenz wähle ich ein Basis-Verzeichnis, in dem die Unterverzeichnisse etc und db erzeugt und für die Konfiguration und Datenbank genutzt werden.

In folgendem Snippet müssen die Werte in spitzen Klammern ersetzt werden.

```
mkdir -p /usr/local/etc/influxdb
mkdir -p /var/lib/influxdb

docker run --rm \
      -e INFLUXDB_DB=<Datenbank> \
      -e INFLUXDB_HTTP_AUTH_ENABLED=true \
      -e INFLUXDB_ADMIN_USER=admin -e INFLUXDB_ADMIN_PASSWORD=<secret1> \
      -e INFLUXDB_USER=<DB-User> -e INFLUXDB_USER_PASSWORD=<secret2> \
      -v $PWD/db:/var/lib/influxdb \
      influxdb /init-influxdb.sh

pushd etc
docker run --rm influxdb influxd config > influxdb.conf
popd

echo "###"
echo "#  in etc/influxdb.conf 'auth-enabled = true' setzen."
```

Anschliessend muss noch der Parameter *auth-enabled = false* in der Datei *etc/influxdb.conf* im Abschnitt \[http\] auf *auth-enabled = true* geändert werden.

## InfluxDB Start

Der Start des Containers kann mit folgendem Snippet erfolgen:

```
docker run -d --name influx \
      -p 8086:8086 \
      -v $PWD/etc/influxdb.conf:/etc/influxdb/influxdb.conf:ro \
      -v $PWD/db:/var/lib/influxdb \
      -v /etc/localtime:/etc/localtime:ro \
      -v /etc/timezone:/etc/timezone:ro \
      influxdb
```

## InfluxDB V2 Usage

Nach dem Backup und Restore einer aus Influxv1 gesicherten Datenbank ist ein V1 kompatibler Benutzer anzulegen.

```text
influx v1 auth create --help  
NAME:
   influx v1 auth create - Create authorization

USAGE:
   influx v1 auth create [command options] [arguments...]

COMMON OPTIONS:
   --host value                     HTTP address of InfluxDB [$INFLUX_HOST]
   --skip-verify                    Skip TLS certificate chain and host name verification [$INFLUX_SKIP_VERIFY]
   --configs-path value             Path to the influx CLI configurations [$INFLUX_CONFIGS_PATH]
   --active-config value, -c value  Config name to use for command [$INFLUX_ACTIVE_CONFIG]
   --http-debug                     
   --json                           Output data as JSON [$INFLUX_OUTPUT_JSON]
   --hide-headers                   Hide the table headers in output data [$INFLUX_HIDE_HEADERS]
   --token value, -t value          Token to authenticate request [$INFLUX_TOKEN]
   
OPTIONS:
   --org-id value                 The ID of the organization [$INFLUX_ORG_ID]
   --org value, -o value          The name of the organization [$INFLUX_ORG]
   --description value, -d value  Token description
   --username value               The username to identify this token
   --password value               The password to set on this token
   --no-password                  Don't prompt for a password. You must use v1 auth set-password command before using the token.
   --read-bucket value            The bucket id
   --write-bucket value           The bucket id
   
root@b8a2a5d61e4e:/# influx v1 auth create --org familie-gremm --username telegraf --password <password> --read-bucket <bucket id> --write-bucket <bucket id>
```

Desweiteren ist ein DBRP Mapping anzulegen, um die Default Retention Policy aus Influxdb V1.x auf das neue Bucket-Konzept von Influxdb V2.x zu mappen.

```bash
# Beispiel 
influx bucket list  # ermitteln der Bucket-ID für das Bucket telegraf/thirty_days
# Anlegen eines expliziten Mappings (überschreiben des automatisch angelegten virtuellen mappings)
influx v1 dbrp create --db telegraf --rp thirty_days --bucket-id cf8d47cbfd31c0ab --default
# Im Test war das DBRP trotz --default Angabe nicht auf Default gesetzt. Daher:
influx v1 dbrp update --id 0b528e493d763000 --rp thirty_days --default
```

## InfluxDB V1 Usage

* [key concepts](https://docs.influxdata.com/influxdb/v1.7/concepts/key_concepts/)
* [getting started](https://docs.influxdata.com/influxdb/v1.7/introduction/getting-started/)      
* [authentication and authorization](https://docs.influxdata.com/influxdb/v1.7/administration/authentication_and_authorization/)

Beispiele und Schnellstart:

```bash
docker exec -it influx bash
root@fb22790cf099:/# influx -precision rfc3339
> auth
username: admin
password: <password von admin>

> help show
Usage:
        connect <host:port>   connects to another node specified by host:port
        auth                  prompts for username and password
        pretty                toggles pretty print for the json format
        chunked               turns on chunked responses from server
        chunk size <size>     sets the size of the chunked responses.  Set to 0 to reset to the default chunked size
        use <db_name>         sets current database
        format <format>       specifies the format of the server responses: json, csv, or column
        precision <format>    specifies the format of the timestamp: rfc3339, h, m, s, ms, u or ns
        consistency <level>   sets write consistency level: any, one, quorum, or all
        history               displays command history
        settings              outputs the current settings for the shell
        clear                 clears settings such as database or retention policy.  run 'clear' for help
        exit/quit/ctrl+d      quits the influx shell

        show databases        show database names
        show series           show series information
        show measurements     show measurement information
        show tag keys         show tag key information
        show field keys       show field key information

        A full list of influxql commands can be found at:
        https://docs.influxdata.com/influxdb/latest/query_language/spec/

> show users
user    admin
----    -----
admin   true
openhab false

> create database homeautomation
> grant all on "homeautomation" to "openhab"
> show databases
name: databases
name
----
openhab
_internal
homeautomation

> grant all on "homeautomation" to "openhab"

### einige andere Befehle / Beispiele
> show  CONTINUOUS QUERIES
name: _internal
name query
---- -----

name: openhab
name                 query
----                 -----
cq_15m_Waschmaschine CREATE CONTINUOUS QUERY cq_15m_Waschmaschine ON openhab BEGIN SELECT mean(value) AS mean_value INTO openhab.a_year.downsampled_Waschmaschine_Power FROM openhab.two_weeks.Waschmaschine_Power GROUP BY time(15m) END
cq_15m_Trockner      CREATE CONTINUOUS QUERY cq_15m_Trockner ON openhab BEGIN SELECT mean(value) AS mean_value INTO openhab.a_year.downsampled_Trockner_Power FROM openhab.two_weeks.Trockner_Power GROUP BY time(15m) END

> show retention policies

name      duration  shardGroupDuration replicaN default
----      --------  ------------------ -------- -------
autogen   0s        168h0m0s           1        false
two_weeks 336h0m0s  24h0m0s            1        true
a_year    8736h0m0s 168h0m0s           1        false

```

## Migration von MySQL/MariaDB (OpenHAB) zu Influx

* https://forum.iobroker.net/topic/12482/frage-migrate-mysql-nach-influxdb
* https://github.com/earthcubeprojects-chords/chords/issues/171
* https://notes.ayushsharma.in/2017/08/migrating-mysql-database-tables-to-influxdb
	* https://github.com/ayush-sharma/infra_helpers/blob/master/influxdb/migrate_mysql_to_influxdb.py

Beispielschritte zur Konvertierung:
Die For-Schleife kann natürlich beliebig modifiziert werden und sollte nicht über die Anzahl der Datensätze in der MySQL-Datenbank gehen. In migrate_mysql_to_influxdb.py werden maximal 10000 Datensätze bearbeitet. (10000 ist ein Richtwert für den gleichzeitigen *INSERT* in die InfluxDB. Im unteren Beispiel werden also pro For-Lauf 100000 Datensätze konvertiert.

Sollte die Anzahl der Datensätze in der MySQL-Datenbank überschritten werden wird folgende Information ausgegeben:

	Written 3374 points for table temperature_log.
	No data retrieved from MySQL for table light_log.
	No data retrieved from MySQL for table temperature_log.

Und jetzt die Befehle:

```bash
python3 -m venv pythonenv
. pythonenv/bin/activate
pip install -u pip
pip install --no-cache-dir --trusted-host pypi.python.org -r requirements.txt
for i in `seq 1 10`; do python migrate_mysql_to_influxdb.py; done
# obige For-Schleife modifizieren oder öfter wiederholen
```

## <a name="retention"></a>Retention 
* https://docs.influxdata.com/influxdb/v1.7/guides/downsampling_and_retention/

OpenHab Beispiel:

```text
CREATE RETENTION POLICY "two_weeks" ON "openhab" DURATION 2w REPLICATION 1 DEFAULT
CREATE RETENTION POLICY "a_year" ON "openhab" DURATION 52w REPLICATION 1

CREATE CONTINUOUS QUERY "cq_15m_Waschmaschine" ON "openhab" BEGIN SELECT mean("value") AS "mean_value"  INTO "a_year"."downsampled_Waschmaschine_Power" FROM "Waschmaschine_Power" GROUP BY time(15m) END

CREATE CONTINUOUS QUERY "cq_15m_Trockner" ON "openhab" BEGIN SELECT mean("value") AS "mean_value"  INTO "a_year"."downsampled_Trockner_Power" FROM "Trockner_Power" GROUP BY time(15m) END

```

Beispiele für Abfragen:

```sql
> select * from "a_year"."downsampled_Waschmaschine_Power"
name: downsampled_Waschmaschine_Power
time                mean_value
----                ----------
1585047600000000000 0.3285518181818183
1585048500000000000 0.3665551333333333
1585049400000000000 0.3543815333333333

> select * from "a_year"."downsampled_Trockner_Power"
name: downsampled_Trockner_Power
time                mean_value
----                ----------
1585047600000000000 0.19696063636363637
1585048500000000000 0.2258042222222222
1585049400000000000 0.1631847272727273

```

### Beispiel: HomeAutomation Migration von MySql auf InfluxDB

Aktuell sind Daten über Helligkeit, Temperatur, Verbindungsqualität der Xbees und Spannungsmessung seit 2017 in der MySql/MariaDB Datenbank enthalten.

Interessant sind allerdings nur die Helligkeit und Temperaturwerte auf lange Sicht. Die Verbindungsqualität und Spannungsmessung dient nur kurzfristig der Fehlersuche.

Um diese Daten in eine InfluxDB zu migrieren um die Vorteile der automatisierten Retention zu nutzen, werden folgende Policies eingerichtet.

* *five_years*: enthält die heruntergerechneten Mittelwerte über 30 Minuten für 5 Jahre
* *four_weeks*: enthält die Realtime-Werte für 4 Wochen. Diese wird zur "Default" Retention-Policy erklärt. Dieses führt dazu, dass alle in die Influx-DB geschriebenen Daten (ohne eine spezifische Retention Policy anzugeben) direkt in *four_weeks* geschrieben werden.


Während der Migration ist die Periode für *four_weeks* allerdings auch auf 5 Jahre gesetzt und nach der erfolgten Migration mittels folendem Statement erst auf vier Wochen gesetzt.:

```sql
alter retention policy "four_weeks" on "homeautomation" duration 4w replication 1 default
```

Die Migration füttert erst einmal alle Daten in die "Default" - Retention Policy, nach der erfolgreichen Migration der Daten wird der Mittelwert in die 5 Jahres Retention Policy gespeichert.

```sql
create retention policy "five_years" on "homeautomation" duration 260w replication 1
create retention policy "four_weeks" on "homeautomation" duration 260w replication 1 default
```

Folgende "kontinuierlichen Abfragen" werden definiert um automatisiert die Mittelwerte einer 30 Minuten Periode dann dauerhaft abzuspeichern.
Da "kontinuierliche Abfragen" nur auf "Live-Werte" definiert sind, werden bei der Migration für die Füllung der "five_years" Retention die gleichen Queries verwendet. Also beispielsweise:

```sql
SELECT mean("light") AS "m_light"  INTO "five_years"."M_Helligkeit" FROM "four_weeks"."Helligkeit" GROUP BY time(30m), room
```

```sql
CREATE CONTINUOUS QUERY "cq_30m_Helligkeit" ON "homeautomation" BEGIN SELECT mean("light") AS "m_light"  INTO "five_years"."M_Helligkeit" FROM "four_weeks"."Helligkeit" GROUP BY time(30m), room END

CREATE CONTINUOUS QUERY "cq_30m_Temperatur" ON "homeautomation" BEGIN SELECT mean("temperatur") AS "m_temperatur"  INTO "five_years"."M_Temperatur" FROM "four_weeks"."Temperatur" GROUP BY time(30m), room END

CREATE CONTINUOUS QUERY "cq_30m_Temperatur_Nativ" ON "homeautomation" BEGIN SELECT mean("temperatur_n") AS "m_temperatur_n"  INTO "five_years"."M_Temperatur_nativ" FROM "four_weeks"."Temperatur_nativ" GROUP BY time(30m), room END

```

Wenn sich bereits Daten in der standard "Default" Retention Policy befinden, können diese in die neue Retention Policy "four_weeks" kopiert werden.

```sql
> SELECT * INTO "homeautomation"."four_weeks".:MEASUREMENT FROM "homeautomation"."autogen"./.*/ GROUP BY *
name: result
time written
---- -------
0    60000

> use homeautomation.four_weeks
Using database homeautomation
Using retention policy four_weeks
> show series
key
---
Helligkeit,room=AUTO
Helligkeit,room=Wohnzimmer
Temperatur,room=AUTO
Temperatur,room=Wohnzimmer
```

Mittelwert von 30 Minuten berechnen (1) und in eine andere Retention Policy schreiben (2):

```sql
(1)
> SELECT mean("temperatur") FROM "Temperatur" WHERE $timeFilter GROUP BY time(30m), "room"

(2)
> SELECT MEAN(*) INTO "homeautomation"."five_years".:MEASUREMENT FROM "homeautomation"."four_weeks"./.*/ GROUP BY time(30m),"room"
name: result
time written
---- -------
0    8132
```

Beispiel-Queries:

```sql
>select * from autogen.Helligkeit where room = 'AUTO'  LIMIT 10
name: Helligkeit
time                light room
----                ----- ----
1507196783708329984 779   AUTO
1507196916958800128 796   AUTO
1507197046040969984 769   AUTO
...

> select * from four_weeks.Helligkeit where room = 'AUTO'  LIMIT 10
name: Helligkeit
time                light room
----                ----- ----
1507196783708329984 779   AUTO
1507196916958800128 796   AUTO
1507197046040969984 769   AUTO
...

> select count(*) from Helligkeit
name: Helligkeit
time count_light
---- -----------
0    30000
> select count(*) from Helligkeit group by *
name: Helligkeit
tags: room=AUTO
time count_light
---- -----------
0    7499

name: Helligkeit
tags: room=Wohnzimmer
time count_light
---- -----------
0    22501

> settings
Setting           Value
--------          --------
Host              localhost:8086
Username          admin
Database          homeautomation
RetentionPolicy   four_weeks
Pretty            false
Format            column
Write Consistency all
Chunked           true
Chunk Size        0
```

### Python Beispiele zur Arbeit mit InfluxDB
Python Beispiele zur Arbeit mit InfluxDB gibt es [hier](https://influxdb-python.readthedocs.io/en/latest/examples.html)


## OpenHAB
Um Openhab mit InfluxDB zu nutzen sind folgende Punkte notwendig.

* Installation der Persistence "InfluxDB" in PaperUI
* Editieren der Datei influxdb.cfg (/var/OpenHAB/openhab_conf/system/influxdb.cfg)
* [Retention und Continous-Query](#retention) einstellen
* Editieren der Datei influxdb.persist (/var/OpenHAB/openhab_conf/persistence/influxdb.persist)
* Editieren der *rules*, um die zusätzliche Datenbank in den Abfragen einzupflegen wenn InfluxDB nicht die einzige (default *definiert in PaperUI-Configuration-System:Persistence*) Datenbank ist. z.B.: Trockner_Power.averageSince(now.minusMinutes(averageTimeTrockner)**,"influxdb"**)

## MySQL hints ....

Um einen einfachen Überblick über die MySQL Datenbanken zu bekommen hilft *PhpMyAdmin*.

```bash
docker run --name myadmin -d -e PMA_HOST=<dbhost> -p 8080:80 phpmyadmin/phpmyadmin
```

Per Web-Browser dann den Port 8080 nutzen. 

## Chronograf
Chronograf ist ein Tool um Datenbanken zu verwalten und hat einen Daten-Explorer ... kurz getestet, hilft ein wenig die Übersicht zu bekommen.

```bash
docker run -p 8888:8888 -v $PWD:/var/lib/chronograf chronograf --influxdb-url=http://openhab.local:8086
```

Innerhalb von Chronograf (Web-Browser Port 8888) muss dann die Verbindung authentifiziert werden.
