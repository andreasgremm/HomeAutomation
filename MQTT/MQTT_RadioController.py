#!/usr/bin/env python3
# -*- coding: latin-1 -*-

import argparse
import atexit
import json
import os
import time
from signal import *
from urllib.parse import urlparse

import paho.mqtt.client as paho
from FSAPI.fsapi import FSAPI
from FSAPI.ssdp import *
from Security.FSAPI import *
from Security.MQTT import *

radioKey = 0
defaultService = ""
volumeList = [
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "10",
    "11",
    "12",
    "13",
    "14",
    "15",
]

# Define event callbacks
def on_connect(mosq, obj, flags, rc):
    print("Connect client: " + mosq._client_id.decode() + ", rc: " + str(rc))
    mqttc.publish(
        "clientstatus/" + mosq._client_id.decode(), "ONLINE", 0, True
    )
    mqttc.subscribe([("radio/power", 2), ("radio/volume", 2)])


def on_disconnect(mosq, obj, rc):
    print(
        "Disconnect client: " + mosq._client_id.decode() + ", rc: " + str(rc)
    )


def on_message(mosq, obj, msg):
    rstatus = None

    print(
        "Message received: "
        + msg.topic
        + ", QoS = "
        + str(msg.qos)
        + ", Payload = "
        + msg.payload.decode()
    )
    payload = msg.payload.decode()

    with FSAPI(defaultService, radioKey) as fs:

        if msg.topic == "radio/power":

            if payload == "on":
                fs.power = True
            elif payload == "off":
                fs.power = False
            elif payload == "?":
                mqttc.publish("radio/status/power", str(fs.power), 0, True)

        elif msg.topic == "radio/volume":
            oldvolume = int(fs.volume)

            if payload == "<":
                fs.volume = str(oldvolume - 1)
            elif payload == "<<":
                fs.volume = str(oldvolume - 2)
            elif payload == ">":
                fs.volume = str(oldvolume + 1)
            elif payload == ">>":
                fs.volume = str(oldvolume + 2)
            elif payload == "?":
                mqttc.publish("radio/status/volume", str(fs.volume), 0, True)
            elif payload == "??":
                mqttc.publish("radio/status/mute", str(fs.mute), 0, True)
            elif payload == "0":
                fs.mute = True
            elif payload == "*":
                fs.mute = False
            elif payload in volumeList:
                fs.volume = payload


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
    try:
        HueController.disconnect()
    except Exception as err:
        pass


def cleanup(sig, frame):
    print("Signal: ", str(sig), " - Cleaning up", client_id)
    mqttc.publish("clientstatus/" + client_id, "OFFLINE", 0, True)
    mqttc.disconnect()


if __name__ == "__main__":

    """ Define the Parser for the command line"""
    parser = argparse.ArgumentParser(description="MQTT Hue-Controller.")
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
        default="MQTT_Webradio",
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
        "-rk",
        "--radio-key",
        help="Key fuer das Webradio",
        dest="radioKey",
        default=DefaultFSAPIKey,
    )
    parser.add_argument(
        "-rh",
        "--radio-host",
        help="Hostname/IP fuer das Webradio",
        dest="radioHost",
        default="192.168.1.104",
    )

    args = parser.parse_args()
    options = vars(args)

    for sig in (SIGABRT, SIGINT, SIGTERM):
        signal(sig, cleanup)

    client_id = options["clientID"]
    radioKey = options["radioKey"]
    defaultService = "http://" + options["radioHost"] + ":80/device"

    mqttc = paho.Client(client_id=client_id, clean_session=True)

    # Assign event callbacks
    mqttc.on_message = on_message
    mqttc.on_connect = on_connect
    mqttc.on_disconnect = on_disconnect
    #   mqttc.on_publish = on_publish
    #   mqttc.on_subscribe = on_subscribe
    #   mqttc.on_unsubscribe = on_unsubscribe
    #   mqttc.on_log = on_log

    # Parse CLOUDMQTT_URL (or fallback to localhost)
    # mqtt://user:password@server:port
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

    services = discover("urn:schemas-frontier-silicon-com:undok:fsapi:1")
    if not len(services):
        print("No device server found on network")
    else:
        print('Found device server at "%s".' % (services[0].location))
        defaultService = services[0].location

    # Connect
    mqttc.username_pw_set(url.username, url.password)
    mqttc.will_set("clientstatus/" + client_id, "OFFLINE", 0, True)
    mqttc.connect_async(url.hostname, url.port)

    mqttc.loop_forever(retry_first_connection=True)
