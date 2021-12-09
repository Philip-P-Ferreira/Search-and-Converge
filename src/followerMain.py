from commonMain import baseConvergeFunction, baseSearchFunction
from modules.Slave import *

DEBUG_FLAG.set()

followerController = Slave("Philips-MacBook-Pro.local", baseSearchFunction, baseConvergeFunction)

followerController.startSearch()
followerController.converge()