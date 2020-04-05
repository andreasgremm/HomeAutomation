#!/usr/bin/env python3
# -*- coding: latin-1 -*-
import argparse
import atexit

from signal import SIGABRT, SIGINT, SIGTERM, signal
from urllib.parse import urlparse

import paho.mqtt.client as paho
from Security.MQTT import DefaultMQTTPassword, DefaultMQTTUser

from MQTT_Xbee.XbeeSender import XbeeSender
from XbeeS2.XbeeS2 import (
    XbeeS2,
    frameStartDelimiter,
    dataSampleRXIndicator,
    ATCommandResponse,
    RemoteCommandResponse,
    modemStatus,
)

RUN = True
client_id = ""
debug = False


@atexit.register
def cleanup_final():
    print("Cleaning up: " + client_id)


def cleanup(sig, frame):
    global RUN, session
    print("Signal: ", str(sig), " - Cleaning up", client_id)
    RUN = False
    mqttc.publish("clientstatus/" + client_id, "OFFLINE", 0, True)
    mqttc.loop_stop()
    mqttc.disconnect()


def on_connect(mosq, obj, flags, rc):
    global XbeeSender
    print("Connect client: " + mosq._client_id.decode() + ", rc: " + str(rc))
    XbeeSender.setMQTTonline(True)
    mqttc.publish("clientstatus/" + client_id, "ONLINE", 0, True)


def on_disconnect(mosq, obj, rc):
    global XbeeSender
    print(
        "Disconnect client: " + mosq._client_id.decode() + ", rc: " + str(rc)
    )
    XbeeSender.setMQTTonline(False)


def on_message(mosq, obj, msg):
    print(
        "Message received: "
        + msg.topic
        + ", QoS = "
        + str(msg.qos)
        + ", Payload = "
        + str(msg.payload)
    )


def on_publish(mosq, obj, mid):
    print("mid: " + str(mid))


def on_subscribe(mosq, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_unsubscribe(mosq, obj, mid):
    print("UNSubscribed: " + str(mid))


def on_log(mosq, obj, level, string):
    print(string)


if __name__ == "__main__":
    """ Define the Parser for the command line"""
    parser = argparse.ArgumentParser(description="Xbee S2 IO Controller")
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
        default="MQTT_ReadXbeeSerial",
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
        "-tty",
        "--serial-input",
        help="Serial Interface",
        dest="serialInput",
        default="/dev/ttyAMA0",
    )
    args = parser.parse_args()
    options = vars(args)

    Xbee = XbeeS2(options["serialInput"])

    Xbee.open()
    print(Xbee, flush=True)

    somethingWrong = False

    for sig in (SIGABRT, SIGINT, SIGTERM):
        signal(sig, cleanup)

    client_id = options["clientID"]

    mqttc = paho.Client(client_id=client_id, clean_session=True)
    XbeeSender.MQTTC(mqttc)

    # Assign event callbacks
    # 	mqttc.on_message = on_message
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
    mqttc.loop_start()

    Xbee.networkDiscovery()

    while RUN:
        incoming = Xbee.read()

        if incoming == frameStartDelimiter:
            frameLength = Xbee.frameLength()
            frame = Xbee.read(frameLength)

            validChecksum = Xbee.verifyChecksum(frame, Xbee.read())

            if validChecksum:

                if frame[0] == dataSampleRXIndicator:
                    sender = Xbee.getSender(frame)
                    actsender = XbeeSender.returnXbee(sender)
                    actsender.setLastContact()
                    print(" DataSample: ", actsender, flush=True)
                    print(" ", flush=True)
                    if actsender.returnSenderNI() is None:
                        Xbee.networkDiscovery()
                    else:
                        valueSaved = actsender.handleFunction(
                            frame, Xbee
                        )
                        if valueSaved:
                            Xbee.getRSSI(actsender.returnSenderID())

                elif frame[0] == modemStatus:
                    if frame[1] == 0:
                        print("Error: Hardware Reset ", flush=True)
                    elif frame[1] == 6:
                        print("Info: Coordinator started ", flush=True)
                    Xbee.printFrame(frame)
                elif frame[0] == ATCommandResponse:
                    if frame[4] != 0:
                        print(" AT Command Error, Frame = ", flush=True)
                        Xbee.printFrame(frame)
                    elif chr(frame[2]) + chr(frame[3]) == "ND":
                        print(" ND Command Response, Frame = ", flush=True)
                        Xbee.printFrame(frame)
                        sender = Xbee.getSenderATNDResponse(frame)
                        actsender = XbeeSender.returnXbee(sender)
                        actsender.setSenderNI(
                            Xbee.getSenderNetID(frame, frameLength)
                        )
                        actsender.setLastContact()

                elif frame[0] == RemoteCommandResponse:
                    if frame[14] != 0:
                        print(" Remote Command Error, Frame = ", flush=True)
                        Xbee.printFrame(frame)
                    elif chr(frame[12]) + chr(frame[13]) == "DB":
                        sender = Xbee.getSenderRCDBResponse(frame)
                        actsender = XbeeSender.returnXbee(sender)
                        actsender.setLastContact()
                        print(" Remote DB Answer: ", actsender, flush=True)
                        print(" ", flush=True)
                        Xbee.printFrame(frame)
                        RSSIValue = Xbee.getRSSIValue(frame, frameLength)
                        actsender.setLastRSSIValue(RSSIValue, session)

                # check for other Frames
                else:
                    print(" Other Frame, Frame = ", flush=True)
                    Xbee.printFrame(frame)
            else:
                print(" Checksum-Error, Frame = ", flush=True)
                Xbee.printFrame(frame)
        else:
            print(" Incoming: Input not expected:", flush=True)
            Xbee.printFrame(incoming)
