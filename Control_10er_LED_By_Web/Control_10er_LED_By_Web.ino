#include <ESP8266WiFi.h>
#include <OneWire.h>
#include <DallasTemperature.h>
// Remove this include which sets the below constants to my own conveniance
#include </Users/andreas/Documents/git-github/non-git-local-includes/Control_10er_LED_By_Web.h>

/*
const char* ssid = "<ssid>";
const char* password = "<password for ssid>";
 */

int countPin = D7; // GPIO13
int resetPin = D6; // GPIO12
int activatePin = D1; // GPIO5
int manuellPin = D2; // GPIO4
int tempPin = D5; // GPIO14
int flashPin = D3; // GPIO16
int internalLED = D4; // GPIO2

int wuerfel;
int randval;
int volatile activate;
int volatile showtemp=LOW;

float temperature;
int zehner,einer,nachkomma;
int showTime=500;

unsigned long previousMillis = 0;  // will store last time Temperature was updated
unsigned long currentMillis;
const long interval = 60000;        // interval at which to ask Temp-Sensor (milliseconds)
const long timerInterval = 10000;   // If you want to set a timer this is the interval to check
bool timerSet = false;
int timerValueStart;
int timerValueEnd;
unsigned long timerValue;
String timerValueString;
unsigned long timerBaseMillis;
long timerNextLed;

OneWire ds(tempPin);
DallasTemperature sensors(&ds);
WiFiServer server(80);

void setup() {
  Serial.begin(115200);
  delay(10);

  pinMode(countPin, OUTPUT);
  pinMode(resetPin, OUTPUT);
  pinMode(activatePin, OUTPUT);
  pinMode(internalLED, OUTPUT);
  pinMode(manuellPin, INPUT);
  pinMode(flashPin, INPUT);

  randomSeed(analogRead(A0));
  attachInterrupt(manuellPin, interruptCallback, FALLING);
  attachInterrupt(flashPin, startTempCallback, FALLING);

  //initTemp();
  sensors.begin();

  // Reset counter at startup
  activate = hardreset(HIGH);

  // Connect to WiFi network
  Serial.println();
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");

  // Start the server
  server.begin();
  Serial.println("Server started");

  // Print the IP address
  Serial.print("Use this URL to connect: ");
  Serial.print("http://");
  Serial.print(WiFi.localIP());
  Serial.println("/");
  temperature = getTemperature();
}

void loop() {

  currentMillis = millis();
  if (abs(currentMillis - previousMillis) >= interval) {
    // save time
    previousMillis = currentMillis;
    temperature = getTemperature();
  }

  if (timerSet && (abs(currentMillis - timerBaseMillis) >= timerValue)) {
    Serial.print(" Timer finished: ");
    Serial.println(currentMillis - timerBaseMillis);
    digitalWrite(internalLED, HIGH);
    timerSet = false;
  }

  if (timerSet && (currentMillis >= timerNextLed)){
    timerNextLed += timerValue / 10;
    Serial.print(" < ");
    Serial.println(timerNextLed);
    count(1);
  }
  
  // Check if a client has connected
  WiFiClient client = server.available();
  if (!client) {
    if (showtemp) {
      zehner = int(temperature/10);
      einer=10-(int(temperature) % 10);
      nachkomma=10-map(int(temperature*100) % 100, 0, 100, 0,9);
      //Serial.println(i);
      showLeft(zehner, showTime*4, 0);
      //Serial.println(j);
      showRight(einer, showTime,0);
      //Serial.println(k);
      showRight(nachkomma, showTime, 1);
    }

    return;
  }

  // Wait until the client sends some data
  Serial.println("new client");
  while(!client.available()){
    delay(1);
  }

  // Read the first line of the request
  String request = client.readStringUntil('\r');
  Serial.println(request);
  client.flush();

  // Match the request
  if (request.indexOf("/ACTIVATE=ON") != -1)  {
    digitalWrite(activatePin, LOW);
    activate = LOW;
  }
  if (request.indexOf("/ACTIVATE=OFF") != -1)  {
    digitalWrite(activatePin, HIGH);
    activate = HIGH;
  }
  if (request.indexOf("/TIMER") != -1)  {
    timerValueString = "";
    timerValueStart=request.indexOf("=")+1;
    timerValueEnd=request.lastIndexOf(" ");
    Serial.print(" Timer: ");
    for (int i = timerValueStart; i < timerValueEnd; i++){
      if (isDigit(request[i])) {
        timerValueString += request[i];
      }
    }
    timerValue = timerValueString.toInt()*60*1000;
    if (timerValue > 0) {
      activate = hardreset(HIGH);
      Serial.print(timerValue);
      Serial.print(" : ");
      timerSet = true;
      timerBaseMillis = millis();
      Serial.print(timerBaseMillis);
      timerNextLed = timerBaseMillis + timerValue / 10;
      Serial.print(" < ");
      Serial.println(timerNextLed);
    }

  }
  
  if (request.indexOf("/RESET") != -1)  {
    activate = hardreset(HIGH);
  }
  if (request.indexOf("/WUERFEL") != -1)  {
    activate = hardreset(HIGH);
    wuerfel = random(0,6);
    count(wuerfel);
  }
  if (request.indexOf("/RANDOM") != -1)  {
    activate = hardreset(HIGH);
    randval = random(0,100);
    count(randval);
  }
  if (request.indexOf("/SHOWTEMP") != -1)  {
    activate = hardreset(showtemp);
    showtemp=HIGH;
  }

  // Return the response
  client.println("HTTP/1.1 200 OK");
  client.println("Content-Type: text/html");
  client.println(""); //  do not forget this one
  client.println("<!DOCTYPE HTML>");
  client.println("<html>");
  client.print("Die Temperatur betr&auml;gt: ");
  client.print("<a href=\"/SHOWTEMP\"\"><button>");
  client.print(temperature);
  client.print("</button></a>");
  client.println("<br><br>");

  client.print("Activate ist: ");
  if(activate == LOW) {
    client.print("On");
  } else {
    client.print("Off");
  }
  client.println("<br><br>");

  client.println("<a href=\"/ACTIVATE=ON\"\"><button>Turn On </button></a>");
  client.println("<a href=\"/ACTIVATE=OFF\"\"><button>Turn Off </button></a><br />");
  client.println("<br><br>");
  client.println("<a href=\"/WUERFEL\"\"><button>W&uuml;rfel </button></a><br />");
  client.println("<br><br>");
  client.println("<a href=\"/RANDOM\"\"><button>Random 1-99</button></a><br />");
  client.println("<br><br>");
  client.println("<a href=\"/RESET\"\"><button>Reset </button></a><br />");

  client.println("<form action='/TIMER' method='get'>");
  client.println("Zeit in Minuten:");
  client.println("<input type='number' name='quantity' value='0' >");
  client.println("<input type='submit' value='Timer setzen'>");
  client.println("</form><br />");

  client.println("</html>");

  delay(1);
  Serial.println("Client disonnected");
  Serial.println("");

}

void interruptCallback() {
  Serial.println("manuelle Übernahme");
  activate=softreset(HIGH);
}

void startTempCallback() {
  Serial.println("manuelle Temperaturanzeige");
  activate = hardreset(showtemp);
  showtemp=HIGH;
}

float getTemperature() {
    sensors.requestTemperatures();
    float temp = sensors.getTempCByIndex(0);
    Serial.print("Temperature is: ");
    Serial.println(temp);
    // Why "byIndex"? You can have more than one IC on the same bus.
    // 0 refers to the first IC on the wire
    return temp;
}
int hardreset(uint8_t resetShowtemp){
  int rvalue = softreset(resetShowtemp);
  digitalWrite(resetPin, LOW);
  delay(0.0001);
  digitalWrite(resetPin, HIGH);

  return rvalue;
}

int softreset(uint8_t resetShowtemp){
  digitalWrite(countPin, HIGH);
  digitalWrite(activatePin, HIGH);
  digitalWrite(internalLED, LOW);
  timerSet = false;

  if (resetShowtemp) {
     showtemp=LOW;
  }

  return HIGH;
}

void count(uint8_t counter) {
  while (counter > 0) {
    digitalWrite(countPin, LOW);
    delay(0.0001);
    digitalWrite(countPin, HIGH);
    counter--;
  }
}

void showRight (byte j, int showTime, byte blinking) {
  int k = showTime;
  while (k > 0 && showtemp) {
    activate=hardreset(LOW);
    count(j);
    delay(1);
    for (int i=j+1; i<10;i++) {
      count(1);
      delay(1);
    }
    k--;
    if (blinking && ((float(k) / 100.0) - int(k / 100)  == 0.0)) {
      delay(100);
    }
  }
}

void showLeft (byte j, int showTime, byte blinking) {
  int k = showTime;
  while (k > 0 && showtemp) {
    activate=hardreset(LOW);
    for (int i=j-1; i>0;i--) {
      count(1);
      delay(1);
    }
    k--;
    if (blinking && ((float(k) / 100.0) - int(k / 100)  == 0.0)) {
      delay(100);
    }
  }
}
