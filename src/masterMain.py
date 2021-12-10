from commonMain import baseConvergeFunction, baseSearchFunction
from modules.Master import * 

CASCADE_FILE = "assets/stop_data.xml"

# toggle debug from here
DEBUG_FLAG.set()

def masterSearchFunction(finished: Event, exit: Event):
  baseSearchFunction(finished, exit, CASCADE_FILE)

masterController = Master(1, masterSearchFunction, baseConvergeFunction)

masterController.startSearch(CASCADE_FILE)
masterController.converge()