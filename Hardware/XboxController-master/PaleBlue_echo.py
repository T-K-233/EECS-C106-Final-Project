import struct
import logging
import json
import time

import random
import threading

import serial
import serial.tools.list_ports

class EscapeCodes:
    END = b"\x0A"
    ESC = b"\x0B"
    ESC_END = b"\x1A"
    ESC_ESC = b"\x1B"


class PaleBlueSerial:
    def __init__(self, COM=None, baudrate=115200, timeout=0):
        self._COM = COM
        if not self._COM:
            self._COM = "COM31"
            
        self._ser = serial.Serial(port=self._COM, baudrate=baudrate, timeout=timeout)

        
    def transmit(self, buffer):
        index = 0
        while index < len(buffer):
            c = struct.pack("B", buffer[index])
            if c == EscapeCodes.END:
                self._ser.write(EscapeCodes.ESC)
                self._ser.write(EscapeCodes.ESC_END)
            elif c == EscapeCodes.ESC:
                self._ser.write(EscapeCodes.ESC)
                self._ser.write(EscapeCodes.ESC_ESC)
            else:
                self._ser.write(c)
            index += 1
        self._ser.write(EscapeCodes.END)

    def receive(self):
        c = b""
        buffer = b""
        while c != EscapeCodes.END:
            if c == EscapeCodes.ESC:
                c = self._ser.read(1)
                if c == EscapeCodes.ESC_END:
                    buffer += EscapeCodes.END
                elif c == EscapeCodes.ESC_ESC:
                    buffer += EscapeCodes.ESC
                else:
                    buffer += c
            else:
                buffer += c
            c = self._ser.read(1)
            if c == b"":
                return -1
        return buffer

rx_counter = 0
tx_counter = 0
recv_data = b""


def tx_handler():
    global tx_counter
    counter = 0
    while True:
        counter += 1
        
        buffer = b"hello world"+struct.pack("B", counter % 256)
        server.transmit(buffer)
        tx_counter += 1


def rx_handler():
    global rx_counter
    global recv_data
    while True:
        recv = server.receive()
        recv_data = recv
        rx_counter += 1

server = PaleBlueSerial(timeout=0.01)
time.sleep(3)
print("conneced")

tx = threading.Thread(target=tx_handler)
rx = threading.Thread(target=rx_handler)
tx.start()
rx.start()

counter = 0
while True:
    print(tx_counter, rx_counter, recv_data)

    
