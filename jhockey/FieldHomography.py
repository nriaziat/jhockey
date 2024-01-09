import json
import numpy as np
import cv2 as cv
from .utils import FieldTag

class FieldHomography:
    def __init__(self):
        self.field_params = json.load(open('field_params.json', 'r'))
        self.field_corners = {tag['id']: (tag['x'], tag['y']) for tag in self.field_params['field_tags']}
        self.H = None
    def find_homography(self, field_tags: list[FieldTag]) -> np.ndarray:
        _, self.H = cv.findHomography(np.array([(elem.x, elem.y) for elem in field_tags]), 
                              np.array([(self.field_corners[elem.id][0], self.field_corners[elem.id][1]) for elem in field_tags]))
        self.H_inv = np.linalg.inv(self.H)
        return self.H
    def convert_px2world(self, x: int, y: int) -> np.ndarray:
        '''
        @param x: x coordinate in pixels
        @param y: y coordinate in pixels
        @return: x, y coordinates in world coordinates
        '''
        if self.H is None:
            raise Exception("Homography not initialized")
        return cv.perspectiveTransform(np.array([x, y]), self.H)
    
    def convert_world2px(self, x: float, y: float) -> np.ndarray:
        '''
        @param x: x coordinate in world coordinates
        @param y: y coordinate in world coordinates
        @return: x, y coordinates in pixels
        '''
        if self.H is None:
            raise Exception("Homography not initialized")
        return cv.perspectiveTransform(np.array([x, y]), self.H_inv).astype(int)
