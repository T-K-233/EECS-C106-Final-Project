

#include <Arduino.h>
#include <Adafruit_TinyUSB.h> // for Serial
#include <Servo.h>

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

BlueArrow_A7 servo;

int pos = 0;

void setup() {
  Serial.begin(115200);
  while (!Serial) {}
  
  servo.init(13, A0);
}

void loop() {
  Serial.println("500");
  servo.set(-1);
  for (int i=0; i<100; i+=1) {
    Serial.println(servo.get());
    delay(20);
  }
  
  Serial.println("1000");
  servo.set(-.5);
  for (int i=0; i<100; i+=1) {
    Serial.println(servo.get());
    delay(20);
  }

  Serial.println("1500");
  servo.set(0);
  for (int i=0; i<100; i+=1) {
    Serial.println(servo.get());
    delay(20);
  }

  Serial.println("2000");
  servo.set(.5);
  for (int i=0; i<100; i+=1) {
    Serial.println(servo.get());
    delay(20);
  }

  Serial.println("2500");
  servo.set(1);
  for (int i=0; i<100; i+=1) {
    Serial.println(servo.get());
    delay(20);
  }
}
