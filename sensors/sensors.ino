#define DHT11_PIN 7
#include <LiquidCrystal.h>
#include "dht.h"
dht           DHT;
char          buff[32];
char          str_temp[8];
float         f;
int           chk;
int           red_pin = 13;
int           green_pin = 9;
int           count = -1;
unsigned long interval = 10000;
unsigned long prev_millis = 0;

// initialize the library with the numbers of the interface pins
LiquidCrystal lcd(12, 11, 5, 4, 3, 2);

void setup() {
  // set up the LCD's number of columns and rows:
  Serial.begin(9600);
  lcd.begin(16, 2);
  lcd.print("Initialized...");
  delay(2000);
  pinMode(red_pin, OUTPUT);
  pinMode(green_pin, OUTPUT);
}

void loop() {
  // set the cursor to column 0, line 1
  // (note: line 1 is the second row, since counting begins with 0):
  unsigned long curr_millis = millis();

  if ((unsigned long)(curr_millis - prev_millis) >= interval)
  {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Project Green");
    lcd.setCursor(4, 1);
    lcd.print("Light");
    delay(5000);
    prev_millis = millis();
  } 
  chk = DHT.read11(DHT11_PIN);
  if (DHT.humidity == -999 || DHT.temperature == -999)
  {
    Serial.println("Failed to read from DHT sensor!");
    return;
  }
  lcd.setCursor(0, 1);
  lcd.print("Humidity:    ");
  lcd.print((int)DHT.humidity);
  lcd.print("%");
  lcd.setCursor(0, 0);
  lcd.print("Temperature: ");
  lcd.print((int)(DHT.temperature * 9.0/5.0 + 32.0));
  lcd.print("F");
  if (DHT.humidity >= 71 || DHT.humidity <= 49)
  {
    analogWrite(red_pin, 255);
    analogWrite(green_pin, 0);
  }
  else
  {
    analogWrite(red_pin, 0);
    analogWrite(green_pin, 255);
  }
//  delay(10000);
  Serial.print("Humidity: ");
  Serial.print(DHT.humidity);

  f = DHT.temperature * 9.0/5.0 + 32.0;
  Serial.print(",Temperature: ");
  Serial.print(f);
  Serial.print("\n");

  delay(2000);
}
