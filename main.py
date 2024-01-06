from jhockey.ArucoDetector import ArucoDetector
import cv2 as cv

def main():
    arucoDetector = ArucoDetector()
    print("ArucoDetector created")
    cap = cv.VideoCapture(0)
    ret, frame = cap.read()
    while ret:
        corners, ids, rejected = arucoDetector.detect(frame)
        print("ArucoDetector.detect() returned: ", ids)
        # cv.imshow("frame", frame)
        # if cv.waitKey(1) & 0xFF == ord('q'):
        #     break
        ret, frame = cap.read()

if __name__ == "__main__":
    main()