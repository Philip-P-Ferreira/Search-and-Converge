from modules.Master import * 

# toggle debug from here
DEBUG_FLAG.set()


def searchFunction(finished: Event, exit: Event):
  finished.set()
  return None

def convergeFunction():
  return None

masterController = Master(searchFunction, convergeFunction)

masterController.startSearch("Some data")
masterController.converge()