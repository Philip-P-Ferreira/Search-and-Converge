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

  except KeyboardInterrupt:
    debug("SIGINT caught!")

  finally: 
    vidCapture.release()
  

def baseConvergeFunction(carNum: int):
  
  # setup pins for buzzer
  GPIO.setwarnings(False)
  GPIO.setmode(GPIO.BCM)
  GPIO.setup(17, GPIO.OUT)

  # Higher number = faster beeps
  period = (1/2)/carNum

  # repeat beeping some number of times
  for i in range(5):
    # toggle button n times fast, followed by a longer pause
    for i in range(carNum):
      GPIO.output(17, True)
      time.sleep(period)
      GPIO.output(17, False)
      time.sleep(period)
    time.sleep(1)

  # always make sure to stop it
  GPIO.output(17, False)

  print("Converging")
class CollisionThread(Thread):
  '''
  CollisionThread:
  Extended Thread to run collision detection task. Must be stoppable via an exit and finished flag
  '''
  def __init__(self, finished: Event, exit: Event):
    '''
    Constructor()
    
    finished: Event
    Event flag. If set, the task must exit

    exit: Event
    Event flag. If set, the task must exit
    '''
    super().__init__()
    self.f = finished
    self.e = exit

    # define objects to control car hardware
    self.motor=Motor()
    self.servo=Servo()
    self.ultrasonic = Ultrasonic()

  def run(self):
    '''
    run()
    Extended method that runs movement task on thread start
    '''
    # center camera/sensor servos
    self.servo.setServoPwm('0', 90)
    self.servo.setServoPwm('1', 90)
    
    # loop while neither flag has been set
    while (not self.checkEndCondition()):
      self.motor.setMotorModel(MOTOR_SPEED, MOTOR_SPEED, MOTOR_SPEED, MOTOR_SPEED)
      angleList = [30, 90, 150, 90]
      
      # swivel in 3 directions and for each take a reading
      for angle in angleList:
        self.servo.setServoPwm('0', angle)
        time.sleep(0.4)
        self.avoid(self.ultrasonic.get_distance())

        # break out if end condition set, reduces delay in ending
        if (self.checkEndCondition()):
          break

    # turn off the motors and reset servo
    self.motor.setMotorModel(0,0,0,0)
    self.servo.setServoPwm('0', 90)

  def avoid(self, distance: int):
    '''
    avoid()
    Simple function that reverses and turns car when distance is less than a specified amount

    distance: int
    The distance (in cm) from the car to the obstacle
    '''
    if (distance < COLLISION_DIST):
        self.motor.setMotorModel(-MOTOR_SPEED, -MOTOR_SPEED, -MOTOR_SPEED, -MOTOR_SPEED)
        time.sleep(0.4)

        self.motor.setMotorModel(MOTOR_SPEED, MOTOR_SPEED, -MOTOR_SPEED, -MOTOR_SPEED)
        time.sleep(0.4)

  def checkEndCondition(self):
    '''
    checkEndCondition()
    Simple function that checks both of the flags that should stop the thread
    '''
    return self.f.is_set() or self.e.is_set()
    
