import cv2

class ArucoDetector:
    def __init__(self, mtx=None, dst=None):
        self.arucoDict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_1000)
        self.arucoParams = cv2.aruco.DetectorParameters()
        self.detector = cv2.aruco.ArucoDetector(self.arucoDict, self.arucoParams)
        self.mtx = mtx
        self.dst = dst

    def detect(self, image):
        if self.mtx is not None and self.dst is not None:
            image = cv2.undistort(image, self.mtx, self.dst)
        (corners, ids, rejected) = self.detector.detectMarkers(image, self.arucoDict, parameters=self.arucoParams)
        return (corners, ids, rejected)
