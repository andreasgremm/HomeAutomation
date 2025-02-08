#include <Arduino.h>
#include <ESP8266WebServer.h>

String ipToString(IPAddress ip);
String macToString(byte mac[6]);
String currentTime();
void handleStatus();
void handleRoot();
void handleTrigger();
void doTrigger();

extern String hostname;
extern ESP8266WebServer httpServer;
extern String lastTrigger;
extern volatile bool torStatus;
extern volatile float tempC;
