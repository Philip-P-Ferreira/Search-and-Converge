from modules.Master import * 
import cv2

# toggle debug from here
DEBUG_FLAG.set()


def searchFunction(finished: Event, exit: Event):
  vidCapture = cv2.VideoCapture(0)
  stop_data = cv2.CascadeClassifier('assets/stop_data.xml')
  while (not exit.is_set()):
    suc, img=vidCapture.read()

    img_gray=cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    found = stop_data.detectMultiScale(img_gray, minSize =(100, 100))
    amount_found = len(found)

    if amount_found != 0:
        debug("Objective Found!")
        finished.set()
        vidCapture.release()
        break

def convergeFunction():
  return None

masterController = Master(searchFunction, convergeFunction)

masterController.startSearch("Some data")
masterController.converge()