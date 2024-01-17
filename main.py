from jhockey import GameGUI, FieldHomography, RobotTracker, PausableTimer, Broadcaster, GameManager
from nicegui import ui
import argparse
import logging

parser = argparse.ArgumentParser()
parser.add_argument("--camera", type=int, default=None)
parser.add_argument("--match-length", type=int, default=180)
parser.add_argument("--puck_tracking", action="store_true")
parser.add_argument("--config", type=str, default="config.json")
parser.add_argument("--debug", action="store_true")
parser.add_argument("--debug-info", action="store_true")
args = parser.parse_args()

if args.debug_info:
    logging.basicConfig(level=logging.INFO)
elif args.debug:
    logging.basicConfig(level=logging.WARNING)
else:
    logging.basicConfig(level=logging.ERROR)

gui = GameGUI()
if args.camera is None:
    from jhockey import JeVoisArucoDetector
    aruco = JeVoisArucoDetector().start()
else:
    from jhockey import ThreadedCamera, ArucoDetector
    cam = ThreadedCamera(src=args.camera).start()
    aruco = ArucoDetector().start(cam)
field_homography = FieldHomography()
rob_track = RobotTracker(field_homography, aruco_config=args.config).start(aruco)
if args.puck_tracking:
    from jhockey import PuckTracker
    puck_track = PuckTracker(field_homography).start(aruco)
else:
    puck_track = None
broadcaster = Broadcaster().start()
timer = PausableTimer()
gm = GameManager(
    match_length_sec=args.match_length,
    broadcaster=broadcaster,
    puck_tracker=puck_track,
    robot_tracker=rob_track,
    field_homography=field_homography,
    aruco_detector=aruco,
    gui=gui,
    timer=timer,
).start()
print("Starting UI...")
ui.run(title="JHockey", reload=False, host="0.0.0.0", port=8080, show=False)
