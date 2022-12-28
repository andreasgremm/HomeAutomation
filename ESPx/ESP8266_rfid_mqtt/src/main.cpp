/*
    ESP8266 RFID Reader - MQTT Sender
    Copyright 2016 Christian Moll <christian@chrmoll.de>
    Copyright 2018 Andreas Gremm

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    Dieses Programm ist Freie Software: Sie können es unter den Bedingungen
    der GNU General Public License, wie von der Free Software Foundation,
    Version 3 der Lizenz oder (nach Ihrer Wahl) jeder neueren
    veröffentlichten Version, weiterverbreiten und/oder modifizieren.

    Dieses Programm wird in der Hoffnung, dass es nützlich sein wird, aber
    OHNE JEDE GEWÄHRLEISTUNG, bereitgestellt; sogar ohne die implizite
    Gewährleistung der MARKTFÄHIGKEIT oder EIGNUNG FÜR EINEN BESTIMMTEN ZWECK.
    Siehe die GNU General Public License für weitere Details.

    Sie sollten eine Kopie der GNU General Public License zusammen mit diesem
    Programm erhalten haben. Wenn nicht, siehe <http://www.gnu.org/licenses/>.
*/

#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <ESP8266WebServer.h>
#include <ESP8266mDNS.h>
#include <ESP8266HTTPUpdateServer.h>
#include <time.h>
#include <TZ.h>

#include <PubSubClient.h>

#include <SPI.h>
#include <MFRC522.h>

#define SS_PIN D4
#define RST_PIN D3
int autoAlarmPin = D1;
int wohnzimmerAlarmPin = D2;
int irPin = A0;

// Remove this include which sets the below constants to my own conveniance
#include </Users/andreas/Documents/git-github/non-git-local-includes/ESP8266_rfid_mqtt_local.h>

// The following constants need to be set in the program
/*
const char* host = "HOSTNAME";
const char* ssid = "SSID of WlAN";
const char* password = "PASSWORD to conect to ssid";

const char* brocker = "HOSTNAME or IP of MQTT brocker";
const char* mqttUser = "MQTT User Name";
const char* mqttPass = "MQTT Password";
const char* mqttClientId = "MQTT Client Name";
*/


int irValue;
bool wohnzimmerAlarm = false;
bool autoAlarm = false;
int motion;
bool buzzer = true;
long mqttConnectionLost = 0;
byte mac[6];
String smac;

unsigned long previousMillis = 0;  
unsigned long currentMillis;
const long interval = 60000;   

String mfrc522SoftwareVersion;

ESP8266WebServer httpServer(80);
ESP8266HTTPUpdateServer httpUpdater;

WiFiClient wifi;
PubSubClient mqtt(wifi);

MFRC522 rfid(SS_PIN, RST_PIN);

void handleRoot() {
  time_t tnow = time(nullptr);
  String swohnzimmerAlarm = wohnzimmerAlarm ? "<font color='green'>Ein</font>" : "<font color='red'>Aus</font>";
  String sautoAlarm = autoAlarm ? "<font color='green'>Ein</font>" : "<font color='red'>Aus</font>";
  String message = "<html><head><style>table, th, td {border: 1px solid black;}</style><title>RFC Reader</title>\
<meta http-equiv='refresh' content='10'></head><body>\
<h4>Uhrzeit: " + String(ctime(&tnow)) + "</h4>\
<br /><table><caption>Alarmanlage Status</caption><tr><th>Wohnzimmer Alarm</th><th>Auto Alarm</th></tr>\
<tr><td><center>" + swohnzimmerAlarm + "</center></td><td><center>" + sautoAlarm + "</center></td></tr>\
</table><br />\
<a href='/status'>Status</a><br />\
<a href='/update'>Update</a><br />\
</body></html>";

  httpServer.send(200, "text/html", message);
}

void blinkLed(int led, int nr, bool ledstatus) {
  if (nr == 0) {
    return;
  }
  nr--;
  digitalWrite(led, !ledstatus);
  delay(200);
  digitalWrite(led, ledstatus);
  delay(200);
  blinkLed(led, nr, ledstatus);  
}

String printHex(byte *buffer, byte bufferSize) {
  String id = "";
  for (byte i = 0; i < bufferSize; i++) {
    id += buffer[i] < 0x10 ? "0" : "";
    id += String(buffer[i], HEX);
  }
  return id;
}

double mapDouble(double x, double in_min, double in_max, double out_min, double out_max)
{
  double temp = (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
  temp = (int) (4*temp + .5);
  return (double) temp/4;
}

String ipToString(IPAddress ip){
  String s="";
  for (int i=0; i<4; i++)
    s += i  ? "." + String(ip[i]) : String(ip[i]);
  return s;
}

String macToString(byte mac[6]){
  String s="";
  for (byte i=0; i<6; i++){
    char buf[3];
    sprintf(buf, "%2X", mac[i]);
    s += buf;
    if (i < 5) s+=':';
  }
  return s;
}

bool handleRfidStatus() {
  bool rfidStatus = rfid.PCD_PerformSelfTest();
  rfid.PCD_Init();
  if (rfidStatus) {
      blinkLed(wohnzimmerAlarmPin, 2, wohnzimmerAlarm);
  }
  else {
      blinkLed(autoAlarmPin, 2, autoAlarm);
  }
  return rfidStatus;
}

void handleStatus() {
  char theRfidStatus[80];
  bool rfidStatus = handleRfidStatus();

  sprintf(theRfidStatus, "RFID-Selftest:<b> %s</b><br />MQTT-Reconnect:<b> %ld </b><br />",rfidStatus ? "True" : "False",mqttConnectionLost);

   String theStatus = "<html><head><style>table, th, td {border: 1px solid black;}</style>\
<title>RFC Reader</title></head><body>\
<table><caption>Network Attributes</caption><tr><th>Attribut</th><th>Wert</th></tr>\
<tr><td>MAC-Adresse</td><td><b>" + smac + "</b></td></tr>\
<tr><td>IP-Adresse</td><td><b>" + ipToString(WiFi.localIP()) + "</b></td></tr>\
<tr><td>Subnet Mask</td><td><b>" + ipToString(WiFi.subnetMask()) + "</b></td></tr>\
<tr><td>Gateway-IP</td><td><b>" + ipToString(WiFi.gatewayIP()) + "</b></td></tr>\
</table><br />" + String(theRfidStatus) + mfrc522SoftwareVersion + "\
<a href='/'>Startseite</a></body></html>";
  httpServer.send(200, "text/html", theStatus);
}

void handleIR() {
  irValue = analogRead(irPin);
  if (irValue > 100) {
    if (wohnzimmerAlarm and buzzer){
      buzzer = false;
      mqtt.publish("buzzer/wohnzimmer", "2");
    }
    if ((currentMillis - previousMillis) >= interval) {
      // save time
      previousMillis = currentMillis;
      bool rfidStatus = handleRfidStatus();
    }
  } else {
    buzzer = true;
  }
}

void messageReceived(char * topic, unsigned char * payload, unsigned int length) {
/*
  Serial.print("incoming: ");
  Serial.print(topic);
  Serial.print(" - ");
  for (byte i = 0; i < length; i++) {
     Serial.print((const char)payload[i]);
  }
*/
  if (strcmp(topic,"alarm/wohnzimmer/motion") == 0) {
    if (strncmp((const char *)payload, "False", length) == 0) {
      digitalWrite(wohnzimmerAlarmPin, LOW);
      wohnzimmerAlarm = false;
    }
    if (strncmp((const char *)payload, "True", length) == 0) {
      digitalWrite(wohnzimmerAlarmPin, HIGH);
      wohnzimmerAlarm = true;
    }
  }

  if (strcmp(topic,"alarm/auto/motion") == 0) {
    if (strncmp((const char *)payload, "False", length) == 0) {
      digitalWrite(autoAlarmPin, LOW);
      autoAlarm = false;
    }
    if (strncmp((const char *)payload, "True", length) == 0) {
      digitalWrite(autoAlarmPin, HIGH);
      autoAlarm = true;
    }
  }
 // Serial.println();
}

void handleRFID() {
  if (!rfid.PICC_IsNewCardPresent()) return;
  if (!rfid.PICC_ReadCardSerial()) return;
  String rfiduid = printHex(rfid.uid.uidByte, rfid.uid.size);
  rfid.PICC_HaltA();
  rfid.PCD_StopCrypto1();
  blinkLed(wohnzimmerAlarmPin, 3, wohnzimmerAlarm);
  
//  Serial.println(rfiduid);
  mqtt.publish("rfid_reader/uid", rfiduid.c_str());
  if (strcmp(rfiduid.c_str(),"c5d54c73") == 0) {
    if (wohnzimmerAlarm) {
      mqtt.publish("alarm/wohnzimmer/motion", "False", true);
    } else {
      mqtt.publish("alarm/wohnzimmer/motion", "True", true);
    }
  }
  if (strcmp(rfiduid.c_str(),"c6ebfe1f") == 0) {
    if (autoAlarm) {
      mqtt.publish("alarm/auto/motion", "False", true);
    } else {
      mqtt.publish("alarm/auto/motion", "True", true);
    }
  }
}

void wificonnect() {
  while(WiFi.waitForConnectResult() != WL_CONNECTED){
    WiFi.begin(ssid, password);
    Serial.println("WiFi failed, retrying.");
    delay(500);
  }

  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  Serial.println("\n WiFi connected!");
}

void mqttconnect() {
  const char* message = "ONLINE";
  const int laenge = strlen(message);
  while (!mqtt.connect(mqttClientId, mqttUser, mqttPass, "clientstatus/RFIDReader",1,true,"OFFLINE")) {
    Serial.print(".");
    delay(500);
  }
  Serial.println("\n MQTT connected!");
  mqtt.subscribe("alarm/wohnzimmer/motion");
  mqtt.subscribe("alarm/auto/motion");
  mqtt.publish("clientstatus/RFIDReader", message, true);
}

void setup(void){
  pinMode(autoAlarmPin, OUTPUT);
  pinMode(wohnzimmerAlarmPin, OUTPUT);
  digitalWrite(autoAlarmPin, HIGH);
  digitalWrite(wohnzimmerAlarmPin, HIGH);
  pinMode(irPin, INPUT);
 
  SPI.begin();
  rfid.PCD_Init();
 
  Serial.begin(9600);
  Serial.println();
  Serial.println("Booting Sketch...");
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  mqtt.setServer(brocker, 1883);
  mqtt.setCallback(messageReceived);

  wificonnect();
  digitalWrite(autoAlarmPin, LOW);

  mqttconnect();
  digitalWrite(wohnzimmerAlarmPin, LOW);

  WiFi.macAddress(mac);
  smac = macToString(mac);

  //Attach handles for different pages.
  httpUpdater.setup(&httpServer);

  httpServer.on("/", handleRoot);
  httpServer.on("/status",handleStatus);

  httpServer.begin();

  if (MDNS.begin(host)) {
      MDNS.addService("http", "tcp", 80);
   }
   else {
      Serial.println("Error setting up MDNS responder!");
   };
  configTime(TZ_Europe_Berlin, "pool.ntp.org");

  mfrc522SoftwareVersion = "MFRC522 software version = <b>" + String(rfid.PCD_ReadRegister(rfid.VersionReg),HEX) + "</b><br />";
  Serial.println(mfrc522SoftwareVersion);

  Serial.println("Up and running!");
}

void loop(void){
  delay(10);
  currentMillis = millis();

  if(!mqtt.connected()) {
    Serial.println("MQTT connection lost.");
    mqttConnectionLost++;
    mqttconnect();
  }

  httpServer.handleClient();
  mqtt.loop();
  MDNS.update();
  handleRFID();
  handleIR();
}
