
#include <Adafruit_GFX.h>    // Core graphics library
#include <Adafruit_ST7735.h> // Hardware-specific library for ST7735
#include <SPI.h>

#define TFT_CS        10
#define TFT_RST        9
#define TFT_DC        7

Adafruit_ST7735 tft = Adafruit_ST7735(TFT_CS, TFT_DC, TFT_RST);

#define WIDTH 128
#define HEIGHT 128

#define SQUARED(val)  ((val) * (val))

#define RGB_TO_565(r, g, b)     ((((uint8_t)r >> 3) << 11) | (((uint8_t)g >> 2) << 5) | (((uint8_t)b >> 3)))


float p = 3.1415926;


uint16_t pcolors[WIDTH * HEIGHT];


void setup(void) {
  Serial.begin(115200);
  Serial.print(F("Hello! ST77xx TFT Test"));

  tft.initR(INITR_144GREENTAB);

  tft.setSPISpeed(40000000);

  Serial.println(F("Initialized"));

  uint16_t time = millis();
  tft.fillScreen(ST77XX_BLACK);
  time = millis() - time;

  Serial.println(time, DEC);
  delay(500);

  pinMode(A0, OUTPUT);
  analogWrite(A0, 64);
}

int lid_position = 110;

int last_t = millis();

void loop() {
  for (int y=0; y<HEIGHT; y+=1) {
    for (int x=0; x<WIDTH; x+=1) {
      pcolors[y * WIDTH + (WIDTH-x-1)] = RGB_TO_565(255, 255, 255);
      
      // pupil
      if (.7 * SQUARED(y - 62) + SQUARED(x - 64) < SQUARED(5)) {
        pcolors[y * WIDTH + (WIDTH-x-1)] = RGB_TO_565(15, 33, 50);
      }
      // base
      else if (.7 * SQUARED(y - 64) + SQUARED(x - 64) < SQUARED(30)) {
        pcolors[y * WIDTH + (WIDTH-x-1)] = RGB_TO_565(26, 77, 147);
      }

      // top blue highlight
      if (SQUARED(y - 85) + SQUARED(x - 66) < 10) {
        pcolors[y * WIDTH + (WIDTH-x-1)] = RGB_TO_565(147, 207, 243);
      }
      // bottom highlight
      if (.6 * SQUARED(y - 38) + SQUARED(x - 64) < SQUARED(10)) {
        pcolors[y * WIDTH + (WIDTH-x-1)] = RGB_TO_565(140, 200, 255);
      }
      
      // moon
      if ((.65 * SQUARED(y - 62) + SQUARED(x - 64) < SQUARED(22)) && (.65 * SQUARED(y - 71) + SQUARED(x - 64) > SQUARED(24))) {
        pcolors[y * WIDTH + (WIDTH-x-1)] = RGB_TO_565(218, 243, 255);
      }
      // moon border
      else if ((.65 * SQUARED(y - 62) + SQUARED(x - 64) < SQUARED(22)) && (.6 * SQUARED(y - 62) + SQUARED(x - 64) > SQUARED(21))) {
        pcolors[y * WIDTH + (WIDTH-x-1)] = RGB_TO_565(15, 40, 60);
      }

      
      // top left white highlight
      if (.8 * SQUARED(y - 80) + SQUARED(x - 48) < 64) {
        pcolors[y * WIDTH + (WIDTH-x-1)] = RGB_TO_565(255, 255, 255);
      }

      // right white highlight
      if (SQUARED(y - 55) + .8 * SQUARED(x - 93) < 10) {
        pcolors[y * WIDTH + (WIDTH-x-1)] = RGB_TO_565(255, 255, 255);
      }
      
      // border
      else if (.7 * SQUARED(y - 64) + SQUARED(x - 64) > SQUARED(30) && .7 * SQUARED(y - 64) + SQUARED(x - 64) < SQUARED(32)) {
        pcolors[y * WIDTH + (WIDTH-x-1)] = RGB_TO_565(15, 40, 60);
      }

      // === eye lids ===
      // skin
      if (y > lid_position) {
        pcolors[y * WIDTH + (WIDTH-x-1)] = RGB_TO_565(223, 154, 156);  //RGB_TO_565(247, 223, 220); // 
      }
      // thick dark line
      if (lid_position-12 < y && y <= lid_position) {
        pcolors[y * WIDTH + (WIDTH-x-1)] = RGB_TO_565(26, 31, 40);
      }
    }
  }

  int16_t x = 0;
  int16_t y = 0;
  int16_t w = WIDTH;
  int16_t h = HEIGHT;
  tft.drawRGBBitmap(x, y, pcolors, w, h);
  
  tft.setCursor(0, 0);
  tft.setTextColor(ST77XX_RED);
  tft.print(millis() - last_t);
  last_t = millis();
}
