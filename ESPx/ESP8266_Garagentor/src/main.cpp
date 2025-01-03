#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <ESP8266WebServer.h>
#include <ESP8266mDNS.h>
#include <ESP8266HTTPUpdateServer.h>
#include <time.h>
#include <TZ.h>
#include <PubSubClient.h>

#include <wifimqtt.h>
#include <httpserver.h>

// Remove this include which sets the below constants to my own conveniance
#include </Users/andreas/Documents/git-github/non-git-local-includes/ESP8266_garagentor_local.h>

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

unsigned long currentMillis;
bool wohnzimmerAlarm = false;
bool autoAlarm = false;
String hostname = host; 


ESP8266WebServer httpServer(80);
ESP8266HTTPUpdateServer httpUpdater;
WiFiClient wifi;
PubSubClient mqtt(wifi);

void setup() {
  Serial.begin(9600);
  Serial.println();
  Serial.println("Booting Sketch...");
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  mqtt.setKeepAlive(60);
  mqtt.setServer(brocker, 1883);
  mqtt.setCallback(messageReceived);

  wificonnect(ssid, password);
  digitalWrite(autoAlarmPin, LOW);

  mqttconnect(mqtt, mqttClientId, mqttUser, mqttPass);
  digitalWrite(wohnzimmerAlarmPin, LOW);

  
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
}

void loop() {
  // put your main code here, to run repeatedly:
  delay(10);
  currentMillis = millis();

  if(!mqtt.connected()) {
    Serial.println("MQTT connection lost.");
    mqttconnect(mqtt, mqttClientId, mqttUser, mqttPass);
  }
  MDNS.update();
  mqtt.loop();
  httpServer.handleClient();
}

