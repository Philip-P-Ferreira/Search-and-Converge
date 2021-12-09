import zmq
from typing import Callable
from modules.Common import *
from time import sleep

class Slave:
  def __init__(self, ipAddr: str, searchFunc: SlaveAction, convergeFunc: Callable[[], None]):
    '''
    Create a Slave control object

    searchFunc: ((Event, Event, any) -> None) -> None
      a search function that is performed while the slave is in "search mode". The first event flag must be set when the 
      function succeeds. The second event flag must be able to stop the function in a reasonable amount of time. The any object
      is the data necessary for the slaves to find the objective
    '''
    self.ipAddr = ipAddr
    self.searchFunc = searchFunc
    self.convergeFunc = convergeFunc

    # Create context and sockets. One distributor and one collector
    context = zmq.Context()
    self.distributor = context.socket(zmq.SUB)
    self.distributor.setsockopt(zmq.SUBSCRIBE, b"")
    self.collector = context.socket(zmq.PUSH)

    # connect to master distributor/collector
    self.distributor.connect(ADDR_FORMAT % (self.ipAddr, DISTRIBUTOR_PORT))
    # self.distributor.setsockopt(zmq.SUBSCRIBE, b"")
    self.collector.connect(ADDR_FORMAT % (self.ipAddr, COLLECTOR_PORT))

    #debug message
    debug("Connect to master on ports %d and %d" % (DISTRIBUTOR_PORT, COLLECTOR_PORT))

  def startSearch(self):
    '''
    Send image data to slave cars and start search

    data: Any
      Data to be sent to slave cars to find the objective
    '''

    # receive data
    data = self.distributor.recv_pyobj()
    debug("Received data from master and starting search")

    # we have to know *who* found the item
    masterFinished = Event()
    slaveFinished = Event()
    threads = (
      ActionThread(slaveFinished, self.searchFunc, data),
      NetworkThread(masterFinished, self.distributor) # listen for found message from master
    )

    debug("Starting task threads")
    for t in threads:
      t.start()

    debug("Waiting at least 1 task completion...")
    # block on either task finishing
    while True:
  
      # check if either flag has been set
      if (masterFinished.is_set() or slaveFinished.is_set()):
        if slaveFinished.is_set(): self.collector.send_string(FOUND_MSG) # tell master if we found the objective
        break
      sleep(1)

    debug("Joining task threads")
    # join task threads
    for t in threads:
      t.join()

  def converge(self):
    '''
    converge()
  
    Simply runs the converge function
    '''
    self.convergeFunc()
    