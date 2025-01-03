#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <PubSubClient.h>

#define autoAlarmPin (D1)
#define wohnzimmerAlarmPin (D2)

#define topic_status_auto_motion ("home/status/auto/motion")
#define topic_status_wohnzimmer_motion ("home/status/wohnzimmer/motion")
#define topic_status_flur_motion ("home/status/flur/motion")
#define topic_status_client_garagentor ("clientstatus/Garagentor")

#define topic_status_wohnzimmer_motion_old ("alarm/wohnzimmer/detected")

#define client_online_message ("ONLINE")
#define client_offline_message ("OFFLINE")

void wificonnect(String ssid, String password);

void mqttconnect(PubSubClient &mqtt, const char *mqttClientId, const char *mqttUser, const char *mqttPass);

void messageReceived(char *topic, unsigned char *payload, unsigned int length);

extern bool wohnzimmerAlarm;
extern bool autoAlarm;
