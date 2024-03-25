# views.py
import cv2
from django.http import StreamingHttpResponse
from django.views.decorators import gzip
import threading
from .import posemodule as pm
import math
from django.shortcuts import render

def findAngle(img, lmList, p1, p2, p3, draw=False):
    x1, y1 = lmList[p1][1:]
    x2, y2 = lmList[p2][1:]
    x3, y3 = lmList[p3][1:]

    angle = math.degrees(math.atan2(y3 - y2, x3 - x2) - math.atan2(y1 - y2, x1 - x2))
    if angle < 0:
        angle = 360 + angle
    if angle > 180:
        angle = 360 - angle

    if draw:
        cv2.circle(img, (x1, y1), 15, (0, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 15, (0, 0, 255), cv2.FILLED)
        cv2.circle(img, (x3, y3), 15, (0, 0, 255), cv2.FILLED)

    return angle

def pose1(img, lmList):
    if findAngle(img, lmList, 11, 13, 15) > 150 and findAngle(img, lmList, 12, 14, 16) > 150:
        if findAngle(img, lmList, 23, 11, 13) > 160 and findAngle(img, lmList, 24, 12, 14) > 160:
            cv2.putText(img, "POSE DETECTED - MOUNTAIN", (50, 50), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)

def pose2(img, lmList):
    if findAngle(img, lmList, 12, 14, 16) > 160 and findAngle(img, lmList, 11, 13, 15) > 160:
        if findAngle(img, lmList, 23, 11, 13) > 70 and findAngle(img, lmList, 24, 12, 14) > 70 and findAngle(
                img, lmList, 23, 11, 13) < 110 and findAngle(img, lmList, 24, 12, 14) < 110:

            if findAngle(img, lmList, 12, 24, 26) > 65 and findAngle(img, lmList, 11, 23, 25) > 100 and findAngle(
                    img, lmList, 12, 24, 26) < 110 and findAngle(img, lmList, 11, 23, 25) < 130:
                cv2.putText(img, "POSE DETECTED - WARRIOR 2", (50, 50), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)

def pose3(img, lmList):
    if findAngle(img, lmList, 12, 14, 16) > 70 and findAngle(img, lmList, 11, 13, 15) > 70 and findAngle(
            img, lmList, 12, 14, 16) < 100 and findAngle(img, lmList, 11, 13, 15) < 100:
        if findAngle(img, lmList, 12, 24, 26) > 65 and findAngle(img, lmList, 11, 23, 25) > 65 and findAngle(
                img, lmList, 12, 24, 26) < 100 and findAngle(img, lmList, 11, 23, 25) < 100:
            cv2.putText(img, "POSE DETECTED - GODDESS", (50, 50), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)

def pose4(img):
   
    cv2.putText(img, "Please Make one of the Pose Shown Above  ", (50, 50), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)


class VideoCamera(object):
    def __init__(self):
        wCam, hCam = 1920, 1080
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, wCam)
        self.cap.set(4, hCam)

        self.detector = pm.poseDetector()

    def __del__(self):
        self.cap.release()

    def get_frame(self):
        success, img = self.cap.read()
        img = cv2.flip(img, 1)
        img = self.detector.findPose(img)
        self.lmList = self.detector.findPosition(img, False)
        if len(self.lmList) != 0:
            pose1(img, self.lmList)
            pose2(img, self.lmList)
            pose3(img, self.lmList)
            # pose4(img)
            _, jpeg = cv2.imencode('.jpg', img)
            return jpeg.tobytes()
        # else:
        #     pose4(img)
        #     _, jpeg = cv2.imencode('.jpg', img)
        #     return jpeg.tobytes()

    def update(self):
        while True:
            (self.grabbed, self.frame) = self.cap.read()


cam = VideoCamera()

@gzip.gzip_page
def livefeed(request):
    def generate():
        while True:
            frame = cam.get_frame()
            if frame is not None:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

    return StreamingHttpResponse(generate(), content_type='multipart/x-mixed-replace; boundary=frame')


def Index(request):
    return render(request, 'index.html')
