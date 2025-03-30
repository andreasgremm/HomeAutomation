#ifndef HTTPSERVER_RFID
#define HTTPSERVER_RFID
#include <Arduino.h>
#include <ESP8266WebServer.h>
#include <SPI.h>
#include <MFRC522.h>

#define SS_PIN D4
#define RST_PIN D3

String ipToString(IPAddress ip);
String macToString(byte mac[6]);
String currentTime();
void handleStatus();
void handleRoot();
void blinkLed(int led, int nr, bool ledstatus);
bool handleRfidStatus();

extern String hostname;
extern ESP8266WebServer httpServer;
extern bool wohnzimmerAlarm;
extern bool autoAlarm;
extern int autoAlarmPin;
extern int wohnzimmerAlarmPin;
extern int irPin;
extern String mfrc522SoftwareVersion;
extern long mqttConnectionLost;
extern String smac;
extern String hostname;

#endif