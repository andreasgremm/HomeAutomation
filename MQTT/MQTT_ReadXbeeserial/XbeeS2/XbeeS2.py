import binascii
import codecs

import serial

frameStartDelimiter = bytes(chr(0x7E), "utf-8")
dataSampleRXIndicator = 0x92
ATCommandResponse = 0x88
RemoteCommandResponse = 0x97
modemStatus = 0x8A

# DIO0 = 0
# DIO1 = 1
# DIO2 = 2
# DIO3 = 3
# DIO4 = 4
# DIO5 = 5
# DIO6 = 6
# GPIO7 = 7
# DIO10 = 10
# DIO11 = 11
# DIO12 = 12

# AD0 = 0
# AD1 = 1
# AD2 = 2
# AD3 = 3


class XbeeS2(object):
    __DIObitmask = [0, 1, 2, 3, 4, 5, 6, 7, 10, 11, 12]
    __AIObitmask = [0, 1, 2, 3]
    __digitalHighLow = [chr(0x4), chr(0x5)]

    def __init__(self, tty):
        self.DigitalIOMask = {}
        self.AnalogIOMask = {}
        self.__tty = tty

        for mask in XbeeS2.__DIObitmask:
            self.DigitalIOMask[mask] = "D" + str(mask)

        for mask in XbeeS2.__AIObitmask:
            self.AnalogIOMask[mask] = "A" + str(mask)

    def open(self):
        self.__serial = serial.Serial(port=self.__tty, baudrate=9600)

    def close(self):
        print("closing ...", flush=True)
        self.__serial.close()
        print(self, flush=True)

    def read(self, num=1):
        incoming = self.__serial.read(num)
        return incoming

    def write(self, frame):
        return self.__serial.write(bytes("".join(frame), "latin-1"))

    def __repr__(self):
        return str(self.__serial)

    def __del__(self):
        self.close()

    def frameLength(self):
        frameLengthBytes = self.read(2)
        msb = frameLengthBytes[0]
        lsb = frameLengthBytes[1]
        frameLength = (msb << 8) + lsb
        # Debug
        if msb == 0xFF:
            print(
                "Problem .... Framelength issue msb =",
                str(msb),
                ", FrameLength = ",
                frameLength,
                flush=True
            )
        return frameLength

    """
    To test data integrity, a checksum is calculated and verified on
    non-escaped data.
    To calculate: Not including frame delimiters and length,
    add all bytes keeping only the lowest 8 bits of the
    result and subtract the result from 0xFF.
    To verify: Add all bytes (include checksum,
    but not the delimiter and length). If the checksum is correct,
    the sum will equal 0xFF.
   """

    def verifyChecksum(self, frame, checksum):
        summe = 0
        for i in frame:
            summe = (summe + i) & 0xFF

        summe = (summe + ord(checksum)) & 0xFF

        return summe == 0xFF

    def createChecksum(self, frame):
        summe = 0
        for i in frame:
            summe = (summe + ord(i)) & 0xFF

        summe = 0xFF - summe

        return summe

    def digitalPin(self, DIO, highlow):
        frame0 = [
            chr(0x08),
            chr(0x01),
            DIO[0],
            DIO[1],
            XbeeS2.__digitalHighLow[highlow],
        ]
        checksum = self.createChecksum(frame0)

        frame = [chr(0x7E), chr(0x00), chr(0x05)]
        for i in frame0:
            frame.append(i)
        frame.append(chr(checksum))
        self.write(frame)

    def getSender(self, frame):
        return codecs.getencoder("hex_codec")(frame[1:9])[0].decode()

    def getSenderRCDBResponse(self, frame):
        return codecs.getencoder("hex_codec")(frame[2:10])[0].decode()

    def getSenderATNDResponse(self, frame):
        return codecs.getencoder("hex_codec")(frame[7:15])[0].decode()

    def getSenderNetID(self, frame, frameLength):
        netID = []
        for i in frame[15:frameLength]:
            if i == 0:
                break
            netID.append(chr(i))
        return "".join(netID)

    def networkDiscovery(self):
        frame0 = [chr(0x08), chr(0x01), chr(0x4E), chr(0x44)]
        checksum = self.createChecksum(frame0)

        frame = [chr(0x7E), chr(0x00), chr(0x04)]
        for i in frame0:
            frame.append(i)
        frame.append(chr(checksum))
        self.write(frame)

    def getAssocIndic(self):
        frame0 = [chr(0x08), chr(0x01), chr(0x41), chr(0x49)]
        checksum = self.createChecksum(frame0)

        frame = [chr(0x7E), chr(0x00), chr(0x04)]
        for i in frame0:
            frame.append(i)
        frame.append(chr(checksum))
        self.printFrame(frame)
        self.write(frame)

    def softReset(self):
        frame0 = ["F", "R"]
        checksum = self.createChecksum(frame0)

        frame = [chr(0x7E), chr(0x00), chr(0x02)]
        for i in frame0:
            frame.append(i)
        frame.append(chr(checksum))
        self.printFrame(frame)
        self.write(frame)

    def getRSSI(self, destination):
        frame0 = [chr(0x17), chr(0x01)]
        for s in binascii.unhexlify(destination):
            frame0.append(chr(s))
        frame0.append(chr(0xFF))
        frame0.append(chr(0xFE))
        frame0.append(chr(0x02))
        frame0.append(chr(0x44))
        frame0.append(chr(0x42))
        checksum = self.createChecksum(frame0)

        frame = [chr(0x7E), chr(0x00), chr(0x0F)]
        for i in frame0:
            frame.append(i)
        frame.append(chr(checksum))

        self.write(frame)

    def getRSSIValue(self, frame, frameLength):
        return frame[frameLength - 1]

    def printFrame(self, frame):
        print("<FRAME START>", flush=True)
        print(frame, flush=True)
        print("<FRAME END>", flush=True)
