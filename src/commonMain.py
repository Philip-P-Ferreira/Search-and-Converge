import cv2
from threading import Event
from modules.Common import debug
from modules.Motor import Motor
from modules.Ultrasonic import Ultrasonic

def detectStopSign(vidCapture, stop_data):
  suc, img=vidCapture.read()

  img_gray=cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  found = stop_data.detectMultiScale(img_gray, minSize =(100, 100))
  
  return len(found) != 0

def baseSearchFunction(finished: Event, exit: Event, data):

  # set up video capture and stop sign data
  vidCapture = cv2.VideoCapture(0)
  stop_data = cv2.CascadeClassifier(data)

  ultrasonic = Ultrasonic()
  ultrasonic.run()
  
  # main loop to search, move, and detect
  while (not exit.is_set()):
    if detectStopSign(vidCapture, stop_data):
        debug("Objective Found!")
        finished.set()
        vidCapture.release()

        Motor.PWM.setMotorModel(0,0,0,0)
        ultrasonic.pwm_S.setServoPwm('0',90)
        break

def baseConvergeFunction():
  return None