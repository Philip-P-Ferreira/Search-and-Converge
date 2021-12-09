from masterMain import convergeFunction
from modules.Slave import *
import cv2

def searchFunction(finished: Event, exit: Event, data):

  stop_data = cv2.CascadeClassifier('stop_data.xml')
  while (not exit.is_set()):
    suc, img=vidCapture.read()

    img_gray=cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    found = stop_data.detectMultiScale(img_gray, minSize =(100, 100))
    amount_found = len(found)

    if amount_found != 0:
        debug("Objective Found!")
        finished.set()

def converge():
  return None

followerController = Slave("phil-pi.local", searchFunction, convergeFunction)

followerController.startSearch()
followerController.converge()