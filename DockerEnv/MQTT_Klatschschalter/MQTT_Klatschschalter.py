#!/usr/bin/env python3
# -*- coding: latin-1 -*-
###
import argparse
import atexit
import json
import threading
import time

# Zusatzfunktion
from http.client import HTTPConnection
from signal import SIGABRT, SIGINT, SIGTERM, signal
from urllib.parse import urlparse
import paho.mqtt.client as paho
###
#
# Provide the following values
#
# DefaultMQTTPassword = "<mqtt password"
# DefaultMQTTUser = "<mqtt user"
from Security.MQTT import DefaultMQTTUser, DefaultMQTTPassword

debug = False
lamps = [1, 2, 3]
scenes = ["Wohnen1", "Wohnen2", "Jump"]
# Zusatzfunktion - Status Alarm
conn = HTTPConnection("127.0.0.1:81")
header_data = {"Content-Type": "application/json"}

threadactive = False
klatsch_klatsch = 0
lampindex = 0
sceneindex = 0
anyLamp = False
anyRequest = json.dumps({"any": "on"})
client_id = ""


def background_wait():
    global sceneindex, lampindex, threadactive, klatsch_klatsch
    if debug:
        print("background_wait started", flush=True)
    time.sleep(timeout)
    if debug:
        print("Anzahl Klatscher: ", klatsch_klatsch, flush=True)
    if klatsch_klatsch == 1:
        pass
    if klatsch_klatsch == 2:
        mqttc.publish("hue/scene/on", scenes[sceneindex])
        sceneindex += 1
        if sceneindex == len(scenes):
            sceneindex = 0
    if klatsch_klatsch >= 3:
        mqttc.publish("hue/control", anyRequest)
    else:
        klatsch_klatsch = 0
    if debug:
        print("background_wait ended", flush=True)
    threadactive = False


def alarm(anyLamp):
    try:
        conn.connect()
        conn.request(method="GET", url="/api/alarmstatus", headers=header_data)
        r1 = conn.getresponse()
        returnmessage = json.load(r1)
        conn.close()

        if returnmessage["Alarm-Eingeschaltet"]["AUTO"]:
            print(returnmessage["Alarm-Eingeschaltet"]["AUTO"], flush=True)
            mqttc.publish("hue/alarm/1", "25500")
        else:
            mqttc.publish("hue/alarm/1", "56000")
    except Exception as err:
        if debug:
            print(err, flush=True)
        mqttc.publish("hue/alarm/1", "46920")

    time.sleep(5)
    mqttc.publish("hue/lamp/1", "off")


def on_connect(mosq, obj, flags, rc):
    if debug:
        print(
            "Connect client: " + mosq._client_id.decode() + ", rc: " + str(rc),
            flush=True,
        )
    mqttc.publish(
        "clientstatus/" + mosq._client_id.decode(), "ONLINE", 0, True
    )

    mqttc.subscribe("hue/any", 2)
    mqttc.subscribe("klatsch/wohnzimmer/detected", 2)


def on_disconnect(mosq, obj, rc):
    print(
        "Disconnect client: " + mosq._client_id.decode() + ", rc: " + str(rc)
    )


def on_message(mosq, obj, msg):
    global sceneindex, lampindex, klatsch_klatsch
    if debug:
        print(
            "Message received (on_message): "
            + msg.topic
            + ", QoS = "
            + str(msg.qos)
            + ", Payload = "
            + msg.payload.decode(),
            flush=True,
        )

    if msg.topic == "hue/any":
        anyLamp = msg.payload.decode() == "True"

        if klatsch_klatsch >= 3 and anyLamp:
            mqttc.publish("hue/scene/off", scenes[sceneindex])
            sceneindex = 0
            lampindex = 0
        if klatsch_klatsch >= 3 and not anyLamp:
            alarm(anyLamp)
        klatsch_klatsch = 0


def klatsch_detected(mosq, obj, msg):
    global klatsch_klatsch, threadactive
    if debug:
        print(
            "Message received (klatsch_detected): "
            + msg.topic
            + ", QoS = "
            + str(msg.qos)
            + ", Payload = "
            + msg.payload.decode(),
            flush=True,
        )
        if msg.payload.decode() == "1":
            if not threadactive:
                threadactive = True
                thread = threading.Thread(target=background_wait)
                thread.start()
            klatsch_klatsch += 1


def on_publish(mosq, obj, mid):
    print("mid: " + str(mid))


def on_subscribe(mosq, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_unsubscribe(mosq, obj, mid):
    print("UNSubscribed: " + str(mid))


def on_log(mosq, obj, level, string):
    print(string)


@atexit.register
def cleanup_final():
    print("Cleaning up: " + client_id)


def cleanup(sig, frame):
    print("Signal: ", str(sig), " - Cleaning up", client_id)
    mqttc.publish("clientstatus/" + client_id, "OFFLINE", 0, True)
    mqttc.loop_stop()
    mqttc.disconnect()


if __name__ == "__main__":
    """ Define the Parser for the command line"""
    parser = argparse.ArgumentParser(description="Klatschschalter.")
    parser.add_argument(
        "-b",
        "--broker",
        help="IP Adress des MQTT Brokers",
        dest="mqttBroker",
        default="localhost",
    )
    parser.add_argument(
        "-p",
        "--port",
        help="Port des MQTT Brokers",
        dest="port",
        default="1883",
    )
    parser.add_argument(
        "-c",
        "--client-id",
        help="Id des Clients",
        dest="clientID",
        default="MQTT_Klatschschalter",
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
        "-t",
        "--timeout",
        help="Time Out in Sekunden fuer die Zaehler der Klatscher",
        dest="timeout",
        default=3,
    )
    parser.add_argument(
        "-a",
        "--api",
        help="IP:PORT für die Abfrage des Autoalarmanlagenstatus",
        dest="conn",
        default="127.0.0.1:81",
    )
    args = parser.parse_args()
    options = vars(args)
    for sig in (SIGABRT, SIGINT, SIGTERM):
        signal(sig, cleanup)
    timeout = int(options["timeout"])
    client_id = options["clientID"]
    conn = HTTPConnection(options["conn"])
    mqttc = paho.Client(client_id=client_id, clean_session=True)
    # Assign event callbacks
    mqttc.on_message = on_message
    mqttc.message_callback_add("klatsch/wohnzimmer/detected", klatsch_detected)
    mqttc.on_connect = on_connect
    mqttc.on_disconnect = on_disconnect
    #   mqttc.on_publish = on_publish
    #   mqttc.on_subscribe = on_subscribe
    #   mqttc.on_unsubscribe = on_unsubscribe
    #   mqttc.on_log = on_log
    url_str = (
        "mqtt://"
        + options["user"]
        + ":"
        + options["password"]
        + "@"
        + options["mqttBroker"]
        + ":"
        + options["port"]
    )
    url = urlparse(url_str)

    mqttc.username_pw_set(url.username, url.password)
    mqttc.will_set("clientstatus/" + client_id, "OFFLINE", 0, True)
    mqttc.connect_async(url.hostname, url.port)
    mqttc.loop_forever(retry_first_connection=True)
