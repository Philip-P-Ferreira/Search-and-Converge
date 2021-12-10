from commonMain import baseConvergeFunction, baseSearchFunction
from modules.Slave import *
import sys

DEBUG_FLAG.set()

carNum = int(sys.argv[1])

followerController = Slave(carNum, "phil-pi.local", baseSearchFunction, baseConvergeFunction)

followerController.startSearch()
followerController.converge()