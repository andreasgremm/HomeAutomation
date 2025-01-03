#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <PubSubClient.h>
#include <wifimqtt.h>

void wificonnect(String ssid, String password)
{
    while (WiFi.waitForConnectResult() != WL_CONNECTED)
    {
        WiFi.begin(ssid, password);
        Serial.println("WiFi failed, retrying.");
        delay(500);
    }

    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());

    Serial.println("\n WiFi connected!");
}

void mqttconnect(PubSubClient &mqtt, const char *mqttClientId, const char *mqttUser, const char *mqttPass)
{
    while (!mqtt.connect(mqttClientId, mqttUser, mqttPass, topic_status_client_garagentor, 1, true, client_offline_message))
    {
        Serial.print("-");
        delay(500);
    }
    Serial.println("\n MQTT connected!");
    mqtt.subscribe(topic_status_auto_motion);
    mqtt.subscribe(topic_set_garagentor_trigger);
    mqtt.subscribe(topic_status_wohnzimmer_motion_old);
    mqtt.publish(topic_status_client_garagentor, client_online_message, true);
}

void messageReceived(char *topic, unsigned char *payload, unsigned int length)
{

    Serial.print("incoming: ");
    Serial.print(topic);
    Serial.print(" - ");
    for (byte i = 0; i < length; i++)
    {
        Serial.print((const char)payload[i]);
    }
    Serial.println("");

    if (strcmp(topic, topic_set_garagentor_trigger) == 0)
    {
        if (strncmp((const char *)payload, "True", length) == 0)
        {
            digitalWrite(garagentorTriggerPin, HIGH);
            delay(500);
            digitalWrite(garagentorTriggerPin, LOW);
        }
    }
}

void blinkStatus()
{
    digitalWrite(garagentorStatusPin, !(digitalRead(garagentorStatusPin))); // Invert Current State of LED
}
