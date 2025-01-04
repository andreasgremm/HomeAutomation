#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <httpserver.h>

String ipToString(IPAddress ip)
{
    String s = "";
    for (int i = 0; i < 4; i++)
        s += i ? "." + String(ip[i]) : String(ip[i]);
    return s;
}

String macToString(byte mac[6])
{
    String s = "";
    for (byte i = 0; i < 6; i++)
    {
        char buf[3];
        sprintf(buf, "%.2X", mac[i]);
        s += buf;
        if (i < 5)
            s += ':';
    }
    return s;
}

String currentTime()
{
    time_t tnow = time(nullptr);
    return ctime(&tnow);
}

void handleRoot()
{
    String storstatus = torStatus ? "<font color='green'>Geschlossen</font>" : "<font color='red'>Ge&ouml;ffnet</font>";
    String message = "<html><head><style>table, th, td {border: 1px solid black;}</style><title>Garagentor</title>\
<meta http-equiv='refresh' content='10'></head><body>\
<h4>Uhrzeit: " + currentTime() +
                     "</h4>\
<br /><table><caption>Garagentor Status</caption><tr><th>Letzter Trigger</th><th>Torstatus</th></tr>\
<tr><td><center>" + lastTrigger + "</center></td><td><center>" + storstatus + "</center></td></tr>\
</table><br />\
<a href='/status'>Status</a><br />\
<a href='/update'>Update</a><br />\
</body></html>";

    httpServer.send(200, "text/html", message);
}

void handleStatus()
{

    byte mac[6];
    String smac;

    WiFi.macAddress(mac);
    smac = macToString(mac);

    String theStatus = "<html><head><style>table, th, td {border: 1px solid black;}</style>\
<title>Garagentor</title></head><body>\
<table><caption>Network Attributes</caption><tr><th>Attribut</th><th>Wert</th></tr>\
<tr><td>Host-Name</td><td><b>" +
                       hostname + "</b></td></tr>\
<tr><td>MAC-Adresse</td><td><b>" +
                       smac + "</b></td></tr>\
<tr><td>IP-Adresse</td><td><b>" +
                       ipToString(WiFi.localIP()) + "</b></td></tr>\
<tr><td>Subnet Mask</td><td><b>" +
                       ipToString(WiFi.subnetMask()) + "</b></td></tr>\
<tr><td>Gateway-IP</td><td><b>" +
                       ipToString(WiFi.gatewayIP()) + "</b></td></tr>\
</table><br />" + "\
<a href='/'>Startseite</a></body></html>";

    httpServer.send(200, "text/html", theStatus);
}
