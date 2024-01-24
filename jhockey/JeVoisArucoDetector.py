from threading import Thread, Lock
from .types import AruCoTag, Point
import serial
from serial.threaded import ReaderThread, LineReader
import logging
import time


class JeVoisSerialReader(LineReader):
    def __init__(self):
        super(JeVoisSerialReader, self).__init__()
        self._tags = []
        self.tags = []
        self.state = "WAITING"

    def connection_made(self, transport):
        super(JeVoisSerialReader, self).connection_made(transport)

    def handle_line(self, data):
        self.data = data
        if data == "MARK START":
            self.state = "READING"
        elif data == "MARK STOP":
            self.state = "WAITING"
            self.tags = self._tags
            self._tags = []
        if self.state == "READING":
            try:
                id, x, y, w, h = self.process_serial(data)
                self._tags.append(AruCoTag(id, center=Point(x, y), w=w, h=h))
            except TypeError:
                return

    def connection_lost(self, exc):
        logging.error("Connection lost: %s", exc)

    def process_serial(self, line: str):
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
        return id, x, y, w, h


class JeVoisArucoDetector:
    def __init__(
        self, name="JeVois ArUco Detector", port="/dev/ttyACM0", baudrate=115200
    ):
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

    def run(self):
        with ReaderThread(self.ser_port, JeVoisSerialReader) as protocol:
            while True:
                if self.stopped:
                    return
                self.tags = protocol.tags

    def try_connect(self):
        while self.connected == False:
            try:
                with serial.Serial(self.port, self.baudrate, timeout=1):
                    self.connected = True
                    logging.info("Connected to JeVois camera")
                self.ser_port = serial.Serial(self.port, self.baudrate, timeout=1)
            except:
                logging.warning("Could not connect to JeVois camera. Retrying...")
                self.port = "/dev/ttyACM1"
                time.sleep(1)
                self.try_connect()

    def stop(self):
        self.stopped = True
