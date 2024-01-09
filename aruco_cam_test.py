from jhockey.ArucoDetector import ArucoDetector
from jhockey.ThreadedCamera import ThreadedCamera
from jhockey.RobotTracker import RobotTracker
from jhockey.PuckTracker import PuckTracker
from jhockey.FieldHomography import FieldHomography
from jhockey.Broadcaster import Broadcaster
from jhockey.GameGUI import GameGUI, handle_sigint
from jhockey.GameManager import GameManager
from jhockey.PausableTimer import PausableTimer
import cv2 as cv

cam = ThreadedCamera().start()
aruco = ArucoDetector().start(cam)
field_homography = FieldHomography()
rob_track = RobotTracker(field_homography).start(aruco)
puck_track = PuckTracker(field_homography).start(cam)
broadcaster = Broadcaster(puck_track, rob_track).start()
gui = GameGUI()
timer = PausableTimer()
gm = GameManager(broadcaster=broadcaster, 
                 puck_tracker=puck_track, 
                 robot_tracker=rob_track, 
                 field_homography=field_homography, 
                 aruco_detector=aruco, 
                 gui=gui,
                 timer=timer).start()