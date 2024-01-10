# adapted from imutils webcamvideostream.py
from threading import Thread, Lock
import cv2 as cv


class ThreadedCamera:
    '''
    Threaded wrapper for OpenCV VideoCapture with built-in camera dewarping.
    '''
    def __init__(self, src: int = -1, name="ThreadedCamera", mtx=None, dist=None):
        """
        Initialize the ThreadedCamera object.

        Args:
            src (int, optional): The index of the camera device to use. Defaults to 0.
            name (str, optional): The name of the thread. Defaults to "ThreadedCamera".
            mtx (numpy.ndarray, optional): The camera matrix. Defaults to None.
            dist (numpy.ndarray, optional): The distortion coefficients. Defaults to None.
        """
        self.stream = cv.VideoCapture(src, cv.CAP_V4L)
        (self.grabbed, self.frame) = self.stream.read()

        self.name = name
        self.lock = Lock()

        self.mtx = mtx
        self.dist = dist

        self.stopped = False

    def start(self):
        """
        Starts the thread that reads frames from the video stream.

        Returns:
            self: the ThreadedCamera instance
        """
        t = Thread(target=self.update, name=self.name, args=())
        t.daemon = True
        t.start()
        return self

    def update(self):
        while True:
            if self.stopped:
                return
            (self.grabbed, frame) = self.stream.read()
            if self.mtx is not None and self.dist is not None:
                self.frame = cv.undistort(
                    frame, self.mtx, self.dist, None, self.mtx
                )

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True
