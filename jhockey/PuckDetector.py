import cv2 as cv

class PuckDetector:
    '''
    PuckDetector class
    Uses OpenCV's KCF tracker to track the puck
    '''
    def __init__(self):
        self.tracker = cv.TrackerKCF_create()
        self.bbox = None
        self.tracker_initialized = False
    
    def initialize_tracker(self, frame):
        # Initialize tracker with first frame and bounding box using color thresholding
        # to look for the orange puck
        hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
        lower_orange = np.array([0, 100, 100])
        upper_orange = np.array([10, 255, 255])
        mask = cv.inRange(hsv, lower_orange, upper_orange)
        contours, _ = cv.findContours(mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        if len(contours) > 0:
            cnt = contours[0]
            x, y, w, h = cv.boundingRect(cnt)
            self.bbox = (x, y, w, h)
            self.tracker.init(frame, self.bbox)
            self.tracker_initialized = True
        else:
            print("No contours found")
        
    def update_tracker(self, frame):
        # Update tracker with new frame
        ok, self.bbox = self.tracker.update(frame)
        return ok, self.bbox
    
    def get_bbox(self):
        return self.bbox
    
