from scipy.spatial import distance as dist
from imutils.video import VideoStream
from imutils import face_utils
from pygame import mixer
from threading import Thread
import numpy as np
import argparse
import imutils
import time
import dlib
import cv2


def eye_aspect_ratio(eye):
    
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    ear = (A + B) / (2.0 * C)
    return ear


ap = argparse.ArgumentParser()
ap.add_argument("-a", "--alarm", type=str, default="",help=r'C:\Users\lenovo\Music\Playlists\danger-alarm-23793.mp3')
ap.add_argument("-w", "--webcam", type=int, default=0,help=0)
args = vars(ap.parse_args())
EYE_AR_THRESH = 0.3
EYE_AR_CONSEC_FRAMES = 48
COUNTER = 0
ALARM_ON = False
print("[INFO] loading facial landmark predictor...")
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(r'C:\Users\lenovo\AppData\Local\Programs\Python\Python36\Lib\site-packages\face_recognition_models\models\shape_predictor_68_face_landmarks.dat')

(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]


print("[INFO] starting video stream thread...")
vs = VideoStream(src=args["webcam"]).start()
time.sleep(1.0)
 
while(True):
    frame = vs.read()
    frame = imutils.resize(frame, width=450)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rects = detector(gray, 0)
    for rect in rects:
        shape = predictor(gray, rect)
        shape = face_utils.shape_to_np(shape)
        leftEye = shape[lStart:lEnd]
        rightEye = shape[rStart:rEnd]
        leftEAR = eye_aspect_ratio(leftEye)
        rightEAR = eye_aspect_ratio(rightEye)
        
        ear = (leftEAR + rightEAR) / 2.0
       
        leftEyeHull = cv2.convexHull(leftEye)
        rightEyeHull = cv2.convexHull(rightEye)
        cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
        cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)
        
        if(ear < EYE_AR_THRESH):
            COUNTER += 1
            if(COUNTER >= EYE_AR_CONSEC_FRAMES):
                if not ALARM_ON:
                    ALARM_ON = True
                   
                    mixer.init()
                    mixer.music.load(r'C:\Users\lenovo\Music\Playlists\danger-alarm-23793.mp3')
                    mixer.music.play()
                    cv2.putText(frame, "DROWSINESS ALERT!", (10, 30),cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

       # elif(ear==)
        
        else:
            COUNTER = 0
            ALARM_ON = False    
        cv2.putText(frame, "EyeRatio: {:.2f}".format(ear), (300, 30),cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.imshow("Frame", frame)
    key = cv2.waitKey(5)
    if(key == ord("q")):
        cv2.destroyAllWindows()
        vs.stop()
        break
mixer.music.stop()
       
