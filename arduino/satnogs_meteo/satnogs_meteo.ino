
/*
satnogs-meteo backend
wiring:
1. Barometric BMP180: VCC to 3.3V, SCL to A4 (UNO), SDA to A5 (UNO)
2. Temp & Humidity: DHT22: VCC to 5V SIGNAL to D9
dependencies: dht library & bmp085 library (https://github.com/adafruit/Adafruit-BMP085-Library)

*/

#define DHT22_PIN 9
#define DELAY_INTERVAL 1000

#include <Wire.h>
#include <Adafruit_BMP085.h>
#include <dht.h>

dht DHT;
bmp Adafruit_BMP085;

void setup() {
  Serial.begin(115200);
  Serial.println("meteorological station initiated");
  
  if (!bmp.begin()) {
   Serial.println)("could not initialize barometer BMP180");
   while(1) {}
  }
  
}

void print_humidity_and_temperature() {
 int chk = DHT.read22(DHT22_PIN);
 switch(chk) 
 {
 //debug
   case DHTLIB_OK:
   break;
  case DHTLIB_ERROR_CHECKSUM:
   Serial.println("Checksum Error");
   break;
  case DHTLIB_ERROR_TIMEOUT:
   Serial.println("Timeout Error");
   break;
  default:
   Serial.println("Unknown Error");
   break;   
 }
  Serial.print(DHT.temperature);
  Serial.println(" C");
  delay(DELAY_INTERNVAL);
  Serial.print(DHT.humidity);
  Serial.println( " RH");
}

void print_pressure() {
  Serial.print(bmp.readPressure());
  Serial.println(" Pa");
}

void loop() {
 print_humidity_and_temperature();
 delay(DELAY_INTERVAL);
 print_pressure();
 delay(DELAY_INTERVAL);
}
