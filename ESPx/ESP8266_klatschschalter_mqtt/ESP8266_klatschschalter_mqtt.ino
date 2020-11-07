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

#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <ESP8266WebServer.h>
#include <ESP8266mDNS.h>
// #include <ESP8266HTTPUpdateServer.h>

#include <PubSubClient.h>
#include <Ticker.h>  //Ticker Library
#include <EEPROM.h>
 
#define LED 2 //On board LED

// Remove this include which sets the below constants to my own conveniance
#include </Users/andreas/Documents/git-github/non-git-local-includes/ESP8266_klatschschalter_mqtt.h>

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

const byte interruptPin = 13;

volatile byte interruptCounter = 0;
volatile int numberOfInterrupts = 0;
volatile int numberOfKlatsch = 0;
volatile bool radioPower = false;
volatile bool radioMute = false;
 
long mqttConnectionLost = 0;
byte defaultVolume = atoi("7");
char charDefaultVolume[3];
const byte eepromInitialized = 100;

Ticker inputTimer;

ESP8266WebServer httpServer(80);
//ESP8266HTTPUpdateServer httpUpdater;

WiFiClient wifi;
PubSubClient mqtt(wifi);

void ICACHE_RAM_ATTR handleInterrupt() {
  interruptCounter++;
}

void ICACHE_RAM_ATTR handleTicker() {
  numberOfKlatsch = numberOfInterrupts;
  numberOfInterrupts = 0;
  digitalWrite(LED, HIGH);
}

void setup(void){
  pinMode(interruptPin, INPUT);
  pinMode(LED, OUTPUT);
  digitalWrite(LED,HIGH);

  Serial.begin(9600);
  Serial.println();
  Serial.println("Booting Sketch...");

  EEPROM.begin(2);
  if (EEPROM.read(0) == eepromInitialized){
    defaultVolume = EEPROM.read(1);
    Serial.print("Default Volume from EEPROM:");
    Serial.print(defaultVolume);
    itoa(defaultVolume, charDefaultVolume,10);
    Serial.print(" Char: ");
    Serial.println(charDefaultVolume);
  }
  else {
    itoa(defaultVolume, charDefaultVolume,10);
  }
  
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  mqtt.setServer(brocker, 1883);
  mqtt.setCallback(messageReceived);

  wificonnect();
  mqttconnect();

  MDNS.begin(host);

  //Attach handles for different pages.
 // httpUpdater.setup(&httpServer);
  httpServer.on("/", handleRoot);
  httpServer.on("/status",handleStatus);
  httpServer.on("/DEFAULTVOLUME",handleDefaultVolume);
  httpServer.begin();

  MDNS.addService("http", "tcp", 80);

  attachInterrupt(digitalPinToInterrupt(interruptPin), handleInterrupt, RISING);
  timer1_attachInterrupt(handleTicker);
  timer1_enable(TIM_DIV256, TIM_EDGE, TIM_SINGLE);

  Serial.println("Up and running!");
}

void loop(void){
  if(!mqtt.connected()) {
    Serial.println("MQTT connection lost.");
    mqttConnectionLost++;
    mqttconnect();
  }

  httpServer.handleClient();
  mqtt.loop();
  
  if (numberOfKlatsch>0){
    Serial.print("Number of Klatsch: ");
    Serial.println(numberOfKlatsch);
    switch (numberOfKlatsch) {
      case 1:
         Serial.println("Do nothing");
      break;
      
      case 2:
         if(!radioPower) {
            mqtt.publish("radio/power", "on");
            mqtt.publish("radio/volume", "*");
            mqtt.publish("radio/volume", charDefaultVolume);
            radioMute = false;
            radioPower = true;
         }
         else if (radioPower && radioMute){
            mqtt.publish("radio/volume", "*");
            radioMute = false;
         }
         else if (radioPower && !radioMute){
            mqtt.publish("radio/volume","0");
            radioMute = true;
         }
         
      break;

      case 3:
         mqtt.publish("radio/volume", ">>");
      break;

      case 4:
         mqtt.publish("radio/volume", "<");
      break;

      case 5:
         mqtt.publish("radio/power", "off");
      break;
      
      default:
         mqtt.publish("radio/volume", charDefaultVolume);
      break;
    }
    
    numberOfKlatsch=0;
  }

  if(interruptCounter>0){
    if (numberOfInterrupts == 0) {
      mqtt.publish("radio/power", "?");
      mqtt.publish("radio/volume", "??");
      timer1_write(1200000); //3-4s
      digitalWrite(LED, LOW);
    }
 
    interruptCounter--;
    numberOfInterrupts++;
 
    Serial.print("An interrupt has occurred. Total: ");
    Serial.println(numberOfInterrupts);
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
  while (!mqtt.connect(mqttClientId, mqttUser, mqttPass, "clientstatus/Klatschschalter-1",1,1,"OFFLINE")) {
    Serial.print(".");
    delay(500);
  }
  Serial.println("\n MQTT connected!");
  mqtt.publish("clientstatus/Klatschschalter-1", "ONLINE");
  mqtt.subscribe("radio/status/#",1);
}

void handleRoot() {
  String message = "<html><head></head><body><a href='/status'>Status</a><br />\
<form action='/DEFAULTVOLUME' method='post'>\
Default Lautst&auml;rke: <input type='number' min='1' max='12' name='volume' value='"+String(defaultVolume)+"' >\
<input type='submit' value='Default setzen'>\
</form><br />\
</body></html>";

 // httpServer.send(200, "text/plain", "It works!!!");
 // httpServer.send(200, "text/html", "<html><head></head><body><a href='/status'>Status</a><br /><a href='/update'>Update</a></body></html>");
  httpServer.send(200, "text/html", message);
}

void handleStatus() {
  char theStatus[80];
  sprintf(theStatus, "MQTT-Reconnect: %d\n",mqttConnectionLost);
  httpServer.send(200, "text/plain", theStatus);
}

void handleDefaultVolume() {
  if (httpServer.args()>0) {
    for ( uint8_t i = 0; i < httpServer.args(); i++ ) {
      if (httpServer.argName(i) == "volume") {
         // do something here with value from server.arg(i);
         defaultVolume=httpServer.arg(i).substring(0,1).toInt();
         Serial.print("Default Valume from HTTP POST:");
         Serial.print(" Byte: ");
         Serial.print(defaultVolume);
         Serial.print(" String: ");
         Serial.println(httpServer.arg(i));
         EEPROM.write(0, eepromInitialized);
         EEPROM.write(1,defaultVolume);
         EEPROM.commit();
      }
   }
  }
  char theStatus[80];
  sprintf(theStatus, "MQTT-Reconnect: %d\n",mqttConnectionLost);
  httpServer.send(200, "text/plain", theStatus);
}

void messageReceived(char * topic, unsigned char * payload, unsigned int length) {

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
}

