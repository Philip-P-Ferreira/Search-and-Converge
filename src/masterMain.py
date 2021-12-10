from commonMain import baseConvergeFunction, baseSearchFunction
from modules.Master import *
from modules.Ultrasonic import Ultrasonic 

CASCADE_FILE = "assets/stop_data.xml\n"

# idle until hand motion
u = Ultrasonic()
while (u.get_distance() > 5):
  pass

# toggle debug from here
DEBUG_FLAG.set()

def masterSearchFunction(finished: Event, exit: Event):
  baseSearchFunction(finished, exit, CASCADE_FILE)

masterController = Master(1, masterSearchFunction, baseConvergeFunction)

masterController.startSearch(CASCADE_FILE)
masterController.converge()