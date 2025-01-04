#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <PubSubClient.h>

#define garagentorTriggerPin (D1)
#define garagentorMagnetPin (D2)
#define garagentorStatusPin (D4) // internal LED

// Küche
#define topic_status_kueche_motion ("home/status/kueche/motion")
#define topic_status_kueche_temperatur ("home/status/kueche/temperatur")
#define topic_status_kueche_helligkeit ("home/status/kueche/helligkeit")

// Wohnzimmer
#define topic_status_wohnzimmer_motion ("home/status/wohnzimmer/motion")
#define topic_status_wohnzimmer_temperatur ("home/status/wohnzimmer/temperatur")
#define topic_status_wohnzimmer_helligkeit ("home/status/wohnzimmer/helligkeit")

// Flur
#define topic_status_flur_motion ("home/status/flur/motion")
#define topic_status_flur_will ("clientstatus/RFIDReader")

// Garage, Garagentor
#define topic_set_garagentor_trigger ("home/set/garage/tor/trigger")
#define topic_status_garagentor_status ("home/status/garage/tor/status") // offen, geschlossen per Magnetkontakt o.ä.
#define topic_status_garagentor_will ("clientstatus/Garagentor")
#define topic_status_garage_motion ("home/status/garage/motion")
#define topic_status_garage_temperatur ("home/status/garage/temperatur")

#define topic_status_wohnzimmer_motion_old ("alarm/wohnzimmer/detected")

#define client_online_message ("ONLINE")
#define client_offline_message ("OFFLINE")

void wificonnect(String ssid, String password);
void mqttconnect(PubSubClient &mqtt, const char *mqttClientId, const char *mqttUser, const char *mqttPass);
void messageReceived(char *topic, unsigned char *payload, unsigned int length);
void blinkStatus();
extern String currentTime();
