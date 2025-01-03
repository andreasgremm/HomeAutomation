#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>

String ipToString(IPAddress ip);
String macToString(byte mac[6]);

extern String hostname;

extern ESP8266WebServer httpServer;

void handleStatus();
void handleRoot();
