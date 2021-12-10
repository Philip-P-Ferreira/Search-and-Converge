import time
import cv2
from threading import Event, Thread
from modules.Common import debug
from modules.Motor import Motor
from modules.Ultrasonic import Ultrasonic
from modules.servo import Servo
import RPi.GPIO as GPIO

MOTOR_SPEED = 700
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
  

def baseConvergeFunction(carNum: int):
  GPIO.setwarnings(False)
  GPIO.setmode(GPIO.BCM)
  GPIO.setup(17, GPIO.OUT)

  for i in range(10):
    for i in range(carNum):
      GPIO.output(17, True)
      time.sleep(0.5)
      GPIO.output(17, False)
      time.sleep(0.5)
    time.sleep(1)


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

      self.servo.setServoPwm('0', 30)
      time.sleep(0.4)
      self.avoid(self.ultrasonic.get_distance())

      self.servo.setServoPwm('0', 90)
      time.sleep(0.4)
      self.avoid(self.ultrasonic.get_distance())
      
      self.servo.setServoPwm('0', 150)
      time.sleep(0.4)
      self.avoid(self.ultrasonic.get_distance())

      self.servo.setServoPwm('0', 90)
      time.sleep(0.4)
      self.avoid(self.ultrasonic.get_distance())

    self.motor.setMotorModel(0,0,0,0)
    self.servo.setServoPwm('0', 90)

  def avoid(self, distance: int):
    if (distance < COLLISION_DIST):
        self.motor.setMotorModel(-MOTOR_SPEED, -MOTOR_SPEED, -MOTOR_SPEED, -MOTOR_SPEED)
        time.sleep(0.4)

        self.motor.setMotorModel(MOTOR_SPEED, MOTOR_SPEED, -MOTOR_SPEED, -MOTOR_SPEED)
        time.sleep(0.4)
    
