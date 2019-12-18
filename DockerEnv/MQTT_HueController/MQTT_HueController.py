#!/usr/bin/env python3
# -*- coding: latin-1 -*-

import argparse
import atexit
import json
from signal import signal, SIGABRT, SIGINT, SIGTERM
from urllib.parse import urlparse

import paho.mqtt.client as paho
from Hue import Hue
from Security.Hue import DefaultHueUser
from Security.MQTT import DefaultMQTTUser, DefaultMQTTPassword

lamp_status = {
    "on": ["1", "on", "True", "yes"],
    "off": ["0", "off", "False", "no"],
    "status": ["?", "status", "help"],
    "info": ["info"],
}
client_id = ""
debug = False


# Define event callbacks
def on_connect(mosq, obj, flags, rc):
    print("Connect client: " + mosq._client_id.decode() + ", rc: " + str(rc),
          flush=True)
    mqttc.publish(
        "clientstatus/" + mosq._client_id.decode(), "ONLINE", 0, True
    )
    mqttc.subscribe(
        [
            ("hue/control", 2),
            ("hue/lamp/#", 2),
            ("hue/scene/#", 2),
            ("hue/alarm/#", 2),
        ]
    )


def on_disconnect(mosq, obj, rc):
    print(
        "Disconnect client: " + mosq._client_id.decode() + ", rc: " + str(rc),
        flush=True
    )


def on_message(mosq, obj, msg):
    rstatus = None
    try:
        HueConnection = HueController.connect()
        if (debug):
            print(HueConnection)
    except Exception as e:
        print(e, flush=True)
    print(
        "Message received: "
        + msg.topic
        + ", QoS = "
        + str(msg.qos)
        + ", Payload = "
        + msg.payload.decode(),
        flush=True
    )

    if msg.topic == "hue/control":
        json_load = "Fehler"
        try:
            json_load = json.loads(msg.payload.decode())
        except Exception as err:
            print(err)

        if "scene" in json_load:
            try:
                sid, val = HueController.getSceneInfo(json_load["scene"], 3)
                rstatus = HueController.setScene(sid)
            except Exception as err:
                print(err)
        elif "lamp" in json_load:
            try:
                rstatus = HueController.setLampStatus(
                    json_load["lamp"], json.dumps(json_load["data"])
                )
            except Exception as err:
                print(err)
        if "all" in json_load:
            if json_load["all"] == "off":
                try:
                    rstatus = HueController.setLampsOff()
                except Exception as err:
                    print(err)
        if "any" in json_load:
            if json_load["any"] == "on":
                try:
                    rstatus = HueController.isAnyLightOn()
                    mqttc.publish("hue/any", str(rstatus), 0, False)
                except Exception as err:
                    print(err)

    elif "hue/alarm" in msg.topic:
        lamp = msg.topic.lstrip("hue/alarm/")

        try:
            rstatus = HueController.setLampAlarm(lamp, int(msg.payload))
        except Exception as err:
            print(err)

    elif "hue/lamp" in msg.topic:
        lamp = msg.topic.lstrip("hue/lamp/")

        if msg.payload.decode() in lamp_status["on"]:
            try:
                rstatus = HueController.setLampOn(lamp)
            except Exception as err:
                print(err)
        elif msg.payload.decode() in lamp_status["off"]:
            try:
                rstatus = HueController.setLampOff(lamp)
            except Exception as err:
                print(err)
        elif msg.payload.decode() in lamp_status["status"]:
            try:
                rstatus = HueController.lampOnOffStatus(lamp)
                mqttc.publish(
                    "hue/lampstatus/" + str(lamp), str(rstatus), 0, False
                )
            except Exception as err:
                print(err)
        elif msg.payload.decode() in lamp_status["info"]:
            try:
                rstatus = HueController.getLampInfo(lamp)
                mqttc.publish(
                    "hue/lampinfo/" + str(lamp), str(rstatus), 0, False
                )
            except Exception as err:
                print(err)

    elif "hue/scene" in msg.topic:
        sceneStatus = msg.topic.lstrip("hue/scene/")

        if sceneStatus in lamp_status["on"]:
            try:
                sid, val = HueController.getSceneInfo(msg.payload.decode(), 3)
                rstatus = HueController.setScene(sid)
            except Exception as err:
                print(err)

        if sceneStatus in lamp_status["off"]:
            try:
                rstatus = HueController.setLampsOff()
            except Exception as err:
                print(err)
    HueController.disconnect()


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
        default="MQTT_Hue",
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
        "-hc",
        "--hue-controller",
        help="IP Adress des Hue Controllers",
        dest="hueController",
        default="192.168.1.138",
    )
    parser.add_argument(
        "-hu",
        "--hue-user",
        help="User fuer den Hue Controller",
        dest="hueUser",
        default=DefaultHueUser,
    )

    args = parser.parse_args()
    options = vars(args)
    for sig in (SIGABRT, SIGINT, SIGTERM):
        signal(sig, cleanup)
    client_id = options["clientID"]
    mqttc = paho.Client(client_id=client_id, clean_session=False)
    HueController = Hue.Hue(options["hueController"], options["hueUser"])
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
    # Connect MQTT
    mqttc.username_pw_set(url.username, url.password)
    mqttc.will_set("clientstatus/" + client_id, "OFFLINE", 0, True)
    mqttc.connect_async(url.hostname, url.port)
    mqttc.loop_forever(retry_first_connection=True)
