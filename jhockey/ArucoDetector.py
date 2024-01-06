import cv2

class ArucoDetector:
    def __init__(self):
        self.arucoDict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_100)
        self.arucoParams = cv2.aruco.DetectorParameters_create()

    def detect(self, image):
        (corners, ids, rejected) = cv2.aruco.detectMarkers(image, self.arucoDict, parameters=self.arucoParams)
        return (corners, ids, rejected)

