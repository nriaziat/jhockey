# adapted from imutils webcamvideostream.py
from threading import Thread, Lock
import cv2 as cv

class ThreadedCamera:
	def __init__(self, src=0, name="ThreadedCamera"):
		# initialize the video camera stream and read the first frame
		# from the stream
		self.stream = cv.VideoCapture(src)
		(self.grabbed, self.frame) = self.stream.read()

		# initialize the thread name
		self.name = name
		self.lock = Lock()

		# initialize the variable used to indicate if the thread should
		# be stopped
		self.stopped = False

	def start(self):
		# start the thread to read frames from the video stream
		t = Thread(target=self.update, name=self.name, args=())
		t.daemon = True
		t.start()
		return self

	def update(self):
		while True:
			if self.stopped:
				return
			with self.lock:
				(self.grabbed, self.frame) = self.stream.read()
		
	def read(self):
		with self.lock:
			return self.frame
		
	def stop(self):
		# indicate that the thread should be stopped
		self.stopped = True