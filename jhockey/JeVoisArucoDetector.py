from threading import Thread, Lock
from .types import AruCoTag, Point
import serial
import logging


class JeVoisArucoDetector:
    def __init__(self, name="JeVois ArUco Detector", port="/dev/ttyACM0", baudrate=115200):
        """
        Parameters
        ----------
        name : str, optional
            The name of the thread, by default "ArUco Detector"
        port : str, optional
            The serial port to connect to, by default "/dev/ttyACM0".
        baudrate : int, optional
            The baudrate of the serial connection, by default 115200
        """
        self.port = port
        self.baudrate = baudrate
        self.name = name
        self.tags: list[AruCoTag] = []
        self.stopped = False
        self.connected = False
        self.ser_port = None
        self.try_connect()
        self.aruco_lock = Lock()
        self.new_data = False
        self.threading = False

    def start(self):
        """
        Start the a new thread to read and parse ArUco data from the JeVois camera.
        """
        t = Thread(target=self.run, name=self.name)
        t.daemon = True
        t.start()
        self.threading = True
        return self

    def get(self) -> list[AruCoTag]:
        if not self.connected:
            return []
        if len(self.tags) == 0:
            logging.warning("No ArUco tags found")
            return []
        return self.tags

    def detect(self, ser=None):
        
        def read_serial(ser):
            try:
                line = ""
                while line != "MARK START":
                    line = ser.readline().decode("utf-8").rstrip()
            except serial.SerialException:
                self.connected = False
                logging.error("JeVois disconnected!")
                self.stop()
                return
            tags = []
            while line != "MARK STOP":
                line = ser.readline().decode("utf-8").rstrip()
                if line == "MARK STOP":
                    with self.aruco_lock:
                        self.tags = tags
                    break
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
                if id in [tag.id for tag in self.tags]:
                    # update existing tag
                    tags = [tag for tag in self.tags if tag.id != id]
                    tags.append(AruCoTag(id, center=Point(x, y), w=w, h=h))
                else:
                    # add new tag
                    tags.append(AruCoTag(id, center=Point(x, y), w=w, h=h))

        if ser is None:
            with self.ser_port as ser:
                read_serial(ser)
        else:
            read_serial(ser)
            
    def run(self):
        while True:
            if self.stopped:
                return
            with self.ser_port as ser:
                self.detect(ser)

    def try_connect(self):
        while self.connected == False:
            try:
                with serial.Serial(self.port, self.baudrate, timeout=1):
                    self.connected = True
                    logging.info("Connected to JeVois camera")
                self.ser_port = serial.Serial(self.port, self.baudrate, timeout=1)
            except:
                logging.warning("Could not connect to JeVois camera. Retrying...")

    def stop(self):
        self.stopped = True
