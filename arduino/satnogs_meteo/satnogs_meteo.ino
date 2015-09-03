
/*
satnogs-meteo backend
wiring:
1. Barometric BMP180: VCC to 3.3V, SCL to A4 (UNO), SDA to A5 (UNO)
2. Temp & Humidity: DHT22: VCC to 5V SIGNAL to D9
dependencies: dht library & bmp085 library (https://github.com/adafruit/Adafruit-BMP085-Library)

*/

#include "DHT.h"

#define DHTPIN 8
#define DHTTYPE DHT22

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(9600);
  dht.begin();
}

void loop() {

  float h = dht.readHumidity();

  float t = dht.readTemperature();
  if (isnan(h) || isnan(t)) {
    Serial.println("Failed to read from DHT sensor!");
    return;
  }

  //as JSON
  Serial.print(" { 'temp': '");
  Serial.print(t);
  Serial.print("', 'hum': '");
  Serial.print(h);
  Serial.println("' }");
  delay(2000);
  
}
