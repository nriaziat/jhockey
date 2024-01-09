from .utils import Team, RobotState
import json
from typing import Protocol
import numpy as np

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
        
class RobotTracker:
    def __init__(self):
        self.robot_states = {Team.BLUE: [RobotState(0, 0, 0, False), RobotState(0, 0, 0, False)], 
                             Team.RED: [RobotState(0, 0, 0, False), RobotState(0, 0, 0, False)]}
        config = json.load(open('aruco_config.json', 'r'))
        self.team_tags = {}
        for id in config['ids']:
            robot_num = config['ids'][id].split("_")[1] 
            team = Team.BLUE if "blue" in config['ids'][id] else Team.RED
            self.team_tags[id] = team, robot_num

    def update(self, corners, ids, field_homography: FieldHomography):
        if field_homography.H is None:
            raise Exception("Homography not initialized")
        for corner, id in zip(corners, ids):
            team = self.team_tags[id][0]
            coor = field_homography.convert_px2world(corner[0][0], corner[0][1])
            robot_num = self.team_tags[id][1]
            self.robot_states[team][robot_num].x = coor[0]
            self.robot_states[team][robot_num].y = coor[1]
