import time
import threading
import random
import Queue
import sys
sys.path.append( '../../tbh_output_interface/src/' )

import PyQt4

import tbh_output_interface

class GuiPart:
    def __init__(self, queue, endCommand):
        self.queue = queue

        self.console = tbh_output_interface.tbh_gui_manager()
        self.console.show()
        self.endCommand = endCommand


    def closeEvent(self, ev):
        self.endCommand()

    def processIncoming(self):
        """
        Handle all the messages currently in the queue (if any).
        """
        while self.queue.qsize():
            try:
                msg = self.queue.get(0)
                # Check contents of message and do what it says
                # As a test, we simply print it

                print msg
            except Queue.Empty:
                pass

class ThreadedClient:
    """
    Launch the main part of the GUI and the worker thread. periodicCall and
    endApplication could reside in the GUI part, but putting them here
    means that you have all the thread controls in a single place.
    """
    def __init__(self):
        """
        Start the GUI and the asynchronous threads. We are in the main
        (original) thread of the application, which will later be used by
        the GUI. We spawn a new thread for the worker.
        """
        # Create the queue
        self.queue = Queue.Queue()

        # Set up the GUI part
        self.gui = GuiPart( self.queue, self.endApplication)
        #self.gui.console.show()

        # A timer to periodically call periodicCall :-)
        self.queue_timer = PyQt4.QtCore.QTimer()

        # Start the timer -- this replaces the initial call 
        # to periodicCall
        self.queue_timer.start(100)
        PyQt4.QtCore.QObject.connect(self.queue_timer, PyQt4.QtCore.SIGNAL("timeout()"), \
                                         self.periodicCall)



        # Set up the thread to do asynchronous I/O
        # More can be made if necessary
        self.running = 1
        
    	self.thread = threading.Thread( target=self.worker_thread )
        self.thread.start()

        # Start the periodic call in the GUI to check if the queue contains
        # anything
        self.periodicCall()

    def periodicCall(self):
        """
        Check every 100 ms if there is something new in the queue.
        """       
        self.gui.processIncoming()

        #if not self.running:
        #    root.quit()
      
    def endApplication(self):
        self.running = 0
     


    def worker_thread( self ):

        """
        This is where we handle the asynchronous I/O. For example, it may be
        a 'select()'.
        One important thing to remember is that the thread has to yield
        control.
        """

        rand = random.Random()
        print "in the worker thread"
        while self.running:
            # To simulate asynchronous I/O, we create a random number at
            # random intervals. Replace the following 2 lines with the real
            # thing.
            time.sleep( rand.random() * 1 )
            msg = rand.random()
            self.queue.put(msg)

       
if __name__ == '__main__':
    app = PyQt4.QtGui.QApplication(sys.argv)
    client = ThreadedClient()
    sys.exit(app.exec_())
    

