from threading import Thread
from .utils import AruCoTag
import serial
import numpy as np
from serial.serialutil import SerialException

class JeVoisArucoDetector:
    def __init__(self, name="ArUco Detector", port="/dev/ttyACM0", baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.name = name
        self.corners = [None] * 8
        self.stopped = False

    def start(self):
        t = Thread(target=self.run, name=self.name)
        t.daemon = True
        t.start()
        return self

    def get(self) -> list[AruCoTag]:
        if len(self.corners) == 0 or len(self.ids) == 0:
            return []
        tag_list = []
        for id, corner in enumerate(self.corners):
            tag_list.append(AruCoTag(id=id, corners=corner))
        return tag_list

    def detect(self, ser):
        line = ser.readline().rstrip()
        tok = line.split()
        if len(tok) < 1:
            return
        if tok[0] != "N2":
            return
        if len(tok) != 6:
            return
        _, id, x, y, w, h = tok
        self.corners[int(id[1:])] = np.array([int(x), int(y), int(x + w), int(y + h)])


    def run(self):
        with serial.Serial(self.port, self.baudrate, timeout=1) as ser:
            while True:
                if self.stopped:
                    return
                self.detect(ser)

    def stop(self):
        self.stopped = True
