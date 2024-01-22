from .types import Team, RobotState, AruCoTag
import json
from typing import Any, Protocol
import numpy as np
from threading import Thread, Lock
import logging

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

    def __init__(
        self, field_homography: FieldHomography, aruco_config: str = "config.json"
    ):
        """
        Parameters
        ----------
        field_homography : FieldHomography
            The field homography object.
        aruco_config : str, optional
            The path to the ArUco configuration file, by default "config.json", which contains the Tag IDs for the field.
        """
        # self.robot_states = {
        #     Team.BLUE: [RobotState(0, 0, 0, False), RobotState(0, 0, 0, False)],
        #     Team.RED: [RobotState(0, 0, 0, False), RobotState(0, 0, 0, False)],
        # }
        self.robot_states: dict[int, RobotState] = {}
        config = json.load(open(aruco_config, "r"))
        # self.team_tags = {}
        # for id in config["ids"]:
        #     tag_id = int(config["ids"][id])
        #     robot_num = int(id.split("_")[1])
        #     team = Team.BLUE if "blue" in id else Team.RED
        #     self.team_tags[tag_id] = team, robot_num
        self.field_tags = [tag["id"] for tag in config["field_tags"]]
        self.field_homography = field_homography
        self.stopped = False
        self.robot_lock = Lock()

    def start(self, aruco: ArucoDetector):
        """
        Start the a new thread to track robots using ArUco Detector.
        Parameters
        ----------
        aruco : ArucoDetector
            The ArUco detector object.
        """
        t = Thread(target=self.run, name="Robot Tracker", args=(aruco,))
        t.daemon = True
        t.start()
        return self

    def update(self, aruco_tags: list[AruCoTag]):
        if self.field_homography.H is None:
            # logging.warning("Homography not set")
            return
        # not_found_list = [
        #     tag_id for tag_id in self.tag_tags.keys() if tag not in aruco_tags
        # ]
        # for tag_id in not_found_list:
        #     team, robot_num = self.team_tags[tag_id]
        #     self.robot_states[team][robot_num] = RobotState(found=False)
        for tag in aruco_tags:
            # team, robot_num = self.team_tags[tag.id]
            center_px = np.mean(tag.corners, axis=0)
            center_mm = self.field_homography.convert_px2world(
                center_px[0], center_px[1]
            )
            heading_millirad = 1e3 * np.arctan2(
                tag.corners[1, 1] - tag.corners[0, 1],
                -tag.corners[1, 0] + tag.corners[0, 0],
            )
            # self.robot_states[team][robot_num] = RobotState(
            #     x=center_mm[0], y=center_mm[1], heading=heading_millirad
            # )
            try:
                self.robot_states[tag.id].x = center_mm[0]
                self.robot_states[tag.id].y = center_mm[1]
                self.robot_states[tag.id].heading = heading_millirad
                self.robot_states[tag.id].found = True
            except KeyError:
                self.robot_states[tag.id] = RobotState(
                    x=center_mm[0], y=center_mm[1], heading=heading_millirad
                )

    def run(self, aruco: ArucoDetector):
        while True:
            if self.stopped:
                return
            aruco_tags = aruco.get()
            if len(aruco_tags) == 0:
                continue
            tag_list = [tag for tag in aruco_tags if tag.id not in self.field_tags]
            if len(tag_list) > 0:
                self.update(tag_list)
            else:
                logging.warning("No robot markers found")

    def get(self) -> dict[Team : list[RobotState]] | dict[int:RobotState]:
        return self.robot_states

    def stop(self):
        self.stopped = True
