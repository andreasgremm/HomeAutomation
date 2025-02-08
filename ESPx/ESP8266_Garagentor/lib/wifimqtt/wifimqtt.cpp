#include <Arduino.h>
#include <wifimqtt.h>

#if HAVE_NETDUMP

#include <NetDump.h>

void dump(int netif_idx, const char* data, size_t len, int out, int success) {
  (void)success;
  Serial.print(out ? F("out ") : F(" in "));
  Serial.printf("%d ", netif_idx);

  // optional filter example: if (netDump_is_ARP(data))
  {
    netDump(Serial, data, len);
    // netDumpHex(Serial, data, len);
  }
}
#endif

String lastTrigger = "None";
const int pinA0 = A0;
const String offen = "Geöffnet";
const String geschlossen = "Geschlossen";

void wificonnect(String ssid, String password)
{

    // WiFi.printDiag(Serial);
    WiFi.setOutputPower(20.5);  // Sets WiFi RF power output to highest level, highest RF power usage
    WiFi.setHostname((const char*) hostname.c_str()); // allow to address the device by the given name
    WiFi.begin();
    WiFi.waitForConnectResult();

    if (WiFi.status() != WL_CONNECTED)
    {
        TRACE("Prepare WiFi\n"); // start WiFI
        WiFi.persistent(true);
        WiFi.setPhyMode(WIFI_PHY_MODE_11N); // Set radio type to N
        WiFi.mode(WIFI_STA);
        WiFi.setAutoReconnect(true);
        WiFi.setAutoConnect(true);
        TRACE("Wifi Begin (ssid)\n");
        WiFi.begin(ssid, password);
        WiFi.persistent(false);
        delay(1000);
        WiFi.waitForConnectResult();
    }

    while (WiFi.status() != WL_CONNECTED)
    {
        delay(500);
        TRACE(".");
    }
    TRACE("connected.\n");

    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
    Serial.println("\n WiFi connected!");
}

void mqttconnect(PubSubClient &mqtt, const char *mqttClientId, const char *mqttUser, const char *mqttPass)
{
    while (!mqtt.connect(mqttClientId, mqttUser, mqttPass, topic_status_garagentor_will, 1, true, client_offline_message))
    {
        Serial.println("MQTT failed, retrying.");
        delay(500);
    }
    Serial.println("\n MQTT connected!");
    mqtt.subscribe(topic_set_garagentor_trigger);
    mqtt.publish(topic_status_garagentor_will, client_online_message, true);
}

void messageReceived(char *topic, unsigned char *payload, unsigned int length)
{
    Serial.print("incoming: ");
    Serial.print(topic);
    Serial.print(" - ");
    for ( byte i = 0; i < length; i++)
    {
        Serial.print((const char)payload[i]);
    }
    Serial.println("");

    if (strcmp(topic, topic_set_garagentor_trigger) == 0)
    {
        // lastTrigger = FromUnsignedCharP(payload);
        lastTrigger = String((char *) payload).substring(0, length) + " ( " + currentTime() + " ) ";
        doTrigger();
    }
}

void blinkStatus()
{
    digitalWrite(garagentorStatusPin, !(digitalRead(garagentorStatusPin))); // Invert Current State of LED
}

void readTemperature()
{
    char msg[5];
    float spannungA0 = analogRead(pinA0) * 3000.0 / 1024.0;
    tempC = (spannungA0 - 500) / 10;
    sprintf(msg, "%2.1f", tempC);
    mqtt.publish(topic_status_garage_temperatur, (const char*)msg, false);
}

ICACHE_RAM_ATTR void torInterrupt()
{
    torStatus = !digitalRead(garagentorMagnetPin);
    String storStatus = torStatus? geschlossen : offen ;
    char ctorStatus[storStatus.length() + 1];
    strcpy(ctorStatus, storStatus.c_str());
    mqtt.publish(topic_status_garagentor_status, (const char*)ctorStatus, false);
}

ICACHE_RAM_ATTR void motionInterrupt()
{
    char msg[14];
    bool motionStatus = digitalRead(garagentorMotionPin);
    sprintf(msg, "{\"Motion\": %1i}", motionStatus);
    mqtt.publish(topic_status_garage_motion, (const char*)msg, false);
}