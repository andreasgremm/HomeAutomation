#!/usr/bin/env python
# -*- coding: latin-1 -*-
from http.client import HTTPConnection, HTTPSConnection
import json

class Hue(object):
	"""
	Steuerung der Phillips Hue Lampen ueber HTTP-Restful.
	"""

	def __init__(self, controller, user):
		"""
		Auffinden der Hue durch nupnp oder Nutzung der Uebergabeparameter.

		controller: IP-Adresse des Hue-Controllers
		user: API-Key (muss vorab in der Hue definiert sein)
		"""
		try:
			nupnp = HTTPSConnection("www.meethue.com")
			nupnp.connect()
			nupnp.request(method='GET', url='/api/nupnp')
			r1=nupnp.getresponse()
			answer = json.loads(r1.read().decode())
			self.__controller=answer[0]['internalipaddress']
		except:
			self.__controller=controller
		self.__user=user
		""" Speicherung des API-Keys. """
		self.__port=80
		""" Default Port des Hue-Restful Interface ist 80. """
		self.__connection=None

	def __repr__(self):
		return u'<Controller: %s, Connection: %s, User: %s>' % (self.__controller, self.__connection, self.__user)
	
	def isConnected(self):
		return self.__connection

	def setUser(self, user):
		self.__user=user

	def connect(self):
		self.__connection = HTTPConnection(self.__controller +':'+ str(self.__port))
		self.__connection.connect()
		return self.__connection

	def disconnect(self):
		self.__connection.close()

	def getSensorInfo(self, sensorName):
		url='/api/'+self.__user+'/sensors'
		self.__connection.request(method='GET', url=url)
		r1=self.__connection.getresponse()
		sensors=json.loads(r1.read().decode())
		for sensor in sensors.items():
			sensorKey, sensorValue=sensor
			if sensorValue['name'] == sensorName:
				return sensor
		print ("Hue: Sensor not found")
		return (-1,{})

	def getSceneInfo(self, sceneNamePart,numLights):
		url='/api/'+self.__user+'/scenes'
		self.__connection.request(method='GET', url=url)
		r1=self.__connection.getresponse()
		scenes=json.loads(r1.read().decode())
		for scene in scenes.items():
			sceneKey, sceneValue=scene
			if sceneNamePart in sceneValue['name']:
				# fix: same scene name 
				if len(sceneValue['lights']) == numLights:
					return scene
		print ("Hue: Scene not found")
		return (-1,{})

	def setScene(self, scene):
		url='/api/'+self.__user+'/groups/0/action'
		self.__connection.request('PUT',url, json.dumps({"scene":scene}))
		r1=self.__connection.getresponse()
		status=json.loads(r1.read().decode())
		return status

	def getDaylightStatus(self):
		sensorkey,daylight=self.getSensorInfo('Daylight')
		if sensorkey >=1:
			return daylight['state']['daylight']
		return False

	def setLampsOff(self):
		url='/api/'+self.__user+'/groups/0/action'
		self.__connection.request('PUT',url, json.dumps({"on":False}))
		r1=self.__connection.getresponse()
		status=json.loads(r1.read().decode())
		return status

	def getLampInfo(self, lamp):
#		print('Lampinfo started')
		url='/api/'+self.__user+'/lights/'+str(lamp)
		self.__connection.request(method='GET', url=url)
		r1=self.__connection.getresponse()
#		print ('Lamp: HTTP Response Code: {0}'.format(r1.status))
		light=json.loads(r1.read().decode())
		return light

	def isAnyLightOn(self):
		url='/api/'+self.__user+'/groups/0'
		self.__connection.request(method='GET', url=url)
		r1=self.__connection.getresponse()
		anylight=json.loads(r1.read().decode())
		return anylight['state']['any_on']

	def lampOnOffStatus(self, lamp):
		#print('Lamp on - off info started')
		lightInfo=self.getLampInfo(lamp)
		status = lightInfo['state']['on']
		return status

	def setLampStatus(self, lamp, data):
		url='/api/'+self.__user+'/lights/'+str(lamp)+'/state'
		self.__connection.request('PUT',url, data)
		r1=self.__connection.getresponse()
		status=json.loads(r1.read().decode())
		return status

	def setLampOn(self, lamp):
		data_to_update = json.dumps({"on":True})
		return self.setLampStatus(lamp, data_to_update)

	def setLampOff(self, lamp):
		data_to_update = json.dumps({"on":False})
		return self.setLampStatus(lamp, data_to_update)

	def setLampAlarm(self, lamp, hue):
		data_to_update = json.dumps({ "hue": hue, "on": True, "bri": 200, "alert":"select" })
		return self.setLampStatus(lamp, data_to_update)
