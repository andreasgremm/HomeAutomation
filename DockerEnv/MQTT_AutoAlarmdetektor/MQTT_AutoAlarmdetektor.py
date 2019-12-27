#!/usr/bin/env python3
# -*- coding: latin-1 -*-
###
#
# https://www.cl.cam.ac.uk/projects/raspberrypi/tutorials/robot/buttons_and_switches/
# http://sourceforge.net/p/raspberry-gpio-python/wiki/Inputs/
#

import argparse
import atexit
import datetime as dt
import threading
import time
from signal import signal, SIGABRT, SIGINT, SIGTERM
from urllib.parse import urlparse

import paho.mqtt.client as paho
from Security.MQTT import DefaultMQTTPassword, DefaultMQTTUser
from Security.Slacker import slackerKey
from slacker import Slacker

###
#
# Provide the following values
#
# slackerKey='<slackerKey'
# DefaultMQTTPassword = "<mqtt password"
# DefaultMQTTUser = "<mqtt user"
slack = Slacker(slackerKey)


alarmON = False
alarmActive = False
threadactive = False
client_id = ""
debug = False


def background_alarm_activity():
    global alarmON, threadactive, timeout
    contentText = " Autoalarm erkannt um: " + str(dt.datetime.now())
    rsp = slack.chat.post_message(
        "#alarmanlageninfo", contentText, as_user="alarmanlage"
    )
    if debug:
        print(rsp)
    while alarmON:
        mqttc.publish("buzzer/wohnzimmer", "6")
        time.sleep(10)
    threadactive = False


def on_connect(mosq, obj, flags, rc):
    print(
        "Connect client: " + mosq._client_id.decode() + ", rc: " + str(rc),
        flush=True,
    )
    mqttc.publish(
        "clientstatus/" + mosq._client_id.decode(), "ONLINE", 0, True
    )

    mqttc.subscribe("alarm/auto/motion", 2)
    mqttc.subscribe("alarm/auto/test", 2)
    mqttc.subscribe("alarm/auto/detected", 2)


def on_disconnect(mosq, obj, rc):
    print(
        "Disconnect client: "
        + str(mosq._client_id, "UTF-8")
        + ", rc: "
        + str(rc),
        flush=True,
    )


def on_message(mosq, obj, msg):
    global alarmActive, alarmON, threadactive, mailstatus
    print(
        "Message received: "
        + msg.topic
        + ", QoS = "
        + str(msg.qos)
        + ", Payload = "
        + msg.payload.decode(),
        flush=True,
    )
    if msg.topic == "alarm/auto/motion":
        alarmActive = msg.payload.decode() == "True"
        # Beim Schalten der Alarmanlage die Bedingung für ALARM zurücksetzen
        alarmON = False
    elif msg.topic == "alarm/auto/test":
        if alarmActive:
            alarmON = True
    elif msg.topic == "alarm/auto/detected":
        if alarmActive:
            alarmON = True
    if alarmActive:
        if alarmON:
            if not threadactive:
                threadactive = True
                thread = threading.Thread(target=background_alarm_activity)
                thread.start()


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
    print("Cleaning up: " + client_id, flush=True)


def cleanup(sig, frame):
    global RUN
    RUN = False
    print("Signal: ", str(sig), " - Cleaning up", client_id, flush=True)
    mqttc.publish("clientstatus/" + client_id, "OFFLINE", 0, True)
    mqttc.loop_stop()
    mqttc.disconnect()


if __name__ == "__main__":

    """ Define the Parser for the command line"""
    parser = argparse.ArgumentParser(description="Alarm Detektor.")
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
        default="MQTT_AutoAlarmdetektor",
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
        "-l",
        "--location",
        help="Ort des Alarmsensors",
        dest="location",
        default="AUTO",
    )
    args = parser.parse_args()
    options = vars(args)
    location = options["location"]
    for sig in (SIGABRT, SIGINT, SIGTERM):
        signal(sig, cleanup)
    client_id = options["clientID"]
    mqttc = paho.Client(client_id=client_id, clean_session=True)
    # Assign event callbacks
    mqttc.on_message = on_message
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
