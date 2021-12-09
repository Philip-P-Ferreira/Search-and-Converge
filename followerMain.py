from masterMain import convergeFunction
from modules.Slave import *

def searchFunction(finished: Event, exit: Event, data):
  finished.set()
  return None

def converge():
  return None

followerController = Slave("phil-pi.local", searchFunction, convergeFunction)

followerController.startSearch()
followerController.converge()