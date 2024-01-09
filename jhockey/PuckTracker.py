import cv2 as cv
import numpy as np
from .utils import PuckState
from typing import Protocol

class FieldHomography(Protocol):
    def convert_px2world(self, x: int, y: int) -> np.ndarray:
        '''
        Convert the coordinates from the camera frame to the field frame.
        @param x: x coordinate in the camera frame
        @param y: y coordinate in the camera frame
        '''
        ...            

    @property
    def H(self) -> np.ndarray:
        '''
        Returns the homography matrix.
        '''
        ...


class PuckTracker:
    '''
    Uses OpenCV's KCF tracker to track the puck
    '''
    def __init__(self, field_homography: FieldHomography):
        self.tracker = cv.TrackerKCF_create()
        self.bbox = None
        self.tracker_initialized = False
        self.field_homography = field_homography
    
    def initialize_tracker(self, frame: np.ndarray):
        '''
        Find the puck in the frame and initialize the tracker.
        @param frame: initial frame to find the puck in
        '''
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
        else:
            print("No contours found")
        
    def update_tracker(self, frame):
        '''
        Update the tracker with the new frame.
        @param frame: new frame to update the tracker with
        '''
        ok, self.bbox = self.tracker.update(frame)
        return ok, self.bbox
    
    def get_puck_state(self) -> PuckState:
        '''
        Get the current state of the puck.
        '''
        if self.field_homography.H is not None:
            center = self.bbox[0] + self.bbox[2] // 2, self.bbox[1] + self.bbox[3] // 2
            coor = self.field_homography.convert_px2world(center[0], center[1])
        if self.tracker_initialized:
            return PuckState(coor[0], coor[1], True)
        else:
            return PuckState(0, 0, False)
    