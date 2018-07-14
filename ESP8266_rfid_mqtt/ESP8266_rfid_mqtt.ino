/*
    ESP8266 RFID Reader - MQTT Sender
    Copyright 2016 Christian Moll <christian@chrmoll.de>

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

#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <ESP8266WebServer.h>
#include <ESP8266mDNS.h>
#include <ESP8266HTTPUpdateServer.h>

#include <PubSubClient.h>

#include <SPI.h>
#include <MFRC522.h>

#define SS_PIN D4
#define RST_PIN D3

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

int onPin = D1;
int offPin = D2;
int irPin = A0;
int irValue;
bool alarm = false;
int motion;
bool buzzer = true;

ESP8266WebServer httpServer(80);
ESP8266HTTPUpdateServer httpUpdater;

WiFiClient wifi;
PubSubClient mqtt(wifi);

MFRC522 rfid(SS_PIN, RST_PIN);

void wificonnect();
void mqttconnect();

void setup(void){
  pinMode(onPin, OUTPUT);
  pinMode(offPin, OUTPUT);
  digitalWrite(onPin, HIGH);
  digitalWrite(offPin, HIGH);
  pinMode(irPin, INPUT);


  SPI.begin();
  rfid.PCD_Init();

  Serial.begin(115200);
  Serial.println();
  Serial.println("Booting Sketch...");
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  mqtt.setServer(brocker, 1883);
  mqtt.setCallback(messageReceived);

  wificonnect();
  digitalWrite(onPin, LOW);

  mqttconnect();
  digitalWrite(offPin, LOW);

  MDNS.begin(host);

  //Attach handles for different pages.
  httpUpdater.setup(&httpServer);

  httpServer.on("/", handleRoot);

  httpServer.begin();

  MDNS.addService("http", "tcp", 80);
  Serial.println("Up and running!");
}

void loop(void){
  if(!mqtt.connected()) {
    mqttconnect();
  }

  httpServer.handleClient();
  mqtt.loop();
  //delay(10);
  handleRFID();
  handleIR();
}

void wificonnect() {
  while(WiFi.waitForConnectResult() != WL_CONNECTED){
    WiFi.begin(ssid, password);
    Serial.println("WiFi failed, retrying.");
  }

  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  Serial.println("\n WiFi connected!");
}

void mqttconnect() {
  while (!mqtt.connect(mqttClientId, mqttUser, mqttPass, "clientstatus/RFIDReader",1,1,"OFFLINE")) {
    Serial.print(".");
  }
  Serial.println("\n MQTT connected!");
  mqtt.subscribe("alarm/wohnzimmer/motion");
  mqtt.publish("clientstatus/RFIDReader", "ONLINE");
}

void handleRoot() {
  httpServer.send(200, "text/plain", "It works!!!");
}

void handleIR() {
  irValue = analogRead(irPin);
  if (irValue > 100) {
    if (alarm and buzzer){
      buzzer = false;
      mqtt.publish("buzzer/wohnzimmer", "2");
    }
  } else {
    buzzer = true;
  }
}
void messageReceived(char * topic, unsigned char * payload, unsigned int length) {
  Serial.print("incoming: ");
  Serial.print(topic);
  Serial.print(" - ");
  for (byte i = 0; i < length; i++) {
     Serial.print((const char)payload[i]);
  }

  if(strncmp((const char *)payload, "False", length) == 0) {
    digitalWrite(onPin, LOW);
    digitalWrite(offPin, HIGH);
    alarm = false;
  }
  if(strncmp((const char *)payload, "True", length) == 0) {
    digitalWrite(onPin, HIGH);
    digitalWrite(offPin, LOW);
    alarm = true;
  }

  Serial.println();
}

void handleRFID() {
  if (!rfid.PICC_IsNewCardPresent()) return;
  if (!rfid.PICC_ReadCardSerial()) return;
  String rfiduid = printHex(rfid.uid.uidByte, rfid.uid.size);
  Serial.println(rfiduid);
  mqtt.publish("rfid_reader/uid", rfiduid.c_str());
  if (strcmp(rfiduid.c_str(),"c5d54c73") == 0) {
    if (alarm) {
      mqtt.publish("alarm/wohnzimmer/motion",(const uint8_t *)"False",5,true);
    } else {
      mqtt.publish("alarm/wohnzimmer/motion",(const uint8_t *)"True",4,true);
    }
  }
  rfid.PICC_HaltA();
  rfid.PCD_StopCrypto1();
}

double mapDouble(double x, double in_min, double in_max, double out_min, double out_max)
{
  double temp = (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
  temp = (int) (4*temp + .5);
  return (double) temp/4;
}

String printHex(byte *buffer, byte bufferSize) {
  String id = "";
  for (byte i = 0; i < bufferSize; i++) {
    id += buffer[i] < 0x10 ? "0" : "";
    id += String(buffer[i], HEX);
  }
  return id;
}
