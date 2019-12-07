#!/usr/bin/env python2
# -*- coding: latin-1 -*-
###
#
# https://www.cl.cam.ac.uk/projects/raspberrypi/tutorials/robot/buttons_and_switches/
# http://sourceforge.net/p/raspberry-gpio-python/wiki/Inputs/
#

import paho.mqtt.client as paho
import time
import atexit
import urlparse
import json
import argparse
from signal import signal, SIGABRT, SIGINT, SIGTERM
from HS110 import tplinkHS110
from datetime import timedelta
import datetime as dt
from slacker import Slacker

###
#
# Provide the following values
#
# maschinenstatusKey='<slackerKey'
# DefaultMQTTPassword = "<mqtt password"
# DefaultMQTTUser = "<mqtt user"

from Security.Slacker import maschinenstatusKey
from Security.MQTT import DefaultMQTTPassword, DefaultMQTTUser

RUN = True
debug = False
client_id = ''
hs110List = []
hs110AllFound = False

###
#
# potential config.py entries

broadcastip = '192.168.1.255'
maschinenstatus = Slacker(maschinenstatusKey)
lowPowerDetection = {
   "Waschmaschine": dict(lowpower=4, period=3, emoji=':potable_water:'),
   "Trockner": dict(lowpower=300, period=2, emoji=':cyclone:'),
   "supercool plug": dict(lowpower=260, period=1, emoji=':signal_strength:')
   }


def tplink_discover(hs110List):
    hs110IPList = tplinkHS110.TplinkHS110.hs110Discover(
        broadcastip, '{"system":{"get_sysinfo":{}}}', debug)
    print('TPLink Discover: ')
    print(hs110IPList)

    for hs110IP in hs110IPList:
        hs110temp = tplinkHS110.TplinkHS110(hs110IP)
        if hs110temp.name in hs110NameList:
            hs110List.append(hs110temp)

    return len(hs110List) == len(hs110NameList)


def tplink_rediscover(hs110):
    hs110IPList = tplinkHS110.TplinkHS110.hs110Discover(
        broadcastip, '{"system":{"get_sysinfo":{}}}', debug)
    print("TPLink Re-Discover: ")
    print(hs110IPList)

    for hs110IP in hs110IPList:
        hs110temp = tplinkHS110.TplinkHS110(hs110IP)
        print(hs110temp)

        if hs110.name == hs110temp.name:
            hs110.ip = hs110temp.ip
            hs110.connected = hs110temp.connected
            hs110.disconnectTime = hs110temp.disconnectTime


def tplink_find(name, hs110List):
    hs110IPList = tplinkHS110.TplinkHS110.hs110Discover(
        broadcastip, '{"system":{"get_sysinfo":{}}}', debug)
    print("TPLink Find: " + name)
    print(hs110IPList)

    for hs110IP in hs110IPList:
        hs110temp = tplinkHS110.TplinkHS110(hs110IP)
        print(hs110temp)

        if hs110temp.name == name:
            hs110List.append(hs110temp)

    return len(hs110List) == len(hs110NameList)


def tplink_set_status(hs110, jmetering):
    if jmetering["emeter"]["get_realtime"]["err_code"] == 0:
        hs110.currentPower = \
            jmetering["emeter"]["get_realtime"]["power"]
        if debug:
            print(hs110.name, hs110.currentPower)

        if hs110.currentPower != 0:
            mqttc.publish('hs110/' + hs110.name + '/power',
                          hs110.currentPower)
        if hs110.currentPower > 0.5:
            if (hs110.currentPower > lowPowerDetection[hs110.name]["lowpower"])\
              and not hs110.systemRunning:
                hs110.startSystem(lowPowerDetection[hs110.name]["lowpower"],
                                  lowPowerDetection[hs110.name]["period"])
                rsp = maschinenstatus.chat.post_message(
                  '#maschinenstatus', hs110.name + ' ist angelaufen!',
                  username='TPLINK HS110',
                  icon_emoji=lowPowerDetection[hs110.name]["emoji"])
                if debug:
                    print(rsp)
            lowhighPeakCount, highlowPeakCount, finishDetected =\
                hs110.calculatePeek()
            if finishDetected:
                rsp = maschinenstatus.chat.post_message(
                    '#maschinenstatus', hs110.name + ' ist fertig!',
                    username='TPLINK HS110',
                    icon_emoji=lowPowerDetection[hs110.name]["emoji"])
                if debug:
                    print(rsp)
                hs110.stopSystem()


def on_connect(mosq, obj, flags, rc):
    global client_id, hs110List, hs110AllFound
    print("Connect client: " + mosq._client_id.decode() + ", rc: " + str(rc))
    mqttc.publish("clientstatus/"+mosq._client_id.decode(), "ONLINE", 0, True)

    mqttc.subscribe("hs110/status", 2)
    hs110AllFound = tplink_discover(hs110List)


def on_disconnect(mosq, obj, rc):
    global hs110List
    print("Disconnect client: " + mosq._client_id.decode() + ", rc: " +
          str(rc))
    del hs110List[:]


def on_message(mosq, obj, msg):
    if debug:
        print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    if msg.topic == 'hs110/status':
        hs110l = []
        for hs110 in hs110List:
            hs110l.append(dict(name=hs110.name, ip=hs110.ip))
            if hs110.name in msg.payload:
                mqttc.publish('hs110/'+hs110.name+'/power', hs110.currentPower)
                mqttc.publish('hs110/'+hs110.name+'/highpower',
                              hs110.highPower)
                mqttc.publish('hs110/'+hs110.name+'/lowpower', hs110.lowPower)
        mqttc.publish('hs110/list', json.dumps(hs110l))


def on_publish(mosq, obj, mid):
    print("mid: " + str(mid))


def on_subscribe(mosq, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_log(mosq, obj, level, string):
    print(string)


@atexit.register
def cleanup_final():
    print("Cleaning up: " + client_id)


def cleanup(sig, frame):
    global RUN
    RUN = False
    print("Signal: ", str(sig), " - Cleaning up", client_id)
    mqttc.publish("clientstatus/" + client_id, "OFFLINE", 0, True)
    mqttc.loop_stop()
    mqttc.disconnect()


if __name__ == '__main__':
    """ Define the Parser for the command line"""
    parser = argparse.ArgumentParser(description='TPLINK Monitor.')
    parser.add_argument('-b', '--broker', help="IP Adress des MQTT Brokers",
                        dest="mqttBroker", default="localhost")
    parser.add_argument('-p', '--port', help="Port des MQTT Brokers",
                        dest="port", default="1883")
    parser.add_argument('-c', '--client-id', help="Id des Clients",
                        dest="clientID", default="MQTT_HS110Monitor")
    parser.add_argument('-u', '--user', help="Broker-Benutzer", dest="user",
                        default=DefaultMQTTUser)
    parser.add_argument('-P', '--password', help="Broker-Password",
                        dest="password", default=DefaultMQTTPassword)
    parser.add_argument('-n', '--name', help="Namen des TPLINK HS110",
                        dest="name", default='["Waschmaschine", "Trockner"]')
    parser.add_argument('-t', '--timeout', help="Schleifentimeout in Minuten",
                        dest="timeout", default=2)

    print(lowPowerDetection)

    args = parser.parse_args()
    options = vars(args)

    timeout = int(options['timeout'])

    hs110NameList = json.loads(options['name'])
#   print hs110NameList

    for sig in (SIGABRT, SIGINT, SIGTERM):
        signal(sig, cleanup)

    client_id = options['clientID']

    mqttc = paho.Client(client_id=client_id, clean_session=True)

# Assign event callbacks
    mqttc.on_message = on_message
    mqttc.on_connect = on_connect
    mqttc.on_disconnect = on_disconnect
#  mqttc.on_publish = on_publish
#  mqttc.on_subscribe = on_subscribe
#  mqttc.on_unsubscribe = on_unsubscribe
#  mqttc.on_log = on_log

    url_str = 'mqtt://'+options['user'] + ':' + options['password'] + '@' +\
              options['mqttBroker'] + ':' + options['port']
    url = urlparse.urlparse(url_str)

    mqttc.username_pw_set(url.username, url.password)
    mqttc.will_set("clientstatus/" + client_id, "OFFLINE", 0, True)
    mqttc.connect_async(url.hostname, url.port, keepalive=60*timeout)

    mqttc.loop_start()

    while RUN:
        for hs110 in hs110List:
            if hs110.connected:
                error, metering = hs110.request(hs110.commands['emeter'])
#                if (debug):
                print(' Error = ', error, metering)
                if error == 0:
                    jmetering = json.loads(metering)
                    tplink_set_status(hs110, jmetering)
                elif error == 1:
                    print(hs110)
                    hs110.connected = False
                    hs110.disconnectTime = dt.datetime.now()
                    print(hs110)
            else:
                if dt.datetime.now() >= hs110.disconnectTime +\
                  timedelta(minutes=timeout*5):
                    hs110.disconnectTime = dt.datetime.now()
                    print(hs110)
                    tplink_rediscover(hs110)
                    print(hs110)

            if not hs110AllFound:
                tempnames = []
                for hs110temp in hs110List:
                    tempnames.append(hs110temp.name)

                for name in hs110NameList:
                    if name not in tempnames:
                        hs110AllFound = tplink_find(name, hs110List)

        time.sleep(timeout * 60)
