from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_restful import Api

from MQTT_Xbee.MqttInterface import *

app = Flask(__name__)
api = Api(app)
app.config.from_object('MQTT_Showtemperature_config')
Bootstrap(app)
#db = SQLAlchemy(app, session_options={'expire_on_commit': False })
db = SQLAlchemy(app)

mqttclient = MqttInterface()

from MQTT_Showtemperature_config import mqttc_default
from MQTT_Xbee import sichten
