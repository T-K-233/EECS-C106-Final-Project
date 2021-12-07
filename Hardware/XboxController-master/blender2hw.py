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
            self._COM = "COM43"
            
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



pose_data = {}


def validateData(bone_name, limit=1):
    global pose_data
    
    if pose_data.get(bone_name):
        pose_data[bone_name] = max(min(pose_data.get(bone_name), 1. * limit), -1. * limit)
    else:
        pose_data[bone_name] = 0


def startSocketComm():
    """
    """
    global pose_data

    # set up Hardware Serial Server
    serial_server = PaleBlueSerial(timeout=0.05)
    print("[HWSS] Hardware Serial Server running...")

    while True:
        # connect to blender server    
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        while True:
            try:
                s.sendall(b"hw")
                buffer = s.recv(1024)
            except OSError:
                # if we lose connection to BSS, reconnect
                s.close()
                time.sleep(1)
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    s.connect(("localhost", 50007))
                except ConnectionRefusedError:
                    time.sleep(2)
                    print("BSS connection failed, retrying...")

                # retry connection
                continue

            except Exception as e:
                print(e)
                raise e
            
            try:
                pose_data = json.loads(buffer.decode())
            except json.decoder.JSONDecodeError:
                print("invalid JSON from BSS, skipping")
                continue

            # angle corrections

            pose_data["shoulder.0.l"] /= .5 * np.pi
            pose_data["shoulder.1.l"] /= .5 * np.pi
            pose_data["elbow.0.l"] /= .5 * np.pi
            pose_data["elbow.1.l"] /= .5 * np.pi
            pose_data["wrist.l"] /= .5 * np.pi
            pose_data["shoulder.0.r"] /= .5 * np.pi
            pose_data["shoulder.1.r"] /= .5 * np.pi
            pose_data["elbow.0.r"] /= .5 * np.pi
            pose_data["elbow.1.r"] /= .5 * np.pi
            pose_data["wrist.r"] /= .5 * np.pi

            pose_data["shoulder.0.l"] *= -1
            pose_data["shoulder.1.l"] *= 1
            pose_data["elbow.0.l"] *= -1
            pose_data["elbow.1.l"] *= -1
            pose_data["wrist.l"] *= -1
            pose_data["shoulder.0.r"] *= -1
            pose_data["shoulder.1.r"] *= 1
            pose_data["elbow.0.r"] *= -1
            pose_data["elbow.1.r"] *= -1
            pose_data["wrist.r"] *= -1

            # offset correction
            pose_data["shoulder.0.l"] += .0
            pose_data["shoulder.1.l"] += -.03
            pose_data["elbow.0.l"] += -.05
            pose_data["elbow.1.l"] += -.08
            pose_data["wrist.l"] += .01
            pose_data["shoulder.0.r"] += .0
            pose_data["shoulder.1.r"] += -.03
            pose_data["elbow.0.r"] += -.05
            pose_data["elbow.1.r"] += -.08
            pose_data["wrist.r"] += .01

            pose_data["shoulder.0.l"] *= .95
            pose_data["shoulder.1.l"] *= .90
            pose_data["elbow.0.l"] *= .77
            pose_data["elbow.1.l"] *= .8
            pose_data["wrist.l"] *= .74
            pose_data["shoulder.0.r"] *= .95
            pose_data["shoulder.1.r"] *= .90
            pose_data["elbow.0.r"] *= .77
            pose_data["elbow.1.r"] *= .8
            pose_data["wrist.r"] *= .74

            
            validateData("shoulder.0.l", 1)
            validateData("shoulder.1.l", 0.5)
            validateData("elbow.0.l", 1)
            validateData("elbow.1.l", 1)
            validateData("wrist.l", 1)
            validateData("shoulder.0.r", 1)
            validateData("shoulder.1.r", 0.5)
            validateData("elbow.0.r", 1)
            validateData("elbow.1.r", 1)
            validateData("wrist.r", 1)
            
            
            buffer = struct.pack("ffffffffff",
                                 pose_data["shoulder.0.l"],
                                 pose_data["shoulder.1.l"],
                                 pose_data["elbow.0.l"],
                                 pose_data["elbow.1.l"],
                                 pose_data["wrist.l"],
                                 pose_data["shoulder.0.r"],
                                 pose_data["shoulder.1.r"],
                                 pose_data["elbow.0.r"],
                                 pose_data["elbow.1.r"],
                                 pose_data["wrist.r"])

            ###### START write to servos ######
            recv_buf = serial_server.receive()

            if recv_buf == -1:
                print("[HWSS] null packet from client")
                serial_server.transmit(b"\xCA")
                continue

            try:
                curr_angles = struct.unpack("fffff", recv_buf)
            except:
                print(recv_buf)

            serial_server.transmit(buffer)

            
            ###### END write to servos ######

            print(pose_data)




if __name__ == "__main__":
    startSocketComm()

