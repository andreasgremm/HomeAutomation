#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import atexit
from signal import signal, SIGABRT, SIGINT, SIGTERM
from urllib.parse import urlparse

import paho.mqtt.client as paho
from Buzzer import Buzzer
###
#
# Provide the following values
#
# DefaultMQTTPassword = "<mqtt password"
# DefaultMQTTUser = "<mqtt user"
from Security.MQTT import DefaultMQTTPassword, DefaultMQTTUser

buzzerpin = 0
mqttBuzzer = None
client_id = ""


@atexit.register
def cleanup_final():
    print("Cleaning up: " + client_id)


def cleanup(sig, frame):
    print("Signal: ", str(sig), " - Cleaning up", client_id)
    mqttc.publish("clientstatus/" + client_id, "OFFLINE", 0, True)
    mqttc.disconnect()


def on_connect(mosq, obj, flags, rc):
    print("Connect client: " + mosq._client_id.decode() + ", rc: " + str(rc))
    mqttc.publish(
        "clientstatus/" + mosq._client_id.decode(), "ONLINE", 0, True
    )
    mqttc.subscribe("buzzer/wohnzimmer", 0)


def on_disconnect(mosq, obj, rc):
    print(
        "Disconnect client: " + mosq._client_id.decode() + ", rc: " + str(rc)
    )


def on_message(mosq, obj, msg):
    global mqttBuzzer
    # 	print(msg.topic + " " + str(msg.qos) + " " + msg.payload.decode())
    if msg.topic == "buzzer/wohnzimmer":
        mqttBuzzer.play(int(msg.payload))


def on_publish(mosq, obj, mid):
    print("mid: " + str(mid))


def on_subscribe(mosq, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_unsubscribe(mosq, obj, mid):
    print("UNSubscribed: " + str(mid))


def on_log(mosq, obj, level, string):
    print(string)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Buzzer Manager.")
    parser.add_argument(
        "-b",
        "--broker",
        help="IP Adress des MQTT Brokers",
        dest="mqttBroker",
        default="localhost",
    )
    parser.add_argument(
        "-p",
        "--mqtt-port",
        help="Port des MQTT Brokers",
        dest="mqttport",
        default="1883",
    )
    parser.add_argument(
        "-c",
        "--client-id",
        help="Id des Clients",
        dest="clientID",
        default="MQTT_Managebuzzer",
    )
    parser.add_argument(
        "-u",
        "--user",
        help="Broker-Benutzer",
        dest="user",
        default=DefaultMQTTUser,
    )
    parser.add_argument(
        "-P",
        "--password",
        help="Broker-Password",
        dest="password",
        default=DefaultMQTTPassword,
    )
    parser.add_argument(
        "-bp", "--buzzer-pin", help="Buzzer Pin", dest="buzzerPin", default=25
    )
    args = parser.parse_args()
    options = vars(args)

    buzzerpin = int(options["buzzerPin"])
    mqttBuzzer = Buzzer.Buzzer(buzzerpin)

    for sig in (SIGABRT, SIGINT, SIGTERM):
        signal(sig, cleanup)

    client_id = options["clientID"]

    mqttc = paho.Client(client_id=client_id, clean_session=True)

    # Assign event callbacks
    mqttc.on_message = on_message
    mqttc.on_connect = on_connect
    mqttc.on_disconnect = on_disconnect
    # 	mqttc.on_publish = on_publish
    # 	mqttc.on_subscribe = on_subscribe
    # 	mqttc.on_unsubscribe = on_unsubscribe
    # 	mqttc.on_log = on_log

    url_str = (
        "mqtt://"
        + options["user"]
        + ":"
        + options["password"]
        + "@"
        + options["mqttBroker"]
        + ":"
        + options["mqttport"]
    )
    url = urlparse(url_str)

    # Connect
    mqttc.username_pw_set(url.username, url.password)
    mqttc.will_set("clientstatus/" + client_id, "OFFLINE", 0, True)
    mqttc.connect_async(url.hostname, url.port)

    mqttc.loop_forever(retry_first_connection=True)
