import cv2 as cv
import numpy as np
from .types import PuckState
from typing import Protocol
from threading import Thread


class FieldHomography(Protocol):
    def convert_px2world(self, x: int, y: int) -> np.ndarray:
        """
        Convert the coordinates from the camera frame to the field frame.
        @param x: x coordinate in the camera frame
        @param y: y coordinate in the camera frame
        """
        ...

    @property
    def H(self) -> np.ndarray:
        """
        Returns the homography matrix.
        """
        ...


class Camera(Protocol):
    def read(self) -> np.ndarray:
        """
        Returns the frame from the camera.
        """
        ...


class PuckTracker:
    """
    PuckTracker class that uses OpenCV's KCF tracker to track the puck
    """

    def __init__(self, field_homography: FieldHomography):
        """
        Parameters
        ----------
        field_homography : FieldHomography
            The field homography object.
        """
        self.tracker = cv.TrackerKCF_create()
        self.bbox = None
        self.tracker_initialized = False
        self.field_homography = field_homography
        self.stopped = False

    def start(self, cam: Camera):
        t = Thread(target=self.run, name="Puck Tracker", args=(cam,))
        t.daemon = True
        t.start()
        return self

    def run(self, cam: Camera):
        while True:
            if self.stopped:
                return
            frame = cam.read()
            if frame is None:
                continue
            if self.tracker_initialized:
                self.update_tracker(frame)
            else:
                self.initialize_tracker(frame)

    def initialize_tracker(self, frame: np.ndarray):
        """
        Find the puck in the frame and initialize the tracker.
        @param frame: initial frame to find the puck in
        """
        hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
        lower_orange = np.array([0, 100, 100])
        upper_orange = np.array([10, 255, 255])
        mask = cv.inRange(hsv, lower_orange, upper_orange)
        contours, _ = cv.findContours(mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        if len(contours) > 0:
            cnt = contours[0]
            x, y, w, h = cv.boundingRect(cnt)
            self.bbox = (x, y, w, h)
            self.tracker.init(frame, self.bbox)
            self.tracker_initialized = True

    def update_tracker(self, frame):
        """
        Update the tracker with the new frame.
        @param frame: new frame to update the tracker with
        """
        ok, self.bbox = self.tracker.update(frame)
        return ok, self.bbox

    def get(self) -> PuckState:
        """
        Get the current state of the puck.
        """
        if self.field_homography.H is None or not self.tracker_initialized:
            return PuckState(0, 0, False)
        else:
            center = self.bbox[0] + self.bbox[2] // 2, self.bbox[1] + self.bbox[3] // 2
            coor = self.field_homography.convert_px2world(center[0], center[1])
            return PuckState(coor[0], coor[1], True)

    def stop(self):
        self.stopped = True
