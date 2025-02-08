#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <PubSubClient.h>

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

// Küche
#define topic_status_kueche_motion ("home/kueche/motion/state")
#define topic_status_kueche_temperatur ("home/kueche/temperatur/state")
#define topic_status_kueche_helligkeit ("home/kueche/helligkeit/state")

// Wohnzimmer
#define topic_status_wohnzimmer_motion ("home/wohnzimmer/motion/state")
#define topic_status_wohnzimmer_temperatur ("home/wohnzimmer/temperatur/state")
#define topic_status_wohnzimmer_helligkeit ("home/wohnzimmer/helligkeit/state")

// Flur
#define topic_status_flur_motion ("home/flur/motion/state")
#define topic_status_flur_will ("clientstatus/RFIDReader")

// Garage, Garagentor
#define topic_set_garagentor_trigger ("home/garage/tor/set")
#define topic_status_garagentor_status ("home/garage/tor/state") // offen, geschlossen per Magnetkontakt o.ä.
#define topic_status_garagentor_will ("clientstatus/Garagentor")
#define topic_status_garage_motion ("home/garage/motion/state")
#define topic_status_garage_temperatur ("home/garage/temperatur/state")

#define topic_status_wohnzimmer_motion_old ("alarm/wohnzimmer/detected")

#define client_online_message ("ONLINE")
#define client_offline_message ("OFFLINE")

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
