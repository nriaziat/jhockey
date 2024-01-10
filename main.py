from jhockey.ArucoDetector import ArucoDetector
from jhockey.ThreadedCamera import ThreadedCamera
from jhockey.RobotTracker import RobotTracker
from jhockey.PuckTracker import PuckTracker
from jhockey.FieldHomography import FieldHomography
from jhockey.Broadcaster import Broadcaster
from jhockey.GameGUI import GameGUI
from jhockey.GameManager import GameManager
from jhockey.PausableTimer import PausableTimer
import cv2 as cv
from nicegui import app, run
from fastapi import Response
import base64
import numpy as np
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--camera", type=int, default=0)
args = parser.parse_args()

black_1px = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAA1JREFUGFdjYGBg+A8AAQQBAHAgZQsAAAAASUVORK5CYII="
placeholder = Response(
    content=base64.b64decode(black_1px.encode("ascii")), media_type="image/png"
)

cam = ThreadedCamera(args.camera).start()
aruco = ArucoDetector().start(cam)
field_homography = FieldHomography()
rob_track = RobotTracker(field_homography).start(aruco)
puck_track = PuckTracker(field_homography).start(cam)
broadcaster = Broadcaster(puck_track, rob_track).start()
timer = PausableTimer()
gui = GameGUI(video_feed=False)
gm = GameManager(
    broadcaster=broadcaster,
    puck_tracker=puck_track,
    robot_tracker=rob_track,
    field_homography=field_homography,
    aruco_detector=aruco,
    gui=gui,
    timer=timer,
).start()


@app.get("/video/frame")
async def update_video_feed() -> Response:
    # So we run it in a separate thread (default executor) to avoid blocking the event loop.
    frame = await run.io_bound(cam.read)
    if frame is None:
        return placeholder
    # `convert` is a CPU-intensive function, so we run it in a separate process to avoid blocking the event loop and GIL.
    jpeg = await run.cpu_bound(convert, frame)
    return Response(content=jpeg, media_type="image/jpeg")


def convert(frame: np.ndarray) -> bytes:
    _, imencode_image = cv.imencode(".jpg", frame)
    return imencode_image.tobytes()
