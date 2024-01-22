from jhockey import GameGUI, FieldHomography, RobotTracker, PausableTimer, XBeeBroadcaster, GameManager
from nicegui import ui
import argparse
import logging

parser = argparse.ArgumentParser()
parser.add_argument("--camera", type=int, default=None, help="Camera port, if not using JeVois.")
parser.add_argument("--match-length", type=int, default=180, help="Match length in seconds. Defaults to 180 seconds.")
parser.add_argument("--puck_tracking", action="store_true", help="Enable puck tracking.")
parser.add_argument("--config", type=str, default="config.json", help="ArUco config .json file. Defaults to config.json.")
parser.add_argument("--debug", action="store_true", help="Enable debug logging.")
parser.add_argument("--debug-info", action="store_true", help="Enable debug logging at info level.")
parser.add_argument("--radio_port", type=str, default="/dev/ttyUSB0",  help="Radio port (i.e., if using Zigbee). Defaults to /dev/ttyUSB0")
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
    from jhockey import ThreadedCamera, CameraArucoDetector
    cam = ThreadedCamera(src=args.camera).start()
    aruco = CameraArucoDetector().start(cam)
field_homography = FieldHomography()
rob_track = RobotTracker(field_homography, aruco_config=args.config).start(aruco)
if args.puck_tracking:
    from jhockey import PuckTracker
    puck_track = PuckTracker(field_homography).start(aruco)
else:
    puck_track = None
broadcaster = XBeeBroadcaster(port=args.radio_port).start()
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
