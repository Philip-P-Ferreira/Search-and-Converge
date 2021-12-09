from common import baseConvergeFunction, baseSearchFunction
from modules.Slave import *
import cv2

DEBUG_FLAG.set()

followerController = Slave("Philips-MacBook-Pro.local", baseSearchFunction, baseConvergeFunction)

followerController.startSearch()
followerController.converge()