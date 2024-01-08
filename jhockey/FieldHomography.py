import json
import numpy as np
import cv2 as cv
from .utils import FieldTag

class FieldHomography:
    def __init__(self):
        self.field_params = json.load(open('field_params.json', 'r'))
        self.field_corners = [FieldTag(tag['id'], tag['x'], tag['y']) for tag in self.field_params['field_tags']]
        self.H = None
    def find_homography(self, field_tags: list[FieldTag]) -> np.ndarray:
        self.H = cv.findHomography(np.array([(elem.x, elem.y) for elem in field_tags]), 
                              np.array([self.field_corners[self.field_corners.index(elem)] for elem in field_tags]))[0]
        return self.H
    def convert_coordinates(self, x, y) -> np.ndarray:
        if self.H is None:
            raise Exception("Homography not initialized")
        return np.array([x, y, 1]).dot(self.H)
