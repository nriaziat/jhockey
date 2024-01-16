from threading import Thread
from .types import AruCoTag
import serial
import logging

class JeVoisArucoDetector:
    def __init__(self, name="ArUco Detector", port="/dev/ttyACM0", baudrate=115200):
        '''
        Parameters
        ----------
        name : str, optional
            The name of the thread, by default "ArUco Detector"
        port : str, optional
            The serial port to connect to, by default "/dev/ttyACM0".
        baudrate : int, optional
            The baudrate of the serial connection, by default 115200
        '''
        self.port = port
        self.baudrate = baudrate
        self.name = name
        self.corners = [None] * 8
        self.stopped = False
        self.connected = False
        self.try_connect()     

    def start(self):
        '''
        Start the a new thread to read and parse ArUco data from the JeVois camera.
        '''
        t = Thread(target=self.run, name=self.name)
        t.daemon = True
        t.start()
        return self

    def get(self) -> list[AruCoTag]:
        if not self.connected:
            return []
        # with serial.Serial(self.port, self.baudrate, timeout=1) as ser:
        #     self.detect(ser)
        found_corners = [corner for corner in self.corners if corner is not None]
        if len(found_corners) == 0:
            logging.warning("No ArUco tags found")
            return []
        tag_list = []
        for id, corner in enumerate(found_corners):
            tag_list.append(AruCoTag(id=id, corners=corner))
        return tag_list

    def detect(self, ser):
        try:
            line = ser.readline().decode('utf-8').rstrip()
        except serial.SerialException:
            self.connected = False
            logging.error("JeVois disconnected!")
            self.stop()
        logging.info("Line received from Jevois: %s", line)
        tok = line.split()
        if len(tok) < 1:
            logging.warning("Invalid line from JeVois: %s", line)
            return
        if tok[0] != "N2":
            logging.warning("JeVois may be in terse mode!")
            logging.warning("Invalid line from JeVois: %s", line)
            return
        if len(tok) != 6:
            logging.warning("Invalid line from JeVois: %s", line)
            return
        _, id, x, y, w, h = tok
        x = int(x)
        y = int(y)
        w = int(w)
        h = int(h)
        id = int(id[1:])
        # coordinates are returned in "standard" coordinates, where center is at (0, 0), right edge is at 1000 and bottom edge is at 750
        self.corners[id] = [x - w/2, y - h/2, x + w/2, y + h/2]


    def run(self):       
        with serial.Serial(self.port, self.baudrate, timeout=1) as ser:
            while True:
                if self.stopped:
                    return
                self.detect(ser)

    def try_connect(self):
        while self.connected == False:
            try:
                with serial.Serial(self.port, self.baudrate, timeout=1) as ser:
                    self.connected = True
                    logging.info("Connected to JeVois camera")
            except:
                logging.warning("Could not connect to JeVois camera. Retrying...")


    def stop(self):
        self.stopped = True
