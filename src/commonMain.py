import time
import cv2
from threading import Event, Thread
from modules.Common import debug
from modules.Motor import Motor
from modules.Ultrasonic import Ultrasonic
from modules.servo import Servo

MOTOR_SPEED = 800
COLLISION_DIST = 15

def detectStopSign(vidCapture, stop_data):
  suc, img=vidCapture.read()

  img_gray=cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  found = stop_data.detectMultiScale(img_gray, minSize =(100, 100))
  
  return len(found) != 0

def baseSearchFunction(finished: Event, exit: Event, data):

  # set up video capture and stop sign data
  vidCapture = cv2.VideoCapture(0)
  stop_data = cv2.CascadeClassifier(data)

  try:
    collisionThread = CollisionThread(finished, exit)
    collisionThread.start()
    # main loop to search, move, and detect
    debug("Looking for object...")
    while (not exit.is_set() and not finished.is_set()):
      if detectStopSign(vidCapture, stop_data):
        debug("Objective Found!")
        finished.set()
        # collisionThread.join()

  except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
    debug("SIGINT caught!")

  finally: 
    vidCapture.release()
  

def baseConvergeFunction():
  return None

class CollisionThread(Thread):
  def __init__(self, finished: Event, exit: Event):
      super().__init__()
      self.f = finished
      self.e = exit

      self.motor=Motor()
      self.servo=Servo()
      self.ultrasonic = Ultrasonic()

  def run(self):
    self.servo.setServoPwm('0', 90)
    self.servo.setServoPwm('1', 90)
    

    while (not self.f.is_set() and not self.e.is_set()):
      self.motor.setMotorModel(MOTOR_SPEED, MOTOR_SPEED, MOTOR_SPEED, MOTOR_SPEED)

      self.servo.setServoPwm('0', 90)
      time.sleep(0.1)
      dist1 = self.ultrasonic.get_distance()

      self.servo.setServoPwm('0', 0)
      time.sleep(0.1)
      dist2 = self.ultrasonic.get_distance()
      
      self.servo.setServoPwm('0', -90)
      time.sleep(0.1)
      dist3 = self.ultrasonic.get_distance()

      if (dist1 < COLLISION_DIST or dist2 < COLLISION_DIST or dist3 < COLLISION_DIST):
        self.motor.setMotorModel(-MOTOR_SPEED, -MOTOR_SPEED, -MOTOR_SPEED, -MOTOR_SPEED)
        time.sleep(0.2)

        self.motor.setMotorModel(MOTOR_SPEED, MOTOR_SPEED, -MOTOR_SPEED, -MOTOR_SPEED)
        time.sleep(0.2)


    self.motor.setMotorModel(0,0,0,0)
    
