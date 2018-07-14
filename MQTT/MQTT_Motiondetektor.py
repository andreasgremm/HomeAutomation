#!/usr/bin/env python
# -*- coding: latin-1 -*-
###
#
# https://www.cl.cam.ac.uk/projects/raspberrypi/tutorials/robot/buttons_and_switches/
# http://sourceforge.net/p/raspberry-gpio-python/wiki/Inputs/
#

import RPi.GPIO as GPIO
import paho.mqtt.client as paho
import time, os, atexit
from urllib.parse import urlparse
import json
import argparse
import subprocess
from datetime import timedelta
import datetime as dt
from email.mime.text import MIMEText
import smtplib
from mail import mail
from MQTT_Motiondetektor_config import *
from http.client import HTTPConnection
from signal import *

motion = False
nomotion = False
noMotionTime=dt.datetime.now()
setLampOwn=False
alarmActive=False
lampstatus=False
mailstatus=False
daylightstatus=False
lamp=0
RUN = True
hueControlData={"on":True, "bri":254, "hue": 34392}
client_id=''

def motion_detected(channel):
	global motion, nomotion, noMotionTime
	if GPIO.input(channel):
		if alarmActive:
			motion=True
		nomotion=False
		mqttc.publish("motion/wohnzimmer", "True", 0, True)
		print('Motion detected on channel %s'%channel)
	else:
		noMotionTime = dt.datetime.now()
		nomotion=True
		mqttc.publish("motion/wohnzimmer", "False", 0, True)
		print('NO-Motion detected on channel %s'%channel)

def on_connect(mosq, obj, flags, rc):
	print("Connect client: "+mosq._client_id.decode()+", rc: " + str(rc))
	mqttc.publish("clientstatus/"+mosq._client_id.decode(), "ONLINE", 0, True)

	mqttc.subscribe("hue/lampstatus/"+str(lamp), 2)
	mqttc.subscribe("alarm/wohnzimmer/motion", 2)

	GPIO.setmode(GPIO.BCM)
	GPIO.setup(pinin,GPIO.IN)
	GPIO.add_event_detect(pinin, GPIO.BOTH, callback=motion_detected, bouncetime=300)

def on_disconnect(mosq, obj, rc):
	print("Disconnect client: " + mosq._client_id.decode() + ", rc: " + str(rc))
	GPIO.cleanup()

def on_message(mosq, obj, msg):
	global lampstatus, setLampOwn, alarmActive
#	print(msg.topic + " " + str(msg.qos) + " " + msg.payload.decode())
	if msg.topic == 'hue/lampstatus/'+str(lamp):
		lampstatus= msg.payload.decode() == 'True'
		if motion and not lampstatus:
			lampControl={"lamp":lamp, "data":hueControlData}
			mqttc.publish('hue/control', json.dumps(lampControl))
			setLampOwn=True
	elif msg.topic == 'alarm/wohnzimmer/motion':
		alarmActive = msg.payload.decode() == 'True'

def on_publish(mosq, obj, mid):
	print("mid: " + str(mid))

def on_subscribe(mosq, obj, mid, granted_qos):
	print("Subscribed: " + str(mid) + " " + str(granted_qos))

def on_log(mosq, obj, level, string):
	print(string)

@atexit.register
def cleanup():
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

def systemStatus():
	mjpg_status=subprocess.call(["pidof", "mjpg_streamer"])
	return (mjpg_status)

if __name__ == '__main__':

	""" Define the Parser for the command line"""
	parser = argparse.ArgumentParser(description='Motion Alarm.')
	parser.add_argument('-b', '--broker', help="IP Adress des MQTT Brokers", dest="mqttBroker", default="localhost")
	parser.add_argument('-p', '--port', help="Port des MQTT Brokers", dest="port", default="1883")
	parser.add_argument('-c', '--client-id', help="Id des Clients", dest="clientID", default="MQTT_Motiondetektor")
	parser.add_argument('-u', '--user', help="Broker-Benutzer", dest="user", default='MQTT User')
	parser.add_argument('-P', '--password', help="Broker-Password", dest="password", default='MQTT PASSWORD')
	parser.add_argument('-sp', '--sensor-pin', help="Sensor Pin des Bewegungsmelders", dest="motionPin", default=23)
	parser.add_argument('-l', '--lamp', help="Lampen Nummer", dest="lamp", default=1)
	parser.add_argument('-t', '--timeout', help="Time Out in Minuten bis die Ueberwachung wieder abgeschaltet wird", dest="timeout", default=2)

	args=parser.parse_args()
	options=vars(args)

	pinin= int(options['motionPin'])
	lamp= int(options['lamp'])
	timeout= int(options['timeout'])

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
		if motion and alarmActive:
			if not lampstatus:
				mqttc.publish("hue/lamp/"+str(lamp), 'status')
			mjpg_status=systemStatus()

			if mjpg_status != 0:
				mjpg_status=subprocess.call(["systemctl", "start", mjpg])

			if not mailstatus:
				contentText=' Bewegung erkannt um: ' + str(dt.datetime.now()) +'\n Siehe: http://andreas-gremm.selfhost.bz:8080'
				contentHtml='<head></head><body><h2>Bewegung erkannt um: ' + str(dt.datetime.now()) + '</h2><br>Siehe: <a href="http://andreas-gremm.selfhost.bz:8080">Kamera</a></body></html>'

				for receiver in mail_receiver:
					mail.sendmail(receiver,' Bewegung erkannt!', [contentText, contentHtml])
				mailstatus = True

			motion = False

		if nomotion:
			#print dt.datetime.now(), noMotionTime+timedelta(minutes=timeout)
			if dt.datetime.now() >= noMotionTime + timedelta(minutes=timeout):
				mjpg_status=systemStatus()

				if mjpg_status == 0:
					mjpg_status=subprocess.call(["systemctl", "stop", mjpg])

				if setLampOwn:
					mqttc.publish('hue/lamp/'+str(lamp), 'off')
					setLampOwn = False

				nomotion = False
				mailstatus = False
				lampstatus = False

		time.sleep(2)
