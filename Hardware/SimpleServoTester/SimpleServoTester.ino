// running on Arduino UNO

//#include <Arduino.h>
//#include <Adafruit_TinyUSB.h> // for Serial

#include <Servo.h>

Servo myservo;  // create servo object to control a servo
// twelve servo objects can be created on most boards

int pos = 0;    // variable to store the servo position

void setup() {
  Serial.begin(115200);
  myservo.attach(9);  // attaches the servo on pin 9 to the servo object
}

void loop() {
  int val = 0;

  while (Serial.available() > 0) {
    val = Serial.parseInt();
    while (Serial.read() != -1) {}
    myservo.writeMicroseconds(1500 + val);
    Serial.println(1500 + val);
  }
}
