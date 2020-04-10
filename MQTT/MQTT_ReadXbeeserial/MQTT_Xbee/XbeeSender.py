import time

TemperaturSensoren = {"Wohnzimmer": "A3", "AUTO": "A3"}
LichtSensoren = {"Wohnzimmer": "A2", "AUTO": "A2"}
SpannungsSensoren = {"AUTO": "A1"}
KlatschSchalter = {"Wohnzimmer": "D1"}
BewegungsMelder = {"Wohnzimmer": "D4", "AUTO": "D4"}

BewegungOut = {"Wohnzimmer": "D2", "AUTO": "D4"}
KlatschOut = {"Wohnzimmer": "D1"}


def actualTime():
    return time.time()


# get the current temp from a list of voltage readings
def get_tempature(data, format="C"):

    # now calculate the proper mv
    # we are using a 3.3v usb explorer so the formula is slightly different
    tempature = (data / 0.76) / 10.0 - 50.0 * 0.76

    if format == "F":
        # convert to farenheit
        tempature = (tempature * 1.8) + 32

    return tempature


class XbeeSender(object):
    __xbeeList = []
    __temperaturIntervall = 60 * 2
    __lichtIntervall = 60 * 2
    __spannungsIntervall = 60 * 5
    __initIntervall = 60 * 10
    __mqttc = None
    __mqttIsOnline = False

    def __init__(self, sender):
        self.__sender = sender
        self.__function = None
        self.__ni = None
        self.__regtime = actualTime()
        self.__lastcontact = actualTime()
        self.__lastValueSave = {}
        self.__lastRSSIValue = 0
        XbeeSender.__xbeeList.append(self)
        print("-----")
        print(XbeeSender.__xbeeList)
        print("", flush=True)

    def setLastRSSIValue(self, value):
        self.__lastRSSIValue = value
        XbeeSender.MQTTpublish("rssi/" + self.__ni.lower(), str(value))

    def setLastValueSave(self, typ, zeit, value):
        self.__lastValueSave[typ] = (zeit, value)

    def getLastValueSave(self, typ):
        return self.__lastValueSave[typ]

    def printLastValueSave(self, jetzt):
        print(
            "Sensor: ",
            self.__ni,
            " Aktuelle Zeit: ",
            time.localtime(jetzt),
            "(",
            jetzt,
            ")",
        )
        for key, value in self.__lastValueSave.items():
            print(key, ":\t", value)
        print("---------------------------------------------")
        print(" ", flush=True)

    def setLastContact(self):
        self.__lastcontact = actualTime()

    def getLastContact(self):
        return self.__lastcontact

    def setSenderNI(self, ni):
        self.__ni = ni

    def returnSenderNI(self):
        return self.__ni

    def handleFunction(self, frame, Xbee):
        print(frame, flush=True)
        digitalChannelMask = (frame[13] << 8) + frame[14]
        analogChannelMask = frame[15]
        valueSaved = False

        if digitalChannelMask > 0:
            # print ('Digital Channel Mask: %d' % digitalChannelMask)
            digitalSample = (frame[16] << 8) + frame[17]
            # print ('Digital Sample', digitalSample)

            ##
            #
            # Echo Digital Signals sent by remote XBee
            #
            for bit in Xbee.DigitalIOMask.keys():
                if digitalChannelMask & 2 ** bit:
                    highlow = (digitalSample & 2 ** bit) >> bit
                    digitalLine = Xbee.DigitalIOMask[bit]
                    # print (" Bit = ", bit)
                    # print (' High/Low = ', highlow)

                    if self.__ni not in BewegungsMelder.keys():
                        pass

                    elif BewegungsMelder[self.__ni] == digitalLine:
                        highlow = (digitalSample & 2 ** bit) >> bit
                        # print ('Setze Pin ', BewegungOut[self.__ni], ' auf ',
                        # highlow)
                        Xbee.digitalPin(BewegungOut[self.__ni], highlow)
                        # print (self.__ni)
                        # print ('alarm/'+self.__ni.lower()+'/detected',
                        # str(highlow))
                        XbeeSender.MQTTpublish(
                            "alarm/" + self.__ni.lower() + "/detected",
                            str(highlow),
                        )

                    if self.__ni not in KlatschSchalter.keys():
                        pass

                    elif KlatschSchalter[self.__ni] == digitalLine:
                        highlow = (digitalSample & 2 ** bit) >> bit
                        # print ('Setze Pin ', KlatschOut[self.__ni],
                        #        ' auf ', highlow)
                        Xbee.digitalPin(KlatschOut[self.__ni], highlow)
                        # print (self.__ni)
                        # print ('klatsch/'+self.__ni.lower()+'/detected',
                        #        str(highlow))
                        if highlow:
                            XbeeSender.MQTTpublish(
                                "klatsch/" + self.__ni.lower() + "/detected",
                                str(highlow),
                            )

        if analogChannelMask > 0:
            # print ('Analog channel mask: %d' % analogChannelMask)
            analogSampleIndex = 18
            jetzt = actualTime()
            # self.printLastValueSave(jetzt)

            for bit in Xbee.AnalogIOMask.keys():
                if analogChannelMask & 2 ** bit:
                    analogLine = Xbee.AnalogIOMask[bit]
                    # print (' Analog-Line =',analogLine)

                    analogSample = (frame[analogSampleIndex] << 8) + frame[
                        analogSampleIndex + 1
                    ]
                    analogSampleIndex += 2

                    if self.__ni not in TemperaturSensoren.keys():
                        pass

                    elif TemperaturSensoren[self.__ni] == analogLine:
                        temperature = get_tempature(analogSample)
                        # print (' Analog sample: %d' % analogSample)
                        # print (' Temperatur: %f' % temperature)

                        if "Temperature" not in self.__lastValueSave.keys():
                            self.__lastValueSave["Temperature"] = (
                                jetzt - XbeeSender.__initIntervall,
                                temperature,
                            )
                        lastTime, lastValue = self.__lastValueSave[
                            "Temperature"
                        ]
                        if lastTime < jetzt - XbeeSender.__temperaturIntervall:
                            self.__lastValueSave["Temperature"] = (
                                jetzt,
                                temperature,
                                )
                            XbeeSender.MQTTpublish(
                                "temperatur/" + self.__ni.lower(),
                                str(temperature)
                            )
                            XbeeSender.MQTTpublish(
                                "temperatur_n/" + self.__ni.lower(),
                                str(analogSample)
                            )

                            valueSaved = True

                    if self.__ni not in LichtSensoren.keys():
                        pass

                    elif LichtSensoren[self.__ni] == analogLine:
                        helligkeit = analogSample

                        # print (' Analog (Licht) sample: %d' % analogSample)
                        if "Light" not in self.__lastValueSave.keys():
                            self.__lastValueSave["Light"] = (
                                jetzt - XbeeSender.__initIntervall,
                                helligkeit,
                            )

                        lastTime, lastValue = self.__lastValueSave["Light"]
                        if lastTime < jetzt - XbeeSender.__lichtIntervall:
                            XbeeSender.MQTTpublish(
                                "licht/" + self.__ni.lower(), str(helligkeit)
                            )
                            self.__lastValueSave["Light"] = (jetzt, helligkeit)
                            valueSaved = True

                    if self.__ni not in SpannungsSensoren.keys():
                        pass

                    elif SpannungsSensoren[self.__ni] == analogLine:
                        spannung = analogSample
                        # print(' Analog (Spannung) sample: %d' % analogSample)
                        if "Power" not in self.__lastValueSave.keys():
                            self.__lastValueSave["Power"] = (
                                jetzt - XbeeSender.__initIntervall,
                                spannung,
                            )

                        lastTime, lastValue = self.__lastValueSave["Power"]
                        if lastTime < jetzt - XbeeSender.__spannungsIntervall:
                            self.__lastValueSave["Power"] = (jetzt, spannung)
                            XbeeSender.MQTTpublish(
                                "spannung/" + self.__ni.lower(), str(spannung)
                            )
                            valueSaved = True
        return valueSaved

    def returnSenderID(self):
        return self.__sender

    def __repr__(self):
        return (
            "<Xbee: %s, Location: %s, Registriert: %s, Last Contact: %s, Last RSSI: %s>"
            % (
                self.__sender,
                self.__ni,
                time.strftime(
                    "%Y-%m-%d %H:%M:%S", time.localtime(self.__regtime)
                ),
                time.strftime(
                    "%Y-%m-%d %H:%M:%S", time.localtime(self.__lastcontact)
                ),
                self.__lastRSSIValue,
            )
        )

    @staticmethod
    def returnXbee(sender):
        resultXbee = None
        for xbee in XbeeSender.__xbeeList:
            if xbee.returnSenderID() == sender:
                resultXbee = xbee
                break

        if not resultXbee:
            resultXbee = XbeeSender(sender)

        return resultXbee

    @staticmethod
    def MQTTC(mqttc):
        XbeeSender.__mqttc = mqttc

    @staticmethod
    def setMQTTonline(status):
        XbeeSender.__mqttIsOnline = status

    @staticmethod
    def getMQTTonline():
        return XbeeSender.__mqttIsOnline

    @staticmethod
    def MQTTpublish(topic, value):
        if XbeeSender.__mqttIsOnline:
            XbeeSender.__mqttc.publish(topic, value)
