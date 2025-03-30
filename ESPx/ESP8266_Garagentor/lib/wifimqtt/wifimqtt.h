#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <PubSubClient.h>

#include </Users/andreas/Documents/git-github/HomeAutomation/ESPx/ESP_MQTT_Definitions.h>

#define HAVE_NETDUMP 0
#include <lwip/napt.h>
#include <lwip/dns.h>

#define TRACE(...) Serial.printf(__VA_ARGS__)

#define NAPT 1000
#define NAPT_PORT 10

#ifndef STASSID
#define STASSID "garagentor"
#define STAPSK "Not used"
#endif

#define garagentorTriggerPin (D1) // Relaisanschluss
#define garagentorMagnetPin (D2)  // Magnetschalter
#define garagentorStatusPin (D4)  // internal LED zur Statusanzeige des Systems
#define garagentorMotionPin (D5)  // Bewegungsmelder 

void wificonnect(String ssid, String password);
void mqttconnect(PubSubClient &mqtt, const char *mqttClientId, const char *mqttUser, const char *mqttPass);
void messageReceived(char *topic, unsigned char *payload, unsigned int length);
void blinkStatus();
void doTrigger();
void readTemperature();
IRAM_ATTR void torInterrupt();
IRAM_ATTR void motionInterrupt();
extern String currentTime();
extern volatile float tempC;
/// @brief torStatus = True => Geschlossen, torStatus = False => Geöffnet
extern volatile bool torStatus;
extern PubSubClient mqtt;
extern String hostname;
