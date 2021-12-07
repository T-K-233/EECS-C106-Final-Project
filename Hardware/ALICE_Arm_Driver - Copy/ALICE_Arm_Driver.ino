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

//#include "PaleBlue.h"









#include <bluefruit.h>
#include <Adafruit_LittleFS.h>
#include <InternalFileSystem.h>

// BLE Service
BLEDfu  bledfu;  // OTA DFU service
BLEDis  bledis;  // device information
BLEUart bleuart; // uart over ble
BLEBas  blebas;  // battery



void BLE_startAdvertise(void) {
  Bluefruit.Advertising.addFlags(BLE_GAP_ADV_FLAGS_LE_ONLY_GENERAL_DISC_MODE);
  Bluefruit.Advertising.addTxPower();
  Bluefruit.Advertising.addService(bleuart);
  
  Bluefruit.ScanResponse.addName();
  
  Bluefruit.Advertising.restartOnDisconnect(true);
  Bluefruit.Advertising.setInterval(32, 244);    // in unit of 0.625 ms
  Bluefruit.Advertising.setFastTimeout(30);      // number of seconds in fast mode
  Bluefruit.Advertising.start(0);                // 0 = Don't stop advertising after n seconds  
}








#include "Arduino.h"


#define NLSM_END       0x0AU
#define NLSM_ESC       0x0BU
#define NLSM_ESC_END   0x1AU
#define NLSM_ESC_ESC   0x1BU


class PaleBlueBLESerialClass {
  public:
    void init(long baudrate) {
    }
    uint16_t receive(uint8_t *buffer, uint16_t size) {
      uint8_t c;
      uint16_t index = 0;

      while (!bleuart.available()) {}
      c = bleuart.read();
      while (c != NLSM_END) {
        if (c == NLSM_ESC) {
          while (!bleuart.available()) {}
          c = bleuart.read();
          if (c == NLSM_ESC_END) {
            buffer[index] = NLSM_END;
          }
          else if (c == NLSM_ESC_ESC) {
            buffer[index] = NLSM_ESC;
          }
          else {
            buffer[index] = c;
          }
        }
        else {
          buffer[index] = c;
        }
        index += 1;
        while (!bleuart.available()) {}
        c = bleuart.read();
      }
      return index;
    }
    
    void transmit(uint8_t *buffer, uint16_t size) {
      if (size == 0) return ;
      uint8_t c;
      uint16_t index = 0;
      while (index < size) {
        c = buffer[index];
        if (c == NLSM_END) {
          c = NLSM_ESC;
          bleuart.write(c);
          c = NLSM_ESC_END;
          bleuart.write(c);
        }
        else if (c == NLSM_ESC) {
          c = NLSM_ESC;
          bleuart.write(c);
          c = NLSM_ESC_ESC;
          bleuart.write(c);
        }
        else {
          bleuart.write(c);
        }
        index += 1;
      }
      c = NLSM_END;
      bleuart.write(c);
    }
};

PaleBlueBLESerialClass PaleBlueSerial;















/*************************************************** 
  This is an example for our Adafruit 16-channel PWM & Servo driver
  Servo test - this will drive 8 servos, one after the other on the
  first 8 pins of the PCA9685

  Pick one up today in the adafruit shop!
  ------> http://www.adafruit.com/products/815
  
  These drivers use I2C to communicate, 2 pins are required to  
  interface.

  Adafruit invests time and resources providing this open source code, 
  please support Adafruit and open-source hardware by purchasing 
  products from Adafruit!

  Written by Limor Fried/Ladyada for Adafruit Industries.  
  BSD license, all text above must be included in any redistribution
 ****************************************************/

#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver(0x40, Wire);

#define SERVOMIN  150 // This is the 'minimum' pulse length count (out of 4096)
#define SERVOMAX  600 // This is the 'maximum' pulse length count (out of 4096)
#define USMIN  600 // This is the rounded 'minimum' microsecond length based on the minimum pulse of 150
#define USMAX  2400 // This is the rounded 'maximum' microsecond length based on the maximum pulse of 600
#define SERVO_FREQ 50 // Analog servos run at ~50 Hz updates






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
      
//      _servo.attach(_pwm_pin);
    }

    float get() {
      float raw_reading = ((float)analogRead(_adc_pin) / 2048.) - 1.;
      raw_reading -= _center_offset;
      raw_reading /= _range_offset;
      return raw_reading;
    }

    void set(float value) {
//      _servo.writeMicroseconds(1500 + 1000 * value);
    }

  private:
    int _pwm_pin;
    int _adc_pin;
    float _center_offset;
    float _range_offset;
//    Servo _servo;
};











uint8_t buffer[128];
float target_angles[] = {0, 0, 0, 0, 0};
float curr_angles[] = {0, 0, 0, 0, 0};

// twelve servo objects can be created on most boards

//BlueArrow_A18 servo_0;
//BlueArrow_A18 servo_1;
//BlueArrow_A7 servo_2;
//BlueArrow_A7 servo_3;
//BlueArrow_A7 servo_4;




int pos = 0;    // variable to store the servo position

void setup() {
  PaleBlueSerial.init(115200);

//  while (!Serial) {}


  Bluefruit.begin();
  Bluefruit.setTxPower(4);    // Check bluefruit.h for supported values

  Bluefruit.setName("A.L.I.C.E."); // useful testing with multiple central connections

  // To be consistent OTA DFU should be added first if it exists
  bledfu.begin();

  // Configure and Start Device Information Service
  bledis.setManufacturer("Adafruit Industries");
  bledis.setModel("Bluefruit Feather52");
  bledis.begin();

  // Configure and Start BLE Uart Service
  bleuart.begin();

  // Start BLE Battery Service
  blebas.begin();
  blebas.write(100);

  // Set up and start advertising
  BLE_startAdvertise();







  

  pwm.begin();
  /*
   * In theory the internal oscillator (clock) is 25MHz but it really isn't
   * that precise. You can 'calibrate' this by tweaking this number until
   * you get the PWM update frequency you're expecting!
   * The int.osc. for the PCA9685 chip is a range between about 23-27MHz and
   * is used for calculating things like writeMicroseconds()
   * Analog servos run at ~50 Hz updates, It is importaint to use an
   * oscilloscope in setting the int.osc frequency for the I2C PCA9685 chip.
   * 1) Attach the oscilloscope to one of the PWM signal pins and ground on
   *    the I2C PCA9685 chip you are setting the value for.
   * 2) Adjust setOscillatorFrequency() until the PWM update frequency is the
   *    expected value (50Hz for most ESCs)
   * Setting the value here is specific to each individual I2C PCA9685 chip and
   * affects the calculations for the PWM update frequency. 
   * Failure to correctly set the int.osc value will cause unexpected PWM results
   */
  pwm.setOscillatorFrequency(27000000);
  pwm.setPWMFreq(SERVO_FREQ);  // Analog servos run at ~50 Hz updates

  
//  servo_0.init(13, A0);
//  servo_1.init(12, A1);
//  servo_2.init(11, A2);
//  servo_3.init(10, A3);
//  servo_4.init(9, A4);
}

void loop() {
//  curr_angles[0] = servo_0.get();
//  curr_angles[1] = servo_1.get();
//  curr_angles[2] = servo_2.get();
//  curr_angles[3] = servo_3.get();
//  curr_angles[4] = servo_4.get();
  
//  PaleBlueSerial.transmit((uint8_t *)curr_angles, 5 * sizeof(float));
  
  uint16_t recv_size = PaleBlueSerial.receive(buffer, 128);
  
  if (recv_size != 5 * sizeof(float)) {
    return;
  }
  target_angles[0] = *((float *)buffer + 0);
  target_angles[1] = *((float *)buffer + 1);
  target_angles[2] = *((float *)buffer + 2);
  target_angles[3] = *((float *)buffer + 3);
  target_angles[4] = *((float *)buffer + 4);
  
//  servo_0.set(target_angles[0]);
//  servo_1.set(target_angles[1]);
//  servo_2.set(target_angles[2]);
//  servo_3.set(target_angles[3]);
//  servo_4.set(target_angles[4]);

  pwm.writeMicroseconds(0, 1500 + 1000 * target_angles[0]);

  delay(10);
}
