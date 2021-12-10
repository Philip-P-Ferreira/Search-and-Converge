from commonMain import baseConvergeFunction, baseSearchFunction
from modules.Slave import *
import sys

DEBUG_FLAG.set()

# Carnumber entered as command line arg
carNum = int(sys.argv[1])

# instantiate controller object
followerController = Slave(carNum, "phil-pi.local", baseSearchFunction, baseConvergeFunction)

# run the program
followerController.startSearch()
followerController.converge()