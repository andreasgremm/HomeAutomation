#!/usr/bin/env python
# -*- coding: latin-1 -*-
import json
import ssl
from http.client import HTTPSConnection

import certifi


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
        self.__context = ssl.create_default_context()
        self.__context.load_verify_locations(cafile=certifi.where())
        try:
            nupnp = HTTPSConnection("discovery.meethue.com",
                                    context=self.__context
                                    )
            nupnp.connect()
            nupnp.request(method="GET", url="/")
            r1 = nupnp.getresponse()
            answer = json.loads(r1.read().decode())
            self.__controller = answer[0]["internalipaddress"]
            print(answer[0]["internalipaddress"])
        except Exception as info:
            print(info)
            self.__controller = controller
        self.__user = user
        """ Speicherung des API-Keys. """
        self.__port = 443
        """ Default Port des Hue-Restful Interface ist 80.
            SSL Port ist 443
        """
        self.__connection = HTTPSConnection(
            self.__controller + ":" + str(self.__port),
            context=ssl._create_unverified_context()
            )

    def __repr__(self):
        return u"<Controller: %s, Connection: %s>" % (
            self.__controller,
            self.__connection
        )

    def connect(self):
        self.__connection.connect()
        return self.__connection

    def disconnect(self):
        self.__connection.close()

    def setUser(self, user):
        self.__user = user

    def getSensorInfo(self, sensorName):
        url = "/api/" + self.__user + "/sensors"
        self.__connection.request(method="GET", url=url)
        r1 = self.__connection.getresponse()
        sensors = json.loads(r1.read().decode())
        for sensor in sensors.items():
            sensorKey, sensorValue = sensor
            if sensorValue["name"] == sensorName:
                return sensor
        print("Hue: Sensor not found")
        return (-1, {})

    def getSceneInfo(self, sceneNamePart, numLights):
        url = "/api/" + self.__user + "/scenes"
        self.__connection.request(method="GET", url=url)
        r1 = self.__connection.getresponse()
        scenes = json.loads(r1.read().decode())
        for scene in scenes.items():
            sceneKey, sceneValue = scene
            if sceneNamePart in sceneValue["name"]:
                # fix: same scene name
                if len(sceneValue["lights"]) == numLights:
                    return scene
        print("Hue: Scene not found")
        return (-1, {})

    def setScene(self, scene):
        url = "/api/" + self.__user + "/groups/0/action"
        self.__connection.request("PUT", url, json.dumps({"scene": scene}))
        r1 = self.__connection.getresponse()
        status = json.loads(r1.read().decode())
        return status

    def getDaylightStatus(self):
        sensorkey, daylight = self.getSensorInfo("Daylight")
        if int(sensorkey) >= 1:
            return daylight["state"]["daylight"]
        return False

    def setLampsOff(self):
        url = "/api/" + self.__user + "/groups/0/action"
        self.__connection.request("PUT", url, json.dumps({"on": False}))
        r1 = self.__connection.getresponse()
        status = json.loads(r1.read().decode())
        return status

    def getLampInfo(self, lamp):
        #       print('Lampinfo started')
        url = "/api/" + self.__user + "/lights/" + str(lamp)
        self.__connection.request(method="GET", url=url)
        r1 = self.__connection.getresponse()
        #       print ('Lamp: HTTP Response Code: {0}'.format(r1.status))
        light = json.loads(r1.read().decode())
        return light

    def isAnyLightOn(self):
        url = "/api/" + self.__user + "/groups/0"
        self.__connection.request(method="GET", url=url)
        r1 = self.__connection.getresponse()
        anylight = json.loads(r1.read().decode())
        return anylight["state"]["any_on"]

    def lampOnOffStatus(self, lamp):
        # print('Lamp on - off info started')
        lightInfo = self.getLampInfo(lamp)
        status = lightInfo["state"]["on"]
        return status

    def setLampStatus(self, lamp, data):
        url = "/api/" + self.__user + "/lights/" + str(lamp) + "/state"
        self.__connection.request("PUT", url, data)
        r1 = self.__connection.getresponse()
        status = json.loads(r1.read().decode())
        return status

    def setLampOn(self, lamp):
        data_to_update = json.dumps({"on": True})
        return self.setLampStatus(lamp, data_to_update)

    def setLampOff(self, lamp):
        data_to_update = json.dumps({"on": False})
        return self.setLampStatus(lamp, data_to_update)

    def setLampAlarm(self, lamp, hue):
        data_to_update = json.dumps(
            {"hue": hue, "on": True, "bri": 200, "alert": "select"}
        )
        return self.setLampStatus(lamp, data_to_update)
