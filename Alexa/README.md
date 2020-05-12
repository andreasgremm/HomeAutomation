#Alexa Skill
Im Rahmen der Homeautomation läuft ein Skill "Automation".

Dieser Skill wurde mit **Flask-Ask** realisiert und läuft als WSGI Anwendung in einem Web-Server. Als WSGI Server wird [uWSGI](https://flask.palletsprojects.com/en/1.1.x/deploying/uwsgi/) verwendet.

Ein Beispiel befindet sich [hier](https://github.com/gabimelo/flask-boilerplate).

uWSGI läuft unter Docker und verwendet den Port 3031.

##Container erzeugen und starten
Image bauen:

```
docker build --tag=uwsgi:prod .
```


Um das Image zu starten ist ein Include-File (run.inc) im Verzeichnis enthalten.

```
docker run -d \
   --name=uwsgi \
   --network host \
   --mount source=non-git-local-includes,destination=/non-git-local-includes,readonly \
   --restart unless-stopped \
    uwsgi:prod
```
