import zmq
from typing import Callable
from modules.Common import *

class Master:
  def __init__(self, carNumber: int, searchFunc: MasterAction, convergeFunc: Callable[[int], None]):
    '''
    Create a Master control object

    searchFunc: ((Event, Event) -> None) -> None
      a search function that is performed while the master is in "search mode". The first event flag must be set when
      the function succeeds. The second event flag must be able to stop the function in a reasonable amount of time
    '''
    self.carNumber = carNumber
    self.searchFunc = searchFunc
    self.convergeFunc = convergeFunc

    # Create context and sockets. One distributor and one collector
    context = zmq.Context()
    self.distributor = context.socket(zmq.PUB)
    self.collector = context.socket(zmq.PULL)

    self.distributor.bind(ADDR_FORMAT % ("*", DISTRIBUTOR_PORT))
    self.collector.bind(ADDR_FORMAT % ("*", COLLECTOR_PORT))

    #debug message
    debug("Bound to ports %d and %d" % (DISTRIBUTOR_PORT, COLLECTOR_PORT))

  def startSearch(self, data: str):
    '''
    Send image data to slave cars and start search

    data: Any
      Data to be sent to slave cars to find the objective
    '''

    # send data
    debug("Sending data to slave cars and starting search")
    self.distributor.send_string(data)

    # start search, run search func in another thread
    debug("Data sent, starting search")

    mailbox = Queue(1)
    finished = Event()
    threads = (
      ActionThread(finished, self.searchFunc),
      NetworkThread(mailbox, finished, self.collector)
    )

    debug("Starting task threads")
    for t in threads:
      t.start()

    debug("Waiting at least 1 task completion...")
    # block on either task finishing
    finished.wait()

    debug("Joining task threads")
    # join task threads
    for t in threads:
      t.join()

    # no message means we found the objective
    if (mailbox.empty):
      self.foundCarNum = self.carNumber
    else:
      msg: str = mailbox.get()
      arr = msg.split(":")
      self.foundCarNum = int(arr[1])

    # redistribute out found message
    self.distributor.send_string(FOUND_MSG + ":" + str(self.foundCarNum))

  def converge(self):
    '''
    converge()
    Simply runs the converge function
    '''
    self.convergeFunc(self.foundCarNum)