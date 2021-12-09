import zmq
from typing import Callable
from modules.Common import *

class Master:
  def __init__(self, searchFunc: MasterAction, convergeFunc: Callable[[], None]):
    '''
    Create a Master control object

    searchFunc: ((Event, Event) -> None) -> None
      a search function that is performed while the master is in "search mode". The first event flag must be set when
      the function succeeds. The second event flag must be able to stop the function in a reasonable amount of time
    '''
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

  def startSearch(self, data):
    '''
    Send image data to slave cars and start search

    data: Any
      Data to be sent to slave cars to find the objective
    '''

    # send data
    debug("Sending data to slave cars and starting search")
    self.distributor.send_pyobj(data)

    # start search, run search func in another thread
    debug("Data sent, starting search")

    finished = Event()
    threads = (
      ActionThread(finished, self.searchFunc),
      NetworkThread(finished, self.collector)
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

    # redistribute out found message
    self.distributor.send_string(FOUND_MSG)

  def converge(self):
    '''
    converge()
    Simply runs the converge function
    '''
    self.convergeFunc()