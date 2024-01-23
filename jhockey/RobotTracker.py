from .types import Team, RobotState, AruCoTag
import json
from typing import Any, Protocol
import numpy as np
from threading import Thread, Lock
import logging
import cv2 as cv


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

    def __init__(self, aruco_config: str = "config.json"):
        """
        Parameters
        ----------
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
        self.stopped = False
        self.aruco_tags = []
        self.robot_lock = Lock()

    def start(self):
        """
        Start the a new thread to track robots using ArUco Detector.
        Parameters
        ----------
        aruco : ArucoDetector
            The ArUco detector object.
        """
        t = Thread(target=self.run, name="Robot Tracker", args=())
        t.daemon = True
        t.start()
        return self

    def convert_cam2world(self, x: int, y: int) -> np.ndarray:
        """
        @param x: x coordinate in pixels
        @param y: y coordinate in pixels
        @return: x, y coordinates in world coordinates
        """
        if self.H is None:
            raise Exception("Homography not initialized")
        return cv.perspectiveTransform(
            np.array([x, y], dtype=np.float32).reshape(-1, 1, 2), self.H
        )

    def update(self, aruco_tags: list[AruCoTag]):
        for robot in self.robot_states.values():
            robot.found = False

        if self.H is None:
            return
        # not_found_list = [
        #     tag_id for tag_id in self.tag_tags.keys() if tag not in aruco_tags
        # ]
        # for tag_id in not_found_list:
        #     team, robot_num = self.team_tags[tag_id]
        #     self.robot_states[team][robot_num] = RobotState(found=False)
        for tag in aruco_tags:
            # team, robot_num = self.team_tags[tag.id]
            center_px = tag.center
            center_mm = self.convert_cam2world(center_px.x, center_px.y).ravel()
            corners = np.array(
                [
                    [tag.center.x - tag.w / 2, tag.center.y - tag.h / 2],
                    [tag.center.x + tag.w / 2, tag.center.y - tag.h / 2],
                    [tag.center.x + tag.w / 2, tag.center.y + tag.h / 2],
                    [tag.center.x - tag.w / 2, tag.center.y + tag.h / 2],
                ]
            )
            heading_millirad = 1e3 * np.arctan2(
                corners[1][1] - corners[0][1], corners[1][0] - corners[0][0]
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

    def run(self):
        while True:
            if self.stopped:
                return
            # aruco_tags = aruco.get()
            if len(self.aruco_tags) == 0:
                continue
            tag_list = [tag for tag in self.aruco_tags if tag.id not in self.field_tags]
            if len(tag_list) > 0:
                self.update(tag_list)
            else:
                logging.warning("No robot markers found")

    def set(self, tags: list[AruCoTag], H):
        self.H = H
        self.aruco_tags = tags
        tag_list = [tag for tag in self.aruco_tags if tag.id not in self.field_tags]
        if len(tag_list) > 0:
            self.update(tag_list)

    def get(self) -> dict[Team : list[RobotState]] | dict[int:RobotState]:
        return self.robot_states

    def stop(self):
        self.stopped = True
