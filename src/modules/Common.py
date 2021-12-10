from threading import Event, Thread
from typing import Callable, Union
import zmq
from queue import Queue

# Constants used across multiple files
DISTRIBUTOR_PORT = 5555
COLLECTOR_PORT = 5556
ADDR_FORMAT = "tcp://%s:%d"
FOUND_MSG = "OBJECTIVE_FOUND"

# custom function types for actions
MasterAction = Callable[[Event, Event], None]
'''
MasterAction: (finished: Event, exit: Event) -> None
Custom function type to represent a local task being run on a master car.

finished: Event
Event flag that MUST be set upon successful completion of the action

exit: Event
The action MUST be stoppable via another thread setting this flag
'''

SlaveAction = Callable[[Event, Event, str], None]
'''
SlaveAction: (finished: Event, exit: Event, data: any) -> None
Custom function type to represent a local task being run on a slave car.

finished: Event
Event flag that MUST be set upon successful completion of the action

exit: Event
The action MUST be stoppable via another thread setting this flag

data: any
data to pass into function
'''

# event flag plus simple function for toggling debug messages
DEBUG_FLAG = Event()
def debug(msg: str):
  if DEBUG_FLAG.is_set(): print(msg)

class ThreadedTask(Thread):
  '''
  Threaded Task
  Base class to define tasks to be run in a separate thread. Tasks must be stoppable via an EXIT flag.
  Tasks must also indicate their completion by setting a "finished" flag
  '''

  def __init__(self, finished: Event):
    '''
    Constructor()

    finished: Event
    Event flag to check if task has finished, readable by an outter scope
    '''
    super().__init__()
    self.finished = finished
    self.EXIT_FLAG = Event()

  def join(self):
    '''
    join()

    Overridden method to also set EXIT_FLAG to signal the task to stop.
    Then joins the thread. Meant to be called by another thread
    '''
    self.EXIT_FLAG.set()
    Thread.join(self)

  def run(self) -> None:
    '''
    run()

    This method is supposed to be overridden. Base functionality does nothing (no-op)
    '''
    return super().run()

class NetworkThread(ThreadedTask):
  '''
  Extended from ThreadedTask to provide a task that reads a message via a (zmq) socket
  '''

  def __init__(self, mailbox: Queue, finished: Event, socket: zmq.Socket):
    '''
    Constructor()

    finished: Event
    Event flag for another thread to know that this task has completed
    
    socket: zmq.Socket()
    Readable Socket to read a string from. recv() must work for given socket type
    '''
    super().__init__(finished)
    self.socket = socket
    self.mailbox = mailbox

  def run(self):
    '''
    run()

    Overridden run function for thread. Polls the socket every 1 second. Allows for termination via
    EXIT_FLAG. Sets the finished flag if a message has been received
    '''

    # poll every second for new message
    while (not self.EXIT_FLAG.is_set() and not self.finished.is_set()):
      if (self.socket.poll(1000) == zmq.POLLIN): # if message to read, then read it
        msg = self.socket.recv_string()
        debug("Message received: %s" % msg)
        self.finished.set()
        self.mailbox.put(msg, True, 5)
      else:
        debug("No message to receive. Trying again...")

class ActionThread(ThreadedTask):
  '''
  ActionThread:
  Extended from ThreadedTask. Accepts a finished event flag, and an action (and optionally some data). Creates an thread object
  that runs the passed action'''

  def __init__(self, finished: Event, action: Union[MasterAction, SlaveAction], data = None):
    '''
    Constructor()
    
    finished: Event
    Event flag for another thread to know that this task has completed
    
    action: Action
    An action to be run in a separate thread. Flags in action must be interacted with'''
    super().__init__(finished)
    self.action = action
    self.data = data

  def run(self):
    '''
    run()
    
    Overridden function that simply runs the action
    '''
    args = [self.finished, self.EXIT_FLAG]
    if (self.data is not None):
      args.append(self.data) # only add data to args if it actually has something
    self.action(*args)
