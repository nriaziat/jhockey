from .utils import Team, RobotState, AruCoTag
import json
from typing import Any, Protocol
import numpy as np
from threading import Thread, Lock


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


class ArucoDetector(Protocol):
    def get(self) -> dict:
        """
        Returns the detected markers.
        """
        ...


class RobotTracker:
    """
    RobotTracker class to maintain the state of the robots using ArUco markers.
    """
    def __init__(self, field_homography: FieldHomography, aruco_config: str = "aruco_config.json"):
        '''
        Parameters
        ----------
        field_homography : FieldHomography
            The field homography object.
        aruco_config : str, optional
            The path to the ArUco configuration file, by default "aruco_config.json"
        '''
        self.robot_states = {
            Team.BLUE: [RobotState(0, 0, 0, False), RobotState(0, 0, 0, False)],
            Team.RED: [RobotState(0, 0, 0, False), RobotState(0, 0, 0, False)],
        }
        config = json.load(open(aruco_config, "r"))
        self.team_tags = {}
        for id in config["ids"]:
            robot_num = id.split("_")[1]
            team = Team.BLUE if "blue" in id else Team.RED
            self.team_tags[id] = team, robot_num
        self.field_homography = field_homography
        self.stopped = False
        self.robot_lock = Lock()

    def start(self, aruco: ArucoDetector):
        t = Thread(target=self.run, name="Robot Tracker", args=(aruco,))
        t.daemon = True
        t.start()
        return self

    def update(self, aruco_tags: list[AruCoTag]):
        for tag in aruco_tags:
            team = self.team_tags[tag.id][0]
            if self.field_homography.H is None:
                continue
            coor = self.field_homography.convert_px2world(tag.corners[0][0], tag.corners[0][1])
            theta = np.arctan2(coor[1], coor[0])
            robot_num = self.team_tags[id][1]
            with self.robot_lock:
                self.robot_states[team][robot_num].x = coor[0]
                self.robot_states[team][robot_num].y = coor[1]
                self.robot_states[team][robot_num].theta = theta
                self.robot_states[team][robot_num].found = True


    def run(self, aruco: ArucoDetector):
        while True:
            if self.stopped:
                return

            for state in self.robot_states.values():
                for robot in state:
                    robot.x = np.random.randint(0, 1000)
                    robot.y = np.random.randint(0, 1000)
                    robot.theta = np.random.randint(0, 360)

            aruco_tags = aruco.get()
            if len(aruco_tags) > 0:
                self.update(aruco_tags)

    def get(self) -> tuple[list[np.ndarray], list[int], list[np.ndarray]]:
        return self.robot_states

    def stop(self):
        self.stopped = True
