import struct
import logging
import json
import time
import socket

import random
import threading
import numpy as np

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
            ### CHANG ACCORDINGLY ###
            self._COM = "COM20"
            
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



def startSocketComm():
    serial_server = PaleBlueSerial(timeout=0.05)

    while True:
        buffer = b"test"
        
        serial_server.transmit(buffer)

        time.sleep(0.01)
        
        ###### START write to servos ######
        recv_buf = serial_server.receive()

        if recv_buf == -1:
            print("[HWSS] null packet from client")
            serial_server.transmit(b"\xCA")
            continue

        print(recv_buf)




if __name__ == "__main__":
    startSocketComm()

