#!/usr/bin/env python3
# -*- coding: latin-1 -*-

import argparse
import atexit
import datetime as dt
import json
import threading
import time
from signal import SIGABRT, SIGINT, SIGTERM, signal
from urllib.parse import urlparse

import paho.mqtt.client as paho
from Mail import mail
from Security.MotionDetector import mail_receiver
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

alarmActive = False
alarmON = False
noMotionTime = dt.datetime.now()
setLampOwn = False
lampstatus = False
daylightstatus = False
lamp = 0
threadactive = False

hueControlData = {"on": True, "bri": 254, "hue": 34392}
client_id = ""
debug = False


def background_alarm_activity():
    global alarmON, lampstatus, setLampOwn, noMotionTime, threadactive, timeout
    if debug:
        print("Alarm started")
    if not lampstatus:
        mqttc.publish("hue/lamp/" + str(lamp), "status")
    mqttc.publish("kamera/wohnzimmer", "EIN")
    alarmtime = str(dt.datetime.now())
    contentText = (
        " Bewegung erkannt um: "
        + alarmtime
        + "\n Siehe: https://familie-gremm.synology.me/camera/"
    )
    contentHtml = (
        "<head></head><body><h2>Bewegung erkannt um: "
        + alarmtime
        + "</h2><br>Siehe: "
        + '<a href="http://andreas-gremm.selfhost.bz:8080">Kamera</a>'
        + "</body></html>"
    )
    rsp = slack.chat.post_message(
        "#alarmanlageninfo", contentText, as_user="alarmanlage"
    )
    if debug:
        print(rsp)
    for receiver in mail_receiver:
        mail.sendmail(
            receiver, " Bewegung erkannt!", [contentText, contentHtml],
        )

    while dt.datetime.now() <= (noMotionTime + dt.timedelta(minutes=timeout)):
        time.sleep(timeout)

    mqttc.publish("kamera/wohnzimmer", "AUS")
    if setLampOwn:
        mqttc.publish("hue/lamp/" + str(lamp), "off")
        setLampOwn = False
    lampstatus = False
    threadactive = False
    if debug:
        print("Alarm stopped")


def on_connect(mosq, obj, flags, rc):
    if debug:
        print(
            "Connect client: " + mosq._client_id.decode() + ", rc: " + str(rc),
            flush=True,
            )
    mqttc.publish(
        "clientstatus/" + mosq._client_id.decode(), "ONLINE", 0, True
    )

    mqttc.subscribe("hue/lampstatus/" + str(lamp), 2)
    mqttc.subscribe("alarm/wohnzimmer/motion", 2)
    mqttc.subscribe("alarm/wohnzimmer/test", 2)
    mqttc.subscribe("alarm/wohnzimmer/detected", 2)
    mqttc.subscribe("motion/wohnzimmer", 2)


def on_disconnect(mosq, obj, rc):
    print(
        "Disconnect client: " + mosq._client_id.decode() + ", rc: " + str(rc),
        flush=True,
    )


def on_message(mosq, obj, msg):
    global motion, noMotionTime, alarmActive, threadactive
    if debug:
        print(
            "Message received (on_message): "
            + msg.topic
            + ", QoS = "
            + str(msg.qos)
            + ", Payload = "
            + msg.payload.decode(),
            flush=True
        )
    if msg.topic == "alarm/wohnzimmer/motion":
        alarmActive = msg.payload.decode() == "True"
        # Beim Schalten der Alarmanlage die Bedingung für ALARM zurücksetzen
        alarmON = False
    elif msg.topic == "alarm/wohnzimmer/test":
        if alarmActive:
            alarmON = True
            noMotionTime = dt.datetime.now()
    elif msg.topic == "alarm/wohnzimmer/detected":
        if alarmActive:
            if msg.payload.decode() == "1":
                alarmON = True
                noMotionTime = dt.datetime.now()
            else:
                alarmON = False
    if alarmActive:
        if alarmON:
            if not threadactive:
                threadactive = True
                thread = threading.Thread(target=background_alarm_activity)
                thread.start()


def manage_light(mosq, obj, msg):
    global lampstatus, setLampOwn, threadactive
    if debug:
        print(
            "Message received (manage_light): "
            + msg.topic
            + ", QoS = "
            + str(msg.qos)
            + ", Payload = "
            + msg.payload.decode(),
            flush=True
        )
    lampstatus = msg.payload.decode() == "True"
    if threadactive and not lampstatus:
        lampControl = {"lamp": lamp, "data": hueControlData}
        mqttc.publish("hue/control", json.dumps(lampControl))
        setLampOwn = True


def motion_detected(mosq, obj, msg):
    global alarmON, noMotionTime, alarmActive, threadactive
    if debug:
        print(
            "Message received (motion_detected): "
            + msg.topic
            + ", QoS = "
            + str(msg.qos)
            + ", Payload = "
            + msg.payload.decode(),
            flush=True
        )
    if alarmActive:
        if msg.payload.decode() == "True":
            alarmON = True
            noMotionTime = dt.datetime.now()
            if not threadactive:
                threadactive = True
                thread = threading.Thread(target=background_alarm_activity)
                thread.start()
        else:
            alarmON = False


def on_publish(mosq, obj, mid):
    print("mid: " + str(mid))


def on_subscribe(mosq, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_log(mosq, obj, level, string):
    print(string)


@atexit.register
def cleanup_final():
    print("Cleaning up: " + client_id, flush=True)


def cleanup(sig, frame):
    print("Signal: ", str(sig), " - Cleaning up", client_id, flush=True)
    mqttc.publish("clientstatus/" + client_id, "OFFLINE", 0, True)
    mqttc.loop_stop()
    mqttc.disconnect()


if __name__ == "__main__":

    """ Define the Parser for the command line"""
    parser = argparse.ArgumentParser(description="Motion Alarm.")
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
        default="MQTT_Motiondetektor",
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
        "-l", "--lamp", help="Lampen Nummer", dest="lamp", default=1
    )
    parser.add_argument(
        "-t",
        "--timeout",
        help="Time Out in Minuten \
         bis die Ueberwachung wieder abgeschaltet wird",
        dest="timeout",
        default=2,
    )

    args = parser.parse_args()
    options = vars(args)

    lamp = int(options["lamp"])
    timeout = int(options["timeout"])

    for sig in (SIGABRT, SIGINT, SIGTERM):
        signal(sig, cleanup)

    client_id = options["clientID"]

    mqttc = paho.Client(client_id=client_id, clean_session=True)

    # Assign event callbacks
    mqttc.on_message = on_message
    mqttc.message_callback_add("hue/lampstatus/" + str(lamp), manage_light)
    mqttc.message_callback_add("motion/wohnzimmer", motion_detected)
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
