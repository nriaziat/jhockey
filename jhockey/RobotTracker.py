from .types import RobotState, AruCoTag
import json
from typing import Protocol
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
        self.threading = False

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
        self.threading = True
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
        def get_pose_from_aruco(tag: AruCoTag):
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
            heading_rad = np.arctan2(
                corners[1][1] - tag.center.y, corners[1][0] - tag.center.x
            )
            if heading_rad < 0:
                heading_rad += 2 * np.pi
            return center_mm, heading_rad

        if self.H is None:
            return

        for robot_id in self.robot_states:
            if robot_id not in [tag.id for tag in aruco_tags]:
                del self.robot_states[robot_id]
            else:
                self.robot_states[robot_id].found = True
                center_mm, heading_rad = get_pose_from_aruco(
                    [tag for tag in aruco_tags if tag.id == robot_id][0]
                )
                self.robot_states[robot_id].x_cm = int(center_mm[0] / 10)
                self.robot_states[robot_id].y_cm = int(center_mm[1] / 10)
                self.robot_states[robot_id].heading_crad = int(heading_rad * 100)
                aruco_tags = [tag for tag in aruco_tags if tag.id != robot_id]

        for new_tag in aruco_tags:
            center_mm, heading_rad = get_pose_from_aruco(new_tag)
            self.robot_states[new_tag.id] = RobotState(
                x_cm=int(center_mm[0] / 10),
                y_cm=int(center_mm[1] / 10),
                heading_crad=int(heading_rad * 100),
                found=True,
            )

    def run(self):
        while True:
            if self.stopped:
                return
            if len(self.aruco_tags) == 0:
                continue
            tag_list = self.filter_tags(self.aruco_tags)
            if len(tag_list) > 0:
                self.update(tag_list)
            else:
                self.robot_states = {}
                logging.warning("No robot markers found")

    def filter_tags(self, tag_list: list[AruCoTag]):
        return [tag for tag in tag_list if tag.id not in self.field_tags]

    def set(self, tags: list[AruCoTag], H):
        self.H = H
        self.aruco_tags = tags

    def get(self) -> dict[int:RobotState]:
        return self.robot_states

    def stop(self):
        self.stopped = True
