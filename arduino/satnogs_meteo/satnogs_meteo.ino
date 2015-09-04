
/*
satnogs-meteo backend
wiring:
1. Barometric BMP180: VCC to 3.3V, SCL to A4 (UNO), SDA to A5 (UNO)
2. Temp & Humidity: DHT22: VCC to 5V SIGNAL to D9
dependencies: found under ./arduino/third-party
*/

#include "SFE_BMP180.h"
#include <Wire.h>
#include "DHT.h"

#define DHTPIN 8
#define DHTTYPE DHT22
#define PRES_RES 1

DHT dht(DHTPIN, DHTTYPE);
SFE_BMP180 bmp;

void setup() {
  Serial.begin(9600);
  dht.begin();
    if (bmp.begin()) {}
  else
  {
    while(1) {}; 
  }
}
  
void loop() {
  double p;
  char bmpstatus;
  float h = dht.readHumidity();
  float t = dht.readTemperature();
  if (isnan(h) || isnan(t)) {
    Serial.println("Failed to read from DHT sensor!");
    return;
  }
  bmpstatus = bmp.startPressure(PRES_RES);
  if (bmpstatus!=0) {
  	delay(bmpstatus);
  	bmp.getPressure(p, (double&)t); //use temp measured by dht22
  }

  //as JSON
  Serial.print(" { \"temp\": \"");
  Serial.print(t);
  Serial.print("\", \"hum\": \"");
  Serial.print(h);
  Serial.print("\", \"pres\" \"");
  Serial.print(p);
  Serial.println("' }");
  delay(2000);
  
}
