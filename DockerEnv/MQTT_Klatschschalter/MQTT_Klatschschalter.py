#!/usr/bin/env python3
# -*- coding: latin-1 -*-
###
import argparse
import atexit
import json
import threading
import time

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

debug = True
lamps = [1, 2, 3]
scenes = ["Wohnen1", "Wohnen2", "Jump"]

threadactive = False
klatsch_klatsch = 0
lampindex = 0
sceneindex = 0
timeout = 3
anyLamp = False
anyRequest = json.dumps({"any": "on"})
client_id = ""
auto_alarm = 2
auto_alarm_light = ['56000', '25500', '46920']


def background_wait():
    global sceneindex, lampindex, threadactive, klatsch_klatsch, timeout
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


def alarm():
    global auto_alarm, auto_alarm_light
    mqttc.publish("hue/alarm/1",
                  auto_alarm_light[auto_alarm])
    time.sleep(5)
    mqttc.publish("hue/lamp/1", "off")


def manage_alarm(mosq, obj, msg):
    global auto_alarm
    if debug:
        print(
            "Message received (manage_alarm): "
            + msg.topic
            + ", QoS = "
            + str(msg.qos)
            + ", Payload = "
            + msg.payload.decode(),
            flush=True,
        )

    if msg.payload.decode() == "False" or msg.payload.decode() == "True":
        auto_alarm = int(msg.payload.decode() == "True")


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
    mqttc.subscribe("alarm/auto/motion", 2)


def on_disconnect(mosq, obj, rc):
    print(
        "Disconnect client: " + mosq._client_id.decode() + ", rc: " + str(rc)
    )


def on_message(mosq, obj, msg):
    global sceneindex, lampindex, klatsch_klatsch, auto_alarm, auto_alarm_light
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
            thread = threading.Thread(target=alarm)
            thread.start()

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
    args = parser.parse_args()
    options = vars(args)
    for sig in (SIGABRT, SIGINT, SIGTERM):
        signal(sig, cleanup)
    timeout = int(options["timeout"])
    client_id = options["clientID"]
    mqttc = paho.Client(client_id=client_id, clean_session=True)
    # Assign event callbacks
    mqttc.on_message = on_message
    mqttc.message_callback_add("klatsch/wohnzimmer/detected", klatsch_detected)
    mqttc.message_callback_add("alarm/auto/motion", manage_alarm)
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
