import cv2
from threading import Thread, Lock
from typing import Protocol
import numpy as np
from .utils import AruCoTag


class Camera(Protocol):
    def read(self) -> np.ndarray:
        """
        Returns the frame from the camera.
        """
        ...


class ArucoDetector:
    def __init__(self, name="ArUco Detector"):
        self.arucoDict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_100)
        self.arucoParams = cv2.aruco.DetectorParameters()
        self.detector: cv2.aruco.ArucoDetector = cv2.aruco.ArucoDetector(
            self.arucoDict, self.arucoParams
        )
        self.name = name
        self.corners = None
        self.ids = None
        self.rejected = None
        self.stopped = False
        self.aruco_lock = Lock()

    def start(self, cam):
        t = Thread(target=self.run, name=self.name, args=(cam,))
        t.daemon = True
        t.start()
        return self

    def get(self) -> list[AruCoTag]:
        if self.corners is None or self.ids is None:
            return []
        tag_list = []
        for tag in zip(self.corners, self.ids):
            tag_list.append(AruCoTag(id=tag[1], corners=tag[0]))
        return tag_list

    def detect(self, frame):
        (self.corners, self.ids, self.rejected) = self.detector.detectMarkers(frame)

    def run(self, cam: Camera):
        while True:
            if self.stopped:
                return
            frame = cam.read()
            if frame is None:
                continue
            self.detect(frame)

    def stop(self):
        self.stopped = True
