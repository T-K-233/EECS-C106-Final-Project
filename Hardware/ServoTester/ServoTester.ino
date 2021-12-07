
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



















uint8_t buffer[128];




void setup() {
  Serial.begin(115200);

  while (!Serial) {}

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

  Serial.println("boot up finished.");
}

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



void loop() {
  uint16_t size = PaleBlueSerial.receive(buffer, 128);
  Serial.print("received ");
  Serial.print(size);
  Serial.println(" pkg");
  if (!size) {
    Serial.println("no packet received");
    return;
  }

  float curr_angles[5];

  curr_angles[0] = 3.14;
  
  PaleBlueSerial.transmit((uint8_t *)curr_angles, 20);
}
