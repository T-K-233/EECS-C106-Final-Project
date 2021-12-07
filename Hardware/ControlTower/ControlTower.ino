#include <bluefruit.h>

BLEClientBas  clientBas;
BLEClientDis  clientDis;
BLEClientUart client_uart;

void setup() {
  Serial.begin(115200);

  while (!Serial) {}

  Bluefruit.begin(0, 1);
  
  Bluefruit.setName("ControlTower");

  // Configure Battyer client
  clientBas.begin();  

  // Configure DIS client
  clientDis.begin();

  // Init BLE Central Uart Serivce
  client_uart.begin();
  client_uart.setRxCallback(BLE_RXHandler);

  // Increase Blink rate to different from PrPh advertising mode
  Bluefruit.setConnLedInterval(250);

  // Callbacks for Central
  Bluefruit.Central.setConnectCallback(BLE_ConnectHandler);

  /* Start Central Scanning
   * - Enable auto scan if disconnected
   * - Interval = 100 ms, window = 80 ms
   * - Don't use active scan
   * - Start(timeout) with timeout = 0 will scan forever (until connected)
   */
  Bluefruit.Scanner.setRxCallback(BLE_ScanHandler);
  Bluefruit.Scanner.restartOnDisconnect(true);
  Bluefruit.Scanner.setInterval(160, 80); // in unit of 0.625 ms
  Bluefruit.Scanner.useActiveScan(false);
  Bluefruit.Scanner.start(0);                   // // 0 = Don't stop scanning after n seconds
}

/**
 * Callback invoked when scanner pick up an advertising data
 * @param report Structural advertising data
 */
void BLE_ScanHandler(ble_gap_evt_adv_report_t* report) {
  // Check if advertising contain BleUart service
  if (Bluefruit.Scanner.checkReportForService(report, client_uart)) {
    // Connect to device with bleuart service in advertising
    Bluefruit.Central.connect(report);
  } else {      
    // For Softdevice v6: after received a report, scanner will be paused
    // We need to call Scanner resume() to continue scanning
    Bluefruit.Scanner.resume();
  }
}

/**
 * Callback invoked when an connection is established
 * @param conn_handle
 */
void BLE_ConnectHandler(uint16_t conn_handle) {
  if (client_uart.discover(conn_handle)) {
    client_uart.enableTXD();
  }
  else {
    Bluefruit.disconnect(conn_handle);
  }  
}


/**
 * Callback invoked when uart received data
 * @param uart_svc Reference object to the service where the data 
 * arrived. In this example it is clientUart
 */
void BLE_RXHandler(BLEClientUart& uart_svc) {
  while (uart_svc.available()) {
    char c = uart_svc.read();
    Serial.print(c);
  }
}

void loop() {
  if (Bluefruit.Central.connected() && client_uart.discovered()) {
    while (Serial.available()) {
      char c = Serial.read();
      client_uart.print(c);
    }
  }
}
