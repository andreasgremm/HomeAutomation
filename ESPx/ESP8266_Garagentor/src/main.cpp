#include <Arduino.h>
#include <WiFiClient.h>
#include <ESP8266mDNS.h>
#include <ESP8266HTTPUpdateServer.h>
#include <time.h>
#include <TZ.h>
#include <Ticker.h>

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
Ticker tmp36;

unsigned long currentMillis;

String hostname = host;
/// @brief Temperatur wird in Ticker tmp36 gesetzt.
volatile float tempC = 0.0;
volatile bool torStatus;

ESP8266WebServer httpServer(80);
ESP8266HTTPUpdateServer httpUpdater;
WiFiClient wifi;
PubSubClient mqtt(wifi);

void setup()
{
  // system_update_cpu_freq(160);
  Serial.begin(115200);
  Serial.println();
  Serial.println("Booting Sketch...");
  pinMode(garagentorTriggerPin, OUTPUT);
  pinMode(garagentorStatusPin, OUTPUT);
  pinMode(garagentorMotionPin, INPUT);
  pinMode(garagentorMagnetPin, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(garagentorMagnetPin), torInterrupt, CHANGE);
  attachInterrupt(digitalPinToInterrupt(garagentorMotionPin), motionInterrupt, CHANGE);

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
  httpServer.on("/trigger",handleTrigger);
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
  tmp36.attach(30.0, readTemperature);
  torStatus = ! digitalRead(garagentorMagnetPin);
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

void doTrigger()
{
  digitalWrite(garagentorTriggerPin, HIGH);
  delay(500);
  digitalWrite(garagentorTriggerPin, LOW);
}