#!/usr/bin/env python
#
# TP-Link Wi-Fi Smart Plug Protocol Client
# For use with TP-Link HS-100 or HS-110
#
# by Lubomir Stroetmann
# Copyright 2016 softScheck GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
import socket
import json
from struct import pack


class TplinkHS110(object):
    version = 0.1

# Predefined Smart Plug Commands
# For a full list of commands, consult tplink_commands.txt
    commands = {'info': '{"system":{"get_sysinfo":{}}}',
                'on': '{"system":{"set_relay_state":{"state":1}}}',
                'off': '{"system":{"set_relay_state":{"state":0}}}',
                'cloudinfo': '{"cnCloud":{"get_info":{}}}',
                'wlanscan': '{"netif":{"get_scaninfo":{"refresh":0}}}',
                'time': '{"time":{"get_time":{}}}',
                'schedule': '{"schedule":{"get_rules":{}}}',
                'countdown': '{"count_down":{"get_rules":{}}}',
                'antitheft': '{"anti_theft":{"get_rules":{}}}',
                'reboot': '{"system":{"reboot":{"delay":1}}}',
                'reset': '{"system":{"reset":{"delay":1}}}',
                'emeter': '{"emeter":{"get_realtime":{}}}'
                }

# Check if IP is valid
    @staticmethod
    def validIP(ip):
        error = 0
        try:
            socket.inet_pton(socket.AF_INET, ip)
        except socket.error:
            error = 1
        return (error, ip)

# Encryption and Decryption of TP-Link Smart Home Protocol
# XOR Autokey Cipher with starting key = 171
    @staticmethod
    def encrypt(string):
        key = 171
        result = pack('>I', len(string))
        for i in string:
            a = key ^ ord(i)
            key = a
            result += chr(a)
        return result

    @staticmethod
    def decrypt(string):
        key = 171
        result = ""
        for i in string:
            a = key ^ ord(i)
            key = ord(i)
            result += chr(a)
        return result

    @staticmethod
    def hs110Discover(ip, cmd, debug):
        port_send = 9999
        port_bind = 9998
        hs110 = []
        if debug:
            print("Raw Request:\t", cmd)
        # Send a request
        sock_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#       sock_send.bind(('', port_bind))
        sock_send.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock_send.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock_send.settimeout(20)
        sock_send.sendto(TplinkHS110.encrypt(cmd)[4:], (ip, port_send))

        RUN = True
        # Receive the reply
        while RUN:
            try:
                response, addr = sock_send.recvfrom(1024)
                ip, fam = addr
                if debug:
                    print("From IP:  ", ip)
                    print("Received: ", len(response), ':',
                          TplinkHS110.decrypt(response))
                hs110.append(ip)
            except socket.timeout:
                if debug:
                    print("no response from server")
                RUN = False

        sock_send.close()
        return hs110

    def __init__(self, ip):
        self.__ip = None
        self.__name = None
        self.__port = 9999
        self.__name = None
        self.__info = None
        self.__currentPower = 0
        self.__highPower = 0
        self.__lowPower = 100000
        self.__lastPower = 0
        self.__lowhighPeak = False
        self.__lowhighPeakCount = 0
        self.__highlowPeak = False
        self.__highlowPeakCount = 0
        self.__connected = True
        self.__disconnectTime = None
        self.__systemStarted = False
        self.__lowPowerDetection = 0.0
        self.__lowPowerDetectionPeriod = 0
        self.__lowPowerCount = 0

        self.ip = ip

    def set_newip(self, value):
        error, vip = TplinkHS110.validIP(value)
        if error == 0:
            self.__ip = vip
            error = self.update()

    def get_newip(self):
        return self.__ip

    ip = property(get_newip, set_newip)

    def __repr__(self):
        return '<HS110: %s, IP: %s, Connected: %s>' %\
         (self.__name, self.__ip, self.__connected)

    def __del__(self):
        print('<Deleted -- HS110: %s, IP: %s>' % (self.__name, self.__ip))

    def update(self):
        error, info = self.request(self.commands['info'])
        if error == 0:
            self.__info = json.loads(info)
            self.__name = \
                unicode(self.__info["system"]["get_sysinfo"]["alias"])
#           print '<Error-Code: %d, alias: %s>' %\
#              (self.__info["system"]["get_sysinfo"]["err_code"],
#               self.__info["system"]["get_sysinfo"]["alias"])
        return error

    def startSystem(self, lowPowerDetection, period):
        self.__systemStarted = True
        self.__lowPowerDetection = lowPowerDetection * 1.0
        self.__lowPowerDetectionPeriod = period
        self.__lowPowerCount = 0
#       print "<System %s: LowPowerDetection: %f Period: %d>" %\
#           (self.__name, self.__lowPowerDetection,
#            self.__lowPowerDetectionPeriod)

    def stopSystem(self):
        self.__systemStarted = False

# Send command and receive reply
    def request(self,  cmd):
        try:
            sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock_tcp.connect((self.__ip, self.__port))
            sock_tcp.send(TplinkHS110.encrypt(cmd))
            data = sock_tcp.recv(2048)
            sock_tcp.close()

#           print "Sent:     ", cmd
#           print "Received: ", TplinkHS110.decrypt(data[4:])
        except socket.error:
            return (1, "Cound not connect to host " + self.__ip + ":"
                    + str(self.__port))
        return (0, TplinkHS110.decrypt(data[4:]))

    def calculatePeek(self):
        if self.lastPower == 0:
            self.lastPower = self.currentPower

        self.lowPower = min(self.currentPower, self.lowPower)
        self.highPower = max(self.currentPower, self.highPower)

        lasthighdifference = abs(self.highPower - self.lastPower)
        lastlowdifference = abs(self.lastPower - self.lowPower)

        highdifference = abs(self.highPower - self.currentPower)
        lowdifference = abs(self.currentPower - self.lowPower)

        if lasthighdifference > lastlowdifference:
            s0 = self.lowPower
        elif lasthighdifference < lastlowdifference:
            s0 = self.highPower
        else:
            s0 = self.currentPower

        if highdifference > lowdifference:
            s1 = self.lowPower
        elif highdifference < lowdifference:
            s1 = self.highPower
        else:
            s1 = self.currentPower

        if self.currentPower < self.__lowPowerDetection:
            self.__lowPowerCount += 1
        else:
            self.__lowPowerCount = 0

        finishDetected = False
        if self.__lowPowerCount == self.__lowPowerDetectionPeriod and \
           self.__systemStarted:
            finishDetected = True

#       print "<Lowpower: %d, Power: %d, Highpower %d, .. Lastpower %d>" %\
#             (self.__lowPower, self.__currentPower,
#              self.__highPower, self.__lastPower)
#       print "<Lastlowdif: %d, lowdif: %d, Lasthighdif %d, highdif %d>" %\
#             (lastlowdifference, lasthighdifference,
#              lowdifference, highdifference)

        if s1 - s0 > 0:
            self.lowhighPeakCount += 1
            self.highlowPeakCount = 0
            if self.lowhighPeakCount > 2:
                # print "< Stromsteigerung bei System %s >" % (self.name)
                self.resetPeekValues()

        elif s1 - s0 < 0:
            self.lowhighPeakCount = 0
            self.highlowPeakCount += 1
            if self.highlowPeakCount > 2:
                # print "< Stromreduktion bei System %s >" % (self.name)
                self.resetPeekValues()

#       print "<S0: %d, S1: %d, LHpeakC: %d, HLpeakC: %d, LowPowerC: %d>" %\
#              (s0, s1, self.lowhighPeakCount, self.highlowPeakCount,
#               self.__lowPowerCount)

        return (self.lowhighPeakCount, self.highlowPeakCount, finishDetected)

    def resetPeekValues(self):
        # print("<ResetStart - Lowpower: %d, Power: %d,
        #   Highpower %d, .. Lastpower %d>" %
        #   (self.__lowPower, self.__currentPower,
        #    self.__highPower, self.__lastPower))
        self.lowhighPeak = False
        self.highlowPeak = False
        self.lowhighPeakCount = 0
        self.highlowPeakCount = 0
        self.lastPower = self.currentPower
#       print "<ResetEnd - Lowpower: %d, Power: %d
#          Highpower %d, .. Lastpower %d>" % (self.__lowPower,
#          self.__currentPower, self.__highPower, self.__lastPower)

    @property
    def name(self):
        return self.__name

    @property
    def systemRunning(self):
        return self.__systemStarted

    def get_currentPower(self):
        return self.__currentPower

    def set_currentPower(self, value):
        self.__currentPower = value

    currentPower = property(get_currentPower, set_currentPower)

    def get_highPower(self):
        return self.__highPower

    def set_highPower(self, value):
        self.__highPower = value

    highPower = property(get_highPower, set_highPower)

    def get_lowPower(self):
        return self.__lowPower

    def set_lowPower(self, value):
        self.__lowPower = value

    lowPower = property(get_lowPower, set_lowPower)

    def get_lastPower(self):
        return self.__lastPower

    def set_lastPower(self, value):
        self.__lastPower = value

    lastPower = property(get_lastPower, set_lastPower)

    def get_lowhighPeak(self):
        return self.__lowhighPeak

    def set_lowhighPeak(self, value):
        self.__lowhighPeak = value

    lowhighPeak = property(get_lowhighPeak, set_lowhighPeak)

    def get_lowhighPeakCount(self):
        return self.__lowhighPeakCount

    def set_lowhighPeakCount(self, value):
        self.__lowhighPeakCount = value

    lowhighPeakCount = property(get_lowhighPeakCount, set_lowhighPeakCount)

    def get_highlowPeak(self):
        return self.__highlowPeak

    def set_highlowPeak(self, value):
        self.__highlowPeak = value

    highlowPeak = property(get_highlowPeak, set_highlowPeak)

    def get_highlowPeakCount(self):
        return self.__highlowPeakCount

    def set_highlowPeakCount(self, value):
        self.__highlowPeakCount = value

    highlowPeakCount = property(get_highlowPeakCount, set_highlowPeakCount)

    def get_connected(self):
        return self.__connected

    def set_connected(self, value):
        self.__connected = value

    connected = property(get_connected, set_connected)

    def get_disconnecttime(self):
        return self.__disconnectTime

    def set_disconnecttime(self, value):
        self.__disconnectTime = value

    disconnectTime = property(get_disconnecttime, set_disconnecttime)


if __name__ == "__main__":
    hs110_1 = TplinkHS110('192.168.1.193')
    print(hs110_1)
    del hs110_1

    hs110 = TplinkHS110('192.168.1.193')
    print(hs110)

    print(hs110.request(hs110.commands['emeter']))
