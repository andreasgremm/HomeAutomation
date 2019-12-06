/*
    ESP8266 Klatschschalter - MQTT Sender
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

//#define WLANON

#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <ESP8266WebServer.h>
#include <ESP8266mDNS.h>
#include <ESP8266HTTPUpdateServer.h>

// #include <PubSubClient.h>
#include <Ticker.h>  //Ticker Library
#include <EEPROM.h>
#include <time.h>
 
#define LED 2
#define internalLED 16 //On board LED
#define KLINGEL D6

// Remove this include which sets the below constants to my own conveniance
#include </Users/andreas/Documents/git-github/non-git-local-includes/ESP8266_klingeldetektor.h>

// The following constants need to be set in the program
/*
const char* host = "HOSTNAME";
const char* ssid[] = {"ssid1", "ssid2"};
const char* password[] = {"pw1", "pw2"};

const char* brocker = "HOSTNAME or IP of MQTT brocker";
const char* mqttUser = "MQTT User Name";
const char* mqttPass = "MQTT Password";
const char* mqttClientId = "MQTT Client Name";
*/

size_t anzSSID = sizeof(ssid) / sizeof(ssid[0]);

const byte interruptPin = 13;

volatile byte interruptCounter = 0;
volatile int numberOfInterrupts = 0;
volatile int numberOfKlatsch = 0;
// volatile int maxKlatsch = 0;

// long mqttConnectionLost = 0;
const byte eepromInitialized = 100;
byte defaultAnzahl=6;
boolean networkConnected = false;
byte mySSID;
byte mac[6];
String smac;

char theOutput[80];

Ticker inputTimer;

ESP8266WebServer httpServer(80);
ESP8266HTTPUpdateServer httpUpdater;

WiFiClient wifi;
//PubSubClient mqtt(wifi);

void ICACHE_RAM_ATTR handleInterrupt() {
  interruptCounter++;
/*  time_t tnow = time(nullptr);
  Serial.println(String(ctime(&tnow)));
  */
}

void ICACHE_RAM_ATTR handleTicker() {
  numberOfKlatsch = numberOfInterrupts;
//  maxKlatsch = max(maxKlatsch, numberOfKlatsch);
  numberOfInterrupts = 0;
  digitalWrite(LED, LOW);
}

void setup(void){
  pinMode(interruptPin, INPUT);
  pinMode(KLINGEL, OUTPUT);
  digitalWrite(KLINGEL, LOW);

  pinMode(LED, OUTPUT);
  digitalWrite(LED,LOW);
  pinMode(internalLED, OUTPUT);
  digitalWrite(internalLED,HIGH); 
  Serial.begin(115200);
  Serial.println();
  Serial.println("Booting Sketch...");

  EEPROM.begin(2);
  if (EEPROM.read(0) == eepromInitialized){
    defaultAnzahl = EEPROM.read(1);
    Serial.print("Default Anzahl from EEPROM:");
    Serial.println(defaultAnzahl);
  }

#ifndef WLANON
  WiFi.mode(WIFI_OFF);
#endif

#ifdef WLANON
  WiFi.mode(WIFI_STA);
  WiFi.disconnect();
  delay(100);
  while (!networkConnected) {
    int n = WiFi.scanNetworks();
    if (n == 0) {
      Serial.println("no networks found");
    } else {
      for (int i = 0; i < n; ++i) {
        for (int j=0;j < anzSSID; j++) {
          if (WiFi.SSID(i).equals(String(ssid[j]))) {
            networkConnected = true;
            wificonnect(ssid[j], password[j]);
            mySSID = j;
            break;
          }
        }
      }
    }    
  delay(1000);
//  WiFi.printDiag(Serial);
  WiFi.macAddress(mac);
  smac = macToString(mac);
  }
  
//  mqtt.setServer(brocker, 1883);
//  mqtt.setCallback(messageReceived);
//  mqttconnect();
  //Attach handles for different pages.
  httpUpdater.setup(&httpServer);
  httpServer.on("/", handleRoot);
  httpServer.on("/status",handleStatus);
  httpServer.on("/DEFAULTANZAHL",handleDefaultAnzahl);
  httpServer.begin();

  if (MDNS.begin(host)) {
      MDNS.addService("http", "tcp", 80);
   }
   else {
      Serial.println("Error setting up MDNS responder!");
   };

  configTime(0, 0, "pool.ntp.org", "time.nist.gov");
  setenv("TZ", "CET-1CEST,M3.5.0,M10.5.0/3", 0);

#endif

  attachInterrupt(digitalPinToInterrupt(interruptPin), handleInterrupt, RISING);
  timer1_attachInterrupt(handleTicker);
  timer1_enable(TIM_DIV256, TIM_EDGE, TIM_SINGLE);

  Serial.println("Up and running!");
}

void loop(void){
  delay(10);
  
#ifdef WLANON
// Allow MDNS processing
 MDNS.update();

/*  if(!mqtt.connected()) {
    Serial.println("MQTT connection lost.");
    mqttConnectionLost++;
    mqttconnect();
  }
*/

  httpServer.handleClient();
//  mqtt.loop();
#endif

  if (numberOfKlatsch>defaultAnzahl){
    time_t tnow = time(nullptr);
    Serial.print(String(ctime(&tnow)));
    sprintf(theOutput, " Number of Klatsch: %d",numberOfKlatsch);
    Serial.println(theOutput);
    digitalWrite(internalLED, LOW);
    digitalWrite(KLINGEL, HIGH); 
    delay(10);
    digitalWrite(KLINGEL, LOW);
    digitalWrite(internalLED, HIGH);

    numberOfKlatsch=0;
  }

  if(interruptCounter>0){
    if (numberOfInterrupts == 0) {
//      mqtt.publish("radio/power", "?");
//      mqtt.publish("radio/volume", "??");
      timer1_write(600000); //3-4s
      digitalWrite(LED, HIGH);
    }
    interruptCounter--;
    numberOfInterrupts++;
    sprintf(theOutput, "An interrupt has occurred. Total: %d\n",numberOfInterrupts);
    Serial.println(theOutput);

  }
}

void wificonnect(const char * ssid, const char * password) {
  while(WiFi.waitForConnectResult() != WL_CONNECTED){
    WiFi.begin(ssid, password);
    Serial.print(".");
    delay(500);
  }
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  Serial.println("\n WiFi connected!");
}

/*void mqttconnect() {
  while (!mqtt.connect(mqttClientId, mqttUser, mqttPass, "clientstatus/Klatschschalter-1",1,1,"OFFLINE")) {
    Serial.print(".");
    delay(500);
  }
  Serial.println("\n MQTT connected!");
  mqtt.publish("clientstatus/Klatschschalter-1", "ONLINE");
  mqtt.subscribe("radio/status/#",1);
}
*/

void handleRoot() {
  time_t tnow = time(nullptr);
  String message = "<html><head><title>Klingeldetektor</title></head><body>\
<h4>Uhrzeit: " + String(ctime(&tnow)) + "</h4>\
<a href='/status'>Status</a><br />\
<a href='/update'>Update</a><br />\
<form action='/DEFAULTANZAHL' method='post'>\
Ausl&ouml;sung durch Anzahl Signale: <input type='number' min='1' max='12' name='Anzahl' value='"+String(defaultAnzahl)+"' >\
<input type='submit' value='Default setzen'>\
</form><br />\
</body></html>";

  httpServer.send(200, "text/html", message);
}

void handleStatus() {
  String theStatus = "<html><head></head><body>Verbunden mit: <b>" + String(ssid[mySSID]) + "</b><br />\
MAC-Adresse: <b>" + smac + "</b><br />\
IP-Adresse: <b>" + ipToString(WiFi.localIP()) + "</b><br />\
Subnet Mask: <b>" + ipToString(WiFi.subnetMask()) + "</b><br />\
Gateway-IP: <b>" + ipToString(WiFi.gatewayIP()) + "</b><br />\
<a href='/'>Startseite</a></body></html>";
  httpServer.send(200, "text/html", theStatus);
}

void handleDefaultAnzahl() {
  char theStatus[180];
  if (httpServer.args()>0) {
    for ( uint8_t i = 0; i < httpServer.args(); i++ ) {
      if (httpServer.argName(i) == "Anzahl") {
         // do something here with value from server.arg(i);
         defaultAnzahl=httpServer.arg(i).substring(0,2).toInt();
         Serial.print("Default Anzahl from HTTP POST:");
         Serial.print(" Byte: ");
         Serial.print(defaultAnzahl);
         Serial.print(" String: ");
         Serial.println(httpServer.arg(i));
         EEPROM.write(0, eepromInitialized);
         EEPROM.write(1,defaultAnzahl);
         EEPROM.commit();
         sprintf(theStatus, "<html><head></head><body>Anzahl gesetzt auf: %d <br /><a href='/'>Startseite</a></body></html>",defaultAnzahl);
         httpServer.send(200, "text/html", theStatus);
      }
   }
  }
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

/*void messageReceived(char * topic, unsigned char * payload, unsigned int length) {

   Serial.print("incoming: ");
   Serial.print(topic);
   Serial.print(" - ");
   for (byte i = 0; i < length; i++) {
      Serial.print((const char)payload[i]);
   }
   Serial.println();
   if (strcmp(topic,"radio/status/power") == 0) {
    if (strncmp((const char *)payload, "False", length) == 0) {
      radioPower = false;
    }
    if (strncmp((const char *)payload, "True", length) == 0) {
      radioPower = true;
    }
  }

  if (strcmp(topic,"radio/status/mute") == 0) {
    if (strncmp((const char *)payload, "False", length) == 0) {
      radioMute = false;
    }
    if (strncmp((const char *)payload, "True", length) == 0) {
      radioMute = true;
    }
  }
}*/
