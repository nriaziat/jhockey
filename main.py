from jhockey import * 
from nicegui import ui
import argparse
import serial

parser = argparse.ArgumentParser()
parser.add_argument("--camera", type=int, default=0)
parser.add_argument("--match-length", type=int, default=10)
parser.add_argument("--video-feed", action="store_true")
parser.add_argument("--jevois", action="store_true")
parser.add_argument("--puck_tracking", action="store_true")
args = parser.parse_args()

gui = GameGUI(video_feed=args.video_feed)
if args.jevois:
    aruco = JeVoisArucoDetector().start()
else:
    cam = ThreadedCamera(src=args.camera).start()
    aruco = ArucoDetector().start(cam)
field_homography = FieldHomography()
rob_track = RobotTracker(field_homography).start(aruco)
if args.puck_tracking:
    puck_track = PuckTracker(field_homography).start(aruco)
else:
    puck_track = None
broadcaster = Broadcaster(robot_tracker=rob_track).start()
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
ui.run(title="JHockey", reload=False, host="0.0.0.0", port=8080, show=False)
