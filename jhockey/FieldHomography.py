import json
import numpy as np
import cv2 as cv
from .types import AruCoTag
import logging


class FieldHomography:
    """
    FieldHomography class to convert between the camera frame and the field frame using ArUco markers.
    """

    def __init__(self, param_file: str = "config.json"):
        """
        Parameters
        ----------
        param_file : str, optional
            The path to the field parameters file, by default "config.json"
            The field parameters file should contain the coordinates of the ArUco markers on the field.
            For example:
            {
            "field_markers": [
                {
                    "id": 0,
                    "x": 10,
                    "y": 20
                },
                {
                    "id": 1,
                    "x": 30,
                    "y": 40
                },
                {
                    "id": 2,
                    "x": 50,
                    "y": 60
                },
                {
                    "id": 3,
                    "x": 70,
                    "y": 80
                }
            ],
            } ...
        """
        self.field_params = json.load(open(param_file, "r"))
        self.tag_positions = {
            int(tag["id"]): (float(tag["x"]), float(tag["y"]))
            for tag in self.field_params["field_tags"]
        }
        self.H = None

    def find_homography(self, field_tags: list[AruCoTag]) -> None:
        try:
            detected_tags = [tag for tag in field_tags if tag.id in self.tag_positions]
        except KeyError as e:
            logging.warning("KeyError in find_homography")
            return None
        if len(detected_tags) < 4:
            # logging.warning(f"Not enough tags for homography detected: {len(detected_tags)} tags received, expected 4.")
            return None
        tag_px = np.array(
            [[tag.center.x, tag.center.y] for tag in detected_tags], dtype=np.float32
        ).reshape(-1, 1, 2)
        self.H, _ = cv.findHomography(
            tag_px,
            np.array(
                [
                    (self.tag_positions[tag.id][0], self.tag_positions[tag.id][1])
                    for tag in detected_tags
                ],
                dtype=np.float32,
            ).reshape(-1, 1, 2),
            cv.RANSAC,
            5.0,
        )
        self.H_inv = np.linalg.inv(self.H)

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

    def convert_world2cam(self, x: float, y: float) -> np.ndarray:
        """
        @param x: x coordinate in world coordinates
        @param y: y coordinate in world coordinates
        @return: x, y coordinates in pixels
        """
        if self.H is None:
            raise Exception("Homography not initialized")
        return cv.perspectiveTransform(np.array([x, y]), self.H_inv).astype(int)
