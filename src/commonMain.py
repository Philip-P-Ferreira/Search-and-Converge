import time
import cv2
from threading import Event, Thread
from modules.Common import debug
from modules.Motor import Motor
from modules.Ultrasonic import Ultrasonic
from modules.servo import Servo

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

  try:
    collisionThread = CollisionThread(ultrasonic, finished, exit)
    collisionThread.start()
    # main loop to search, move, and detect
    while (not exit.is_set() and not finished.is_set()):
      if detectStopSign(vidCapture, stop_data):
        debug("Objective Found!")
        finished.set()
        collisionThread.join()

  except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
    debug("SIGINT caught!")

  finally: 
    vidCapture.release()
    Motor.PWM.setMotorModel(0,0,0,0)
    ultrasonic.pwm_S.setServoPwm('0',90)
  

def baseConvergeFunction():
  return None

class CollisionThread(Thread):
  def __init__(self, ultrasonic: Ultrasonic, finished: Event, exit: Event):
      super().__init__()
      self.f = finished
      self.e = exit
      self.ultrasonic = ultrasonic

      self.PWM=Motor()
      self.pwm_S=Servo()

  def run(self):

    for i in range(30,151,60):
      self.pwm_S.setServoPwm('0',90)
      time.sleep(0.2)
      if i==30:
        L = self.ultrasonic.get_distance()
      elif i==90:
        M = self.ultrasonic.get_distance()
      else:
        R = self.ultrasonic.get_distance()

    while (not self.f.is_set() and not self.e.is_set()):
      for i in range(90,30,-60):
          # self.pwm_S.setServoPwm('0',i)
          time.sleep(0.2)
          if i==30:
              L = self.ultrasonic.get_distance()
          elif i==90:
              M = self.ultrasonic.get_distance()
          else:
              R = self.ultrasonic.get_distance()
          self.ultrasonic.run_motor(L,M,R)
      for i in range(30,151,60):
          # self.pwm_S.setServoPwm('0',i)
          time.sleep(0.2)
          if i==30:
              L = self.ultrasonic.get_distance()
          elif i==90:
              M = self.ultrasonic.get_distance()
          else:
              R = self.ultrasonic.get_distance()
          self.ultrasonic.run_motor(L,M,R)

