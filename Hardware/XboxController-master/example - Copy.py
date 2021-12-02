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



pose_data = {}


def validateData(bone_name, limit=1):
    global pose_data
    
    if pose_data.get(bone_name):
        pose_data[bone_name] = max(min(pose_data.get(bone_name), 1. * limit), -1. * limit)
    else:
        pose_data[bone_name] = 0


def socketExample():
    """
    """
    global pose_data
    server = PaleBlueSerial(timeout=0.05)
    
    print("conneced")
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(("localhost", 50007))
        
        while True:
            
            recv = server.receive()

            if recv == -1:
                print("packet loss! sending dull packet")
                server.transmit(b"\xCA")    
                continue
            curr_angles = struct.unpack("fffff", recv)



            s.sendall(b"Hello, world")
            buffer = s.recv(1024)
            
            pose_data = json.loads(buffer.decode())


            
            ###### write to servos ######

            pose_data["shoulder.0.l"] /= .5 * np.pi
            pose_data["shoulder.1.l"] /= .5 * np.pi
            pose_data["elbow.0.l"] /= .5 * np.pi
            pose_data["elbow.1.l"] /= .5 * np.pi
            pose_data["wrist.l"] /= .5 * np.pi

            pose_data["shoulder.0.l"] *= -1
            pose_data["shoulder.1.l"] *= 1
            pose_data["elbow.0.l"] *= -1
            pose_data["elbow.1.l"] *= -1
            pose_data["wrist.l"] *= -1

            # offset correction
            pose_data["shoulder.0.l"] += .0
            pose_data["shoulder.1.l"] += -.03
            pose_data["elbow.0.l"] += -.05
            pose_data["elbow.1.l"] += -.08
            pose_data["wrist.l"] += .01

            pose_data["shoulder.0.l"] *= .95
            pose_data["shoulder.1.l"] *= .90
            pose_data["elbow.0.l"] *= .77
            pose_data["elbow.1.l"] *= .8
            pose_data["wrist.l"] *= .74

            
            validateData("shoulder.0.l", 1)
            validateData("shoulder.1.l", 0.5)
            validateData("elbow.0.l", 1)
            validateData("elbow.1.l", 1)
            validateData("wrist.l", 1)
                
            
            buffer = struct.pack("fffff",
                                 pose_data["shoulder.0.l"],
                                 pose_data["shoulder.1.l"],
                                 pose_data["elbow.0.l"],
                                 pose_data["elbow.1.l"],
                                 pose_data["wrist.l"])
            
            server.transmit(buffer)

            ###### write to servos ######

            print(pose_data)

            #time.sleep(0.05)





import time
import sys

import serial

from XboxController import XboxController, Hand

def listDevices():
    numbers, sticks = XboxController.enumerateDevices()
    print("found %d devices: %s" % (len(numbers), numbers))
    
    if not sticks:
        sys.exit(0)

    for stick in sticks:        
        print("stick num" % stick.device_number)
        print(stick.getBatteryInformation())

def loopBasedExample():
    """
    """
    stick = XboxController(0, deadzone=0)
    server = PaleBlueSerial(timeout=0.01)

    time.sleep(2)
    
    print("conneced")

    tar_angles = [0, 0, 0, 0, 0]
    curr_angles = [0, 0, 0, 0, 0]
    
    while True:
        
        recv = server.receive()

        if recv == -1:
            print("packet loss! sending dull packet")
            server.transmit(b"\xCA")    
            continue
        curr_angles = struct.unpack("fffff", recv)
        
        stick.dispatchEvents()
        #stick.setRumble(Hand.k_left, abs(stick.axes["LTrigger"]))
        #stick.setRumble(Hand.k_right, abs(stick.axes["RTrigger"]))
        #print("A Btn:", stick.getAButton(), end="")
        #print("\tPOV:", stick.getPOV(), end="")
        #print("\tX Axis:", stick.getX(Hand.k_left))

        x = stick.getX(Hand.k_left)
        y = stick.getY(Hand.k_left)

        if stick.getYButton():
            tar_angles[0] = y
            
        if stick.getXButton():
            tar_angles[1] = -x
            
        if stick.getBButton():
            tar_angles[2] = x
            
        if stick.getAButton():
            tar_angles[3] = y
            
        if stick.getBumper(Hand.k_right):
            tar_angles[4] = y


        ###### write to servos ######
        tar_angles[0] *= -1
        
        tar_angles[0] = max(min(tar_angles[0], 1.), -1.)
        tar_angles[1] = max(min(tar_angles[1], 1.), -1.)
        tar_angles[2] = max(min(tar_angles[2], 1.), -1.)
        tar_angles[3] = max(min(tar_angles[3], 1.), -1.)
        tar_angles[4] = max(min(tar_angles[4], 1.), -1.)

        buffer = struct.pack("fffff", tar_angles[0], tar_angles[1], tar_angles[2], tar_angles[3], tar_angles[4])
        server.transmit(buffer)

        ###### write to servos ######
        
        print(curr_angles, tar_angles)

        time.sleep(.01)


if __name__ == "__main__":
    socketExample()
    #loopBasedExample()
    # eventBasedExample()

