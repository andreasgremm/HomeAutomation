#include <Arduino.h>
#include <httpserver.h>
#include <FS.h>        // File System for Web Server Files
#include <LittleFS.h> 

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
    String message = F("<!DOCTYPE html>\
<html lang=de><head>\
<link rel='apple-touch-icon' sizes='57x57' href='/apple-icon-57x57.png'>\
<link rel='apple-touch-icon' sizes='60x60' href='/apple-icon-60x60.png'>\
<link rel='apple-touch-icon' sizes='72x72' href='/apple-icon-72x72.png'>\
<link rel='apple-touch-icon' sizes='76x76' href='/apple-icon-76x76.png'>\
<link rel='apple-touch-icon' sizes='114x114' href='/apple-icon-114x114.png'>\
<link rel='apple-touch-icon' sizes='120x120' href='/apple-icon-120x120.png'>\
<link rel='apple-touch-icon' sizes='144x144' href='/apple-icon-144x144.png'>\
<link rel='apple-touch-icon' sizes='152x152' href='/apple-icon-152x152.png'>\
<link rel='apple-touch-icon' sizes='180x180' href='/apple-icon-180x180.png'>\
<link rel='icon' type='image/png' sizes='192x192'  href='/android-icon-192x192.png'>\
<link rel='icon' type='image/png' sizes='32x32' href='/favicon-32x32.png'>\
<link rel='icon' type='image/png' sizes='96x96' href='/favicon-96x96.png'>\
<link rel='icon' type='image/png' sizes='16x16' href='/favicon-16x16.png'>\
<link rel='icon' type='image/vnd.microsoft.icon' href='/favicon.ico'>\
<link rel='manifest' href='/manifest.json'>\
<meta name='msapplication-TileColor' content='#ffffff'>\
<meta name='msapplication-TileImage' content='/ms-icon-144x144.png'>\
<style>table, th, td {border: 1px solid black;}</style><title>Garagentor</title>\
<meta name='viewport' content='width=device-width, initial-scale=1'>\
<meta http-equiv='refresh' content='10'>\
</head><body>\
<h4>Uhrzeit: ") + currentTime() +
                     F("</h4>\
<br />Garagentor ausl&ouml;sen: <a href='/trigger'><button class='button'>Trigger</button></a><br /><br />\
<br /><table><caption>Garagentor Status</caption><tr><th>Letzter Trigger</th><th>Torstatus</th></tr>\
<tr><td><center>") + lastTrigger +
                     F("</center></td><td><center>") + storstatus + F("</center></td></tr>\
</table><br />\
<br /><table>\
<tr><td><center>Temperatur &ordm;C</center></td><td><center>") +
                     tempC + F("</center></td></tr>\
</table><br />\
<a href='/status'>Status</a><br />\
<a href='/update'>Update</a><br />\
</body></html>");
    httpServer.sendHeader("Cache-Control", "no-cache");
    httpServer.send(200, "text/html", message);
}

void handleStatus()
{

    byte mac[6];
    String smac;

    WiFi.macAddress(mac);
    smac = macToString(mac);

    FSInfo fs_info;
    LittleFS.info(fs_info);

    String theStatus = F("<!DOCTYPE html>\
<html lang=de><head><style>table, th, td {border: 1px solid black;}</style>\
<link rel='apple-touch-icon' sizes='57x57' href='/apple-icon-57x57.png'>\
<link rel='apple-touch-icon' sizes='60x60' href='/apple-icon-60x60.png'>\
<link rel='apple-touch-icon' sizes='72x72' href='/apple-icon-72x72.png'>\
<link rel='apple-touch-icon' sizes='76x76' href='/apple-icon-76x76.png'>\
<link rel='apple-touch-icon' sizes='114x114' href='/apple-icon-114x114.png'>\
<link rel='apple-touch-icon' sizes='120x120' href='/apple-icon-120x120.png'>\
<link rel='apple-touch-icon' sizes='144x144' href='/apple-icon-144x144.png'>\
<link rel='apple-touch-icon' sizes='152x152' href='/apple-icon-152x152.png'>\
<link rel='apple-touch-icon' sizes='180x180' href='/apple-icon-180x180.png'>\
<link rel='icon' type='image/png' sizes='192x192'  href='/android-icon-192x192.png'>\
<link rel='icon' type='image/png' sizes='32x32' href='/favicon-32x32.png'>\
<link rel='icon' type='image/png' sizes='96x96' href='/favicon-96x96.png'>\
<link rel='icon' type='image/png' sizes='16x16' href='/favicon-16x16.png'>\
<link rel='icon' type='image/vnd.microsoft.icon' href='/favicon.ico'>\
<link rel='manifest' href='/manifest.json'>\
<meta name='msapplication-TileColor' content='#ffffff'>\
<meta name='msapplication-TileImage' content='/ms-icon-144x144.png'>\
<meta name='viewport' content='width=device-width, initial-scale=1'>\
<title>Garagentor</title></head><body>\
<table><caption>Network Attributes</caption><tr><th>Attribut</th><th>Wert</th></tr>\
<tr><td>Host-Name</td><td><b>") +
                       hostname + F("</b></td></tr>\
<tr><td>Connected-To</td><td><b>") +
                       WiFi.SSID() + F("</b></td></tr>\
<tr><td>RSSI</td><td><b>") +
                       WiFi.RSSI() + F("</b></td></tr>\
<tr><td>MAC-Adresse</td><td><b>") +
                       smac + F("</b></td></tr>\
<tr><td>IP-Adresse</td><td><b>") +
                       WiFi.localIP().toString().c_str() + F("</b></td></tr>\
<tr><td>Subnet Mask</td><td><b>") +
                       WiFi.subnetMask().toString().c_str() + F("</b></td></tr>\
<tr><td>Gateway-IP</td><td><b>") +
                       WiFi.gatewayIP().toString().c_str() + F("</b></td></tr>\
<tr><td>SoftAP-SSID</td><td><b>") +
                       WiFi.softAPSSID() + F("</b></td></tr>\
<tr><td>SoftAP-IP</td><td><b>") +
                       WiFi.softAPIP().toString().c_str() + F("</b></td></tr>\
<tr><td>flashSize</td><td><b>") +
                       String(ESP.getFlashChipSize()) + F("</b></td></tr>\
<tr><td>freeHeap</td><td><b>") +
                       String(ESP.getFreeHeap()) + F("</b></td></tr>\
<tr><td>fsTotalBytes</td><td><b>") +
                       String(fs_info.totalBytes) + F("</b></td></tr>\
<tr><td>fsUsedBytes</td><td><b>") +
                       String(fs_info.usedBytes) + F("</b></td></tr>\
</table><br />") + F("\
<a href='/'>Startseite</a></body></html>");
    httpServer.sendHeader("Cache-Control", "no-cache");
    httpServer.send(200, "text/html", theStatus);
}

void handleTrigger()
{
    String theStatus = F("<!DOCTYPE html>\
<html lang=de><head><style>table, th, td {border: 1px solid black;}</style>\
<link rel='apple-touch-icon' sizes='57x57' href='/apple-icon-57x57.png'>\
<link rel='apple-touch-icon' sizes='60x60' href='/apple-icon-60x60.png'>\
<link rel='apple-touch-icon' sizes='72x72' href='/apple-icon-72x72.png'>\
<link rel='apple-touch-icon' sizes='76x76' href='/apple-icon-76x76.png'>\
<link rel='apple-touch-icon' sizes='114x114' href='/apple-icon-114x114.png'>\
<link rel='apple-touch-icon' sizes='120x120' href='/apple-icon-120x120.png'>\
<link rel='apple-touch-icon' sizes='144x144' href='/apple-icon-144x144.png'>\
<link rel='apple-touch-icon' sizes='152x152' href='/apple-icon-152x152.png'>\
<link rel='apple-touch-icon' sizes='180x180' href='/apple-icon-180x180.png'>\
<link rel='icon' type='image/png' sizes='192x192'  href='/android-icon-192x192.png'>\
<link rel='icon' type='image/png' sizes='32x32' href='/favicon-32x32.png'>\
<link rel='icon' type='image/png' sizes='96x96' href='/favicon-96x96.png'>\
<link rel='icon' type='image/png' sizes='16x16' href='/favicon-16x16.png'>\
<link rel='icon' type='image/vnd.microsoft.icon' href='/favicon.ico'>\
<link rel='manifest' href='/manifest.json'>\
<meta name='msapplication-TileColor' content='#ffffff'>\
<meta name='msapplication-TileImage' content='/ms-icon-144x144.png'>\
<meta name='viewport' content='width=device-width, initial-scale=1'>\
<title>Garagentor</title></head><body>\
<h4>Garagentor ausgel&ouml;st!</h4>\
<a href='/'>Startseite</a><br />\
</body></html>");
    lastTrigger = "WebTrigger ( " + currentTime() + " ) ";
    doTrigger();
    httpServer.send(200, "text/html", theStatus);
}
