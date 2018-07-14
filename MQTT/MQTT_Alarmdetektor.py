#!/usr/bin/env python3
# -*- coding: latin-1 -*-
###
#
# https://www.cl.cam.ac.uk/projects/raspberrypi/tutorials/robot/buttons_and_switches/
# http://sourceforge.net/p/raspberry-gpio-python/wiki/Inputs/
#

import RPi.GPIO as GPIO
import paho.mqtt.client as paho
import time, atexit
from urllib.parse import urlparse
from signal import *
import argparse
import json
import base64

alarmON = False
alarmActive = False
RUN = True
client_id=''

def alarm_detected(channel):
	global alarmON
	alarmON=True
#	print (' ALARM !')

def on_connect(mosq, obj, flags, rc):
	print("Connect client: "+mosq._client_id.decode()+", rc: " + str(rc))
	mqttc.publish("clientstatus/"+mosq._client_id.decode(), "ONLINE", 0, True)

	mqttc.subscribe("alarm/auto/motion", 2)
	mqttc.subscribe("alarm/auto/test", 2)

	GPIO.setmode(GPIO.BCM)
	GPIO.setup(pinin,GPIO.IN)
	GPIO.add_event_detect(pinin, GPIO.RISING, callback=alarm_detected)

def on_disconnect(mosq, obj, rc):
	print("Disconnect client: " + str(mosq._client_id, 'UTF-8') + ", rc: " + str(rc))
	GPIO.cleanup()

def on_message(mosq, obj, msg):
	global alarmActive, alarmON
	print("Message received: "+msg.topic + ", QoS = " + str(msg.qos) + ", Payload = " + msg.payload.decode())
	if msg.topic == 'alarm/auto/motion':
		alarmActive = msg.payload.decode() == 'True'
	elif msg.topic == 'alarm/auto/test':
		alarmON=True

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
	print ("Cleaning up: "+client_id)
	GPIO.setwarnings(False)
	try:
		GPIO.cleanup()
	except Exception as err:
		pass

def cleanup(sig,frame):
	global RUN
	RUN=False
	print ("Signal: ",str(sig)," - Cleaning up", client_id)
	mqttc.publish("clientstatus/"+client_id, "OFFLINE", 0, True)
	mqttc.loop_stop()
	mqttc.disconnect()

if __name__ == '__main__':

	""" Define the Parser for the command line"""
	parser = argparse.ArgumentParser(description='Alarm Detektor.')
	parser.add_argument('-b', '--broker', help="IP Adress des MQTT Brokers", dest="mqttBroker", default="localhost")
	parser.add_argument('-p', '--port', help="Port des MQTT Brokers", dest="port", default="1883")
	parser.add_argument('-c', '--client-id', help="Id des Clients", dest="clientID", default="MQTT_Alarmdetektor")
	parser.add_argument('-u', '--user', help="Broker-Benutzer", dest="user", default='mqttgremm')
	parser.add_argument('-P', '--password', help="Broker-Password", dest="password", default='MdOijT3vGkXD43qAWTJX')
	parser.add_argument('-sp', '--sensor-pin', help="Sensor Pin des Alarm-Detectors", dest="alarmPin", default=4)
	parser.add_argument('-l', '--location', help="Ort des Alarmsensors", dest="location", default='AUTO')
	parser.add_argument('-t', '--timeout', help="Time Out in Sekunden", dest="timeout", default=2)

	args=parser.parse_args()
	options=vars(args)
	pinin= int(options['alarmPin'])
	timeout= int(options['timeout'])
	location= options['location']

	for sig in (SIGABRT, SIGINT, SIGTERM):
		signal(sig, cleanup)

	client_id=options['clientID']

	mqttc = paho.Client(client_id=client_id, clean_session=True)

# Assign event callbacks
	mqttc.on_message = on_message
	mqttc.on_connect = on_connect
	mqttc.on_disconnect = on_disconnect
#	mqttc.on_publish = on_publish
#	mqttc.on_subscribe = on_subscribe
#	mqttc.on_unsubscribe = on_unsubscribe
#	mqttc.on_log = on_log

	url_str = 'mqtt://'+options['user']+':'+options['password']+'@'+options['mqttBroker']+':'+options['port']
	url = urlparse(url_str)

	mqttc.username_pw_set(url.username, url.password)
	mqttc.will_set("clientstatus/"+client_id, "OFFLINE", 0, True)
	mqttc.connect_async(url.hostname, url.port)

	mqttc.loop_start()

	while RUN:
#		print (' alarm = ', alarmON, ' GPIO:', pinin, ' = ', GPIO.input(pinin))
		if alarmActive:
			if  alarmON:
				mqttc.publish("buzzer/wohnzimmer", '6')
				time.sleep(3*timeout)
		else:
			alarmON = False

		time.sleep(2*timeout)

