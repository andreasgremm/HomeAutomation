#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <ESP8266WebServer.h>
#include <ESP8266mDNS.h>
#include <ESP8266HTTPUpdateServer.h>
#include <time.h>
#include <TZ.h>
#include <Ticker.h>
#include <PubSubClient.h>

#include <wifimqtt.h>
#include <httpserver.h>

// Remove this include which sets the below constants to my own conveniance
#include </Users/andreas/Documents/git-github/non-git-local-includes/ESPx_wlan.h>
#include </Users/andreas/Documents/git-github/non-git-local-includes/ESPx_mqtt.h>
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

Ticker blinker;

unsigned long currentMillis;
String hostname = host;

ESP8266WebServer httpServer(80);
ESP8266HTTPUpdateServer httpUpdater;
WiFiClient wifi;
PubSubClient mqtt(wifi);

void setup()
{
  Serial.begin(9600);
  Serial.println();
  Serial.println("Booting Sketch...");
  pinMode(garagentorTriggerPin, OUTPUT);
  pinMode(garagentorStatusPin, OUTPUT);
  pinMode(garagentorMagnetPin, INPUT);

  blinker.attach(0.2, blinkStatus);
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  mqtt.setKeepAlive(60);
  mqtt.setServer(brocker, 1883);
  mqtt.setCallback(messageReceived);

  wificonnect(ssid, password);
  mqttconnect(mqtt, mqttClientId, mqttUser, mqttPass);

  // Attach handles for different pages.
  httpUpdater.setup(&httpServer);
  httpServer.on("/", handleRoot);
  httpServer.on("/status", handleStatus);
  httpServer.begin();

  if (MDNS.begin(host))
  {
    MDNS.addService("http", "tcp", 80);
  }
  else
  {
    Serial.println("Error setting up MDNS responder!");
  };
  configTime(TZ_Europe_Berlin, "pool.ntp.org");
  blinker.detach();
  digitalWrite(garagentorStatusPin, HIGH);
}

void loop()
{
  // put your main code here, to run repeatedly:
  delay(10);
  currentMillis = millis();

  if (!mqtt.connected())
  {
    blinker.attach(0.2, blinkStatus);
    mqttconnect(mqtt, mqttClientId, mqttUser, mqttPass);
    blinker.detach();
    digitalWrite(garagentorStatusPin, HIGH);
  }
  MDNS.update();
  mqtt.loop();
  httpServer.handleClient();
}
