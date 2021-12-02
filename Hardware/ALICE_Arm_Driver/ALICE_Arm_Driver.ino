/* Sweep
 by BARRAGAN <http://barraganstudio.com>
 This example code is in the public domain.

 modified 8 Nov 2013
 by Scott Fitzgerald
 http://www.arduino.cc/en/Tutorial/Sweep
*/

#include <Arduino.h>
#include <Adafruit_TinyUSB.h> // for Serial
#include <Servo.h>

#include "PaleBlue.h"









class BlueArrow_A18 {
  public:
    void init(int pwm_pin, int adc_pin, float center_offset=-.09, float range_offset=.48) {
      analogReference(AR_INTERNAL);
      analogReadResolution(12);
  
      _pwm_pin = pwm_pin;
      _adc_pin = adc_pin;

      _center_offset = center_offset;
      _range_offset = range_offset;
      
      _servo.attach(_pwm_pin);
    }

    float get() {
      float raw_reading = ((float)analogRead(_adc_pin) / 2048.) - 1.;
      raw_reading -= _center_offset;
      raw_reading /= _range_offset;
      return raw_reading;
    }

    void set(float value) {
      _servo.writeMicroseconds(1500 + 1000 * value);
    }

  private:
    int _pwm_pin;
    int _adc_pin;
    float _center_offset;
    float _range_offset;
    Servo _servo;
};


class BlueArrow_A7 {
  public:
    void init(int pwm_pin, int adc_pin, float center_offset=-.07, float range_offset=.61) {
      analogReference(AR_INTERNAL);
      analogReadResolution(12);
  
      _pwm_pin = pwm_pin;
      _adc_pin = adc_pin;

      _center_offset = center_offset;
      _range_offset = range_offset;
      
      _servo.attach(_pwm_pin);
    }

    float get() {
      float raw_reading = ((float)analogRead(_adc_pin) / 2048.) - 1.;
      raw_reading -= _center_offset;
      raw_reading /= _range_offset;
      return raw_reading;
    }

    void set(float value) {
      _servo.writeMicroseconds(1500 + 1000 * value);
    }

  private:
    int _pwm_pin;
    int _adc_pin;
    float _center_offset;
    float _range_offset;
    Servo _servo;
};











uint8_t buffer[128];
float target_angles[] = {0, 0, 0, 0, 0};
float curr_angles[] = {0, 0, 0, 0, 0};

// twelve servo objects can be created on most boards

BlueArrow_A18 servo_0;
BlueArrow_A18 servo_1;
BlueArrow_A7 servo_2;
BlueArrow_A7 servo_3;
BlueArrow_A7 servo_4;


int pos = 0;    // variable to store the servo position

void setup() {
  PaleBlueSerial.init(115200);

  while (!Serial) {}
  
  servo_0.init(13, A0);
  servo_1.init(12, A1);
  servo_2.init(11, A2);
  servo_3.init(10, A3);
  servo_4.init(9, A4);
}

void loop() {
  curr_angles[0] = servo_0.get();
  curr_angles[1] = servo_1.get();
  curr_angles[2] = servo_2.get();
  curr_angles[3] = servo_3.get();
  curr_angles[4] = servo_4.get();
  
  PaleBlueSerial.transmit((uint8_t *)curr_angles, 5 * sizeof(float));
  
  uint16_t recv_size = PaleBlueSerial.receive(buffer, 128);
  
  if (recv_size != 5 * sizeof(float)) {
    return;
  }
  target_angles[0] = *((float *)buffer + 0);
  target_angles[1] = *((float *)buffer + 1);
  target_angles[2] = *((float *)buffer + 2);
  target_angles[3] = *((float *)buffer + 3);
  target_angles[4] = *((float *)buffer + 4);
  
  servo_0.set(target_angles[0]);
  servo_1.set(target_angles[1]);
  servo_2.set(target_angles[2]);
  servo_3.set(target_angles[3]);
  servo_4.set(target_angles[4]);
  delay(10);
}
