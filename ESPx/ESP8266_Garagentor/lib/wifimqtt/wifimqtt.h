#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <PubSubClient.h>

#define garagentorTriggerPin (D1)
#define garagentorMagnetPin  (D2)
#define garagentorStatusPin  (D4) // internal LED

#define topic_status_auto_motion ("home/status/auto/motion")
#define topic_status_wohnzimmer_motion ("home/status/wohnzimmer/motion")
#define topic_status_flur_motion ("home/status/flur/motion")
#define topic_set_garagentor_trigger ("home/set/garage/tor/trigger")
#define topic_status_client_garagentor ("clientstatus/Garagentor")

#define topic_status_wohnzimmer_motion_old ("alarm/wohnzimmer/detected")

#define client_online_message ("ONLINE")
#define client_offline_message ("OFFLINE")

void wificonnect(String ssid, String password);

void mqttconnect(PubSubClient &mqtt, const char *mqttClientId, const char *mqttUser, const char *mqttPass);

void messageReceived(char *topic, unsigned char *payload, unsigned int length);

void blinkStatus();
