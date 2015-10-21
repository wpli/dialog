import PyQt4
from PyQt4 import QtCore, QtGui
import tbh_pyqt_gui
import sys
import threading
import random
import Queue
import sys
import time

# Get Skype4Py constants
#import Skype4Py 
sys.path.append( '../../tbh_pomdp_util/src/' )
import tbh_pomdp_data_viz


class tbh_gui_thread:
    """
    Launch the main part of the GUI and the worker thread. periodicCall and
    endApplication could reside in the GUI part, but putting them here
    means that you have all the thread controls in a single place.
    """
    def __init__( self ):

        """
        Start the GUI and the asynchronous threads. We are in the main
        (original) thread of the application, which will later be used by
        the GUI. We spawn a new thread for the worker.
        """

        # Create the queue
        self.queue = Queue.Queue()

        # Set up the GUI part
        self.gui_manager = tbh_gui_manager( self.queue, self.endApplication )
        self.gui_manager.show()
        
        self.data_viz_queue = Queue.Queue()
        
        self.pomdp_data_viz = tbh_pomdp_data_viz.tbh_pomdp_data_viz_t( \
            self.queue, self.endApplication )
        self.pomdp_data_viz.show()
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
        self.gui_manager.process_incoming()
        #if not self.running:
        #    root.quit()
      
    def endApplication(self):
        self.running = 0
     


    def worker_thread( self ):

        """
        This is where we handle the asynchronous I/O. 
        """

        # rand = random.Random()
        
        #while self.running:
        #    # To simulate asynchronous I/O, we create a random number at
        #    # random intervals. Replace the following 2 lines with the real
        #    # thing.
        #    time.sleep( rand.random() * 1 )
        #    msg = rand.random()
        #    self.queue.put(msg)
       

class tbh_gui_manager( QtGui.QMainWindow ):
    def __init__(self, queue, end_command, parent=None):

        self.queue = queue
        self.end_command = end_command

        # Initialize system to 'sleeping'
        self.system_state = 'sleeping'
       
        # Attempted workaround for the segmentation fault associated
        # with running the GUI and the audio listener simultaneously
        self.started_audio_listener = False

        # This is what is displayed in the GUI
        self.gui_system_state = None
        self.gui_system_state = 'sleeping'


        self.phone_state = None
        self.voice_synthesizer_state = None
        ##
        # Description:
        # Voice synthesizer's state when the system was awake
        self.awake_voice_synthesizer_state = None

        self.load_gui_specs()


        # Initialize the actual GUI created by Qt Designer
        QtGui.QWidget.__init__(self, parent)
        self.gui = tbh_pyqt_gui.Ui_MainWindow()
        self.gui.setupUi(self)

        self.gui.date_time.setText( '%s, %s %s, %s, %s:%s %s' % (time.strftime("%a"), time.strftime("%b"), time.strftime("%e"), time.strftime("%Y"), time.strftime("%I"), time.strftime("%M"), time.strftime("%p") ))        
    
        # Initialize the POMDP data visualizer






















        QtCore.QObject.connect(self.gui.unit_test_button, QtCore.SIGNAL("clicked()"), self.unit_test )
 
        self.unit_test_counter = 0

    '''
    def unit_test( self ):
        self.unit_test_counter = self.unit_test_counter + 1
        x = self.unit_test_counter 
        if x == 1:
            self.gui.system_state.setText("Awake")
    '''

    def closeEvent( self, ev ):
        self.end_command()


    ## Description:
    # processes incoming messages
    def process_incoming(self):
        """
        Handle all the messages currently in the queue (if any).
        """
        while self.queue.qsize():
            try:
                desired_action = self.queue.get(0)
                # Check contents of message and do what it says
                # As a test, we simply print it

                #print desired_action
                #self.unit_test()

                if desired_action['action'] == "change_gui_system_state":
                    desired_state = desired_action['action_predicate']
                    self.gui.system_state.setText( \
                        self.gui_system_state_lookup['text'][desired_state] )
                    self.gui.system_state.setStyleSheet( \
                        "QWidget { background-color: %s }" % \
                            self.gui_system_state_lookup['colors'][desired_state])  

                elif desired_action['action'] == "show_output_string":
                    output_string = desired_action['action_predicate']
                    self.gui.system_message.setText( output_string )

                elif desired_action['action'] == "change_phone_system_state":
                    desired_state = desired_action['action_predicate']

                    self.gui.phone_state.setText( \
                        self.phone_state_lookup['text'][desired_state] )

                    self.gui.phone_state.setStyleSheet( \
                        "QWidget { background-color: %s }" % \
                            self.phone_state_lookup['colors'][desired_state])  
                    



            except Queue.Empty:
                pass




    ##
    # Description:
    # Function that loads various state lookup dictionaries for the interface
    def load_gui_specs( self ):
        self.gui_system_state_lookup = {}
        self.gui_system_state_lookup['text'] = { 'sleeping': 'Sleeping', 
                                        'awake': 'Awake',
                                        'listening': 'Listening', 
                                        'attentive': 'Attentive',
                                        'processing': 'Thinking'
                                        }

        self.gui_system_state_lookup['colors'] = { 'sleeping': 'yellow', 
                                        'awake': 'green',                                   
                                        'listening': 'orange',
                                        'attentive': 'cyan',
                                        'processing': 'orange'
                                        }
     
        self.voice_synthesizer_state_lookup = {}
        self.voice_synthesizer_state_lookup['text'] = { 
            'voice_off': 'Voice Off', 
            'voice_on': 'Voice On'
            }
        self.voice_synthesizer_state_lookup['colors'] = {
            'voice_off': 'yellow', 
            'voice_on': 'green'
            }

        self.phone_state_lookup = {}
        self.phone_state_lookup['text'] = {
            'dialing': 'Dialing',
            'phone_available': 'Phone Available', 
            'phone_unavailable': 'Phone Unavailable',
            'connecting': 'Connecting',
            'in_phone_call': 'In Phone Call',
            'on_hold': 'On Hold',
            'voice_dial': 'Voice Dial'
            }
        self.phone_state_lookup['colors'] = {
            'dialing': 'orange', 
            'phone_available': 'yellow', 
            'phone_unavailable': 'gray',
            'connecting': 'orange',
            'in_phone_call': 'green',
            'on_hold': 'pink',
            'voice_dial': 'cyan'
            }

    # Handler that changes state when the speech recognizer is processing 
    def end_of_audio_handler( self, param_dict ):
        if self.system_state != 'sleeping':
            self.change_system_state( 'processing' )

    # Handler that changes the GUI system state when the speech
    # recognizer is finished
    # Accepts param dict, even though it is not used
    def end_of_processing_handler( self, param_dict ):
        if self.system_state != 'sleeping':
            self.change_system_state( self.system_state )

    def start_of_audio_handler( self ):
        if self.system_state != 'sleeping':
            self.change_system_state( 'listening' )

    def activate_system( self ):
        self.change_system_state( 'awake' )
        self.change_voice_synthesizer_state( 'awake', self.awake_voice_synthesizer_state )

    def sleep_system( self ):
        self.awake_voice_synthesizer_state = self.voice_synthesizer_state
        self.change_voice_synthesizer_state( 'sleeping', 'voice_off' )
        self.change_system_state( 'sleeping' )

    def change_system_state( self, desired_state ):
        # Change the self.system_state variable based on a simple finite
        # state machine
        final_desired_state = None
        if self.system_state == 'sleeping':
            if desired_state == 'awake':
                self.system_state = 'awake'
                final_desired_state = self.change_gui_system_state( desired_state )         
            else:
                pass
        
        elif self.system_state == 'awake':
            final_desired_state = self.change_gui_system_state( desired_state )      
            if desired_state == 'attentive':
                self.system_state = 'attentive'
            elif desired_state == 'sleeping':
                self.system_state = 'sleeping'
            else:
                pass
        elif self.system_state == 'attentive':
            final_desired_state = self.change_gui_system_state( desired_state )      

            if desired_state == 'awake':
                self.system_state = 'awake'
            elif desired_state == 'sleeping':
                self.system_state = 'sleeping'
            else:
                pass
        else:
            pass

        return final_desired_state

    def change_gui_system_state( self, desired_state ):  
        if self.system_state != 'sleeping':
            self.gui_system_state = desired_state
            #print "new system state", self.gui_system_state

            if desired_state in self.gui_system_state_lookup['text'].keys():
                # Put GUI events in the queue
                # Change the text and change the background color
                self.queue.put( { 'action': 'change_gui_system_state',
                                  'action_predicate': desired_state } )

            else:
                desired_state = None

        return desired_state

    def change_phone_state( self, desired_state ):
        self.phone_state = desired_state
        #print desired_state

        if desired_state in self.phone_state_lookup['text'].keys():
            self.queue.put( { 'action': 'change_phone_system_state',
                              'action_predicate': desired_state } )
        else:
            desired_state = None

        return desired_state

    def change_voice_synthesizer_state( self, current_state, desired_state ):
        # The voice synthesizer state can only be changed while the system 
        # in 'awake' mode
        if self.system_state != 'sleeping':

            #print "new system state", self.voice_synthesizer_state
            if desired_state in self.voice_synthesizer_state_lookup['text'].keys():
                self.voice_synthesizer_state = desired_state
                if current_state != 'sleeping':
                    self.awake_voice_synthesizer_state = desired_state
                self.gui.voice_synthesizer_state.setText( \
                   self.voice_synthesizer_state_lookup['text'][desired_state] )

                self.gui.voice_synthesizer_state.setStyleSheet("QWidget { background-color: %s }" % \
                                                        self.voice_synthesizer_state_lookup['colors'][desired_state])  



                #self.gui.voice_synthesizer_state_box.modify_bg( \
                #    gtk.STATE_NORMAL, gtk.gdk.color_parse( \
                #    self.voice_synthesizer_state_lookup['colors'][desired_state] ) )   
            else:
                desired_state = None

        return desired_state


    def output_answer_as_text( self, text ):     
        # determine number of lines of text
        
        # Count the number of line breaks and shrink the text if 
        # there are more than 6 line breaks
        
        
        line_break_count = text.count( "\n" )
        
        
        
        # If there are more than 6 line breaks,
        # shrink the text
        '''
        if line_break_count >= 6:
            self.gui.answer_font = self.answer_font = pango.FontDescription( 'Sans 14' )
            self.gui.answer.modify_font( self.gui.answer_font )
        else:
            self.gui.answer_font = self.answer_font = pango.FontDescription( 'Sans 20' )
            self.gui.answer.modify_font( self.gui.answer_font )
        '''
        #print text
        self.gui.answer.setText( text )        
        
    def load_gui_specs( self ):


        self.gui_system_state_lookup = {}
        self.gui_system_state_lookup['text'] = { 'sleeping': 'Sleeping', 
                                        'awake': 'Awake',
                                        'listening': 'Listening', 
                                        'attentive': 'Attentive',
                                        'processing': 'Thinking'
                                        }

        self.gui_system_state_lookup['colors'] = { 'sleeping': 'yellow', 
                                        'awake': 'chartreuse',                                   
                                        'listening': 'orange',
                                        'attentive': 'cyan',
                                        'processing': 'orange'
                                        }
        
    
        self.voice_synthesizer_state_lookup = {}
        self.voice_synthesizer_state_lookup['text'] = { 
            'voice_off': 'Voice Off', 
            'voice_on': 'Voice On'
            }
        self.voice_synthesizer_state_lookup['colors'] = {
            'voice_off': 'yellow', 
            'voice_on': 'chartreuse'
            }

        self.phone_state_lookup = {}
        self.phone_state_lookup['text'] = {
            'phone_available': 'Phone Available', 
            'phone_unavailable': 'Phone Unavailable',
            'dialing': "Dialing",
            'ringing': 'Ringing',
            'in_phone_call': 'In Phone Call',
            'on_hold': 'On Hold',
            'voice_dial': 'Voice Dial'
            }
        self.phone_state_lookup['colors'] = {
            'phone_available': 'yellow', 
            'phone_unavailable': 'gray',
            'dialing': 'orange',
            'ringing': 'orange',
            'in_phone_call': 'chartreuse',
            'on_hold': 'pink',
            'voice_dial': 'cyan'
            }

    def update_state( self ):
        pass
        



    def unit_test( self ):
        import time
        #output_as_text( self, "Testing 1 2 3" )
        try:
            self.placeholder = self.placeholder + 1
        except:
            self.placeholder = 0                                           

        # to test speech synthesizer asynchronously
        # our own software's threading might make it possible
        # to interrupt the speech synthesizer
        """
        if self.placeholder == 0:
            x.output_as_speech( "testing one two three" )
        elif self.placeholder == 1:
            x.interrupt_synthesizer()
        """

        index = self.placeholder
        # Run the corresponding unit test

        if index == 0:
            self.activate_system()
        elif index == 1:
            self.change_voice_synthesizer_state( self.system_state, 'voice_on' )
        elif index == 2:
            self.change_voice_synthesizer_state( self.system_state, 'voice_off' )
        elif index == 3:
            self.change_voice_synthesizer_state( self.system_state, 'voice_on' )
        elif index == 4:
            self.sleep_system()
        elif index == 5:
            self.activate_system()
        elif index == 6:
            self.change_phone_state( 'phone_available' )

        elif index == 7:
            self.change_phone_state( 'phone_unavailable' )

        elif index == 8:
            self.change_phone_state( 'connecting' )

        elif index == 9:
            self.change_phone_state( 'in_phone_call' )
        elif index == 10:
            self.change_phone_state( 'on_hold' )

        elif index == 11:
            self.change_phone_state( 'voice_dial' )

        elif index == 12:
            self.change_phone_state( 'phone_available' )
        
        elif index == 13:
            self.change_system_state( 'listening' )
        elif index == 14:
            self.change_system_state( 'processing' )
        elif index == 15:
            self.change_system_state( 'awake' )
        elif index == 16:
            self.change_system_state( 'attentive' )

        elif index == 17:
            self.change_system_state( 'awake' )

        elif index == 18:
            self.output_answer_as_text( "Here is a possible answer." )
        elif index == 19:
            self.output_answer_as_text( \
                "Here is another possible answer.\nCoffee and News.\n2nd Floor Store\nFirst Floor Store.\nMovie.\nCocktails.\nBridge.\nPoker.\nBirthday Celebration." )


        else:
            print "End of unit tests"
            self.placeholder = 0


    ## 
    # Description
    # Shows the nbest list on the gui
    def show_nbest_handler( self , param_dict ):
        nbest_list = param_dict[ 'nbest_list' ]

        # We don't want to change back to 'awake' until 
        # the information is obtained
        # if self.system_state != 'sleeping':
        #     self.change_system_state( 'awake' )


        nbest_string = ""
        for index, item in enumerate( nbest_list ):
            output_string = \
                "%s, Hypothesis: %s, Score: %.2f" % ( index, item['text'], item['score'] )
            nbest_string = nbest_string + output_string + "\n"
        #print nbest_string

        # self.output_answer_as_text( nbest_string )
        

        #if 'good_day' in nbest_list[0]['text']:
        #    self.change_system_state( 'awake' )
        #elif 'good_night' in nbest_list[0]['text']:
        #    self.change_system_state( 'sleeping' )


        self.gui.date_time.setText( '%s, %s %s, %s, %s:%s %s' % (time.strftime("%a"), time.strftime("%b"), time.strftime("%e"), time.strftime("%Y"), time.strftime("%I"), time.strftime("%M"), time.strftime("%p") ))        



    ##
    # Description:
    # Shows one-best result for debugging purposes
    def system_message_handler( self, param_dict ):
        nbest_list = param_dict[ 'nbest_list' ]
        output_string = \
        "%s, Score: %.2f" % ( \
            nbest_list[0]['text'], nbest_list[0]['score'] )
        
        self.queue.put( { 'action': "show_output_string", 
                          'action_predicate': output_string } )

        # This command is done by the queue-polling function
        #self.gui.system_message.setText( output_string )


 
    ##
    # Description:
    # Does whatever actions requested by the DM
    def execute_action_handler( self , param_dict ):

        action_dict = param_dict[ 'action_dict' ]

        # Handle each of the elements in the action_dict
        if self.system_state != 'sleeping':
            self.change_system_state( 'awake' )
            
        if action_dict['gui_suggestions'] != None:
            # Commands to display suggestion function here
            pass
        else:
            pass

        #print action_dict

                    
        if action_dict['gui_state'] is not None:
            if action_dict['gui_state'] in ( 'awake', 'sleeping', 'attentive' ):
                self.change_system_state( action_dict['gui_state'] )


                if action_dict['gui_state'] == 'sleeping':
                    self.sleep_system()
            else:
                print "ERROR in system state"
                print self.system_state
        else:
            pass



        if action_dict['gui_answer_text'] != None:
            # print "OUTPUT:", action_dict['answer']

            self.output_answer_as_text( action_dict['gui_answer_text'] )
        else:
            pass

        if action_dict['gui_voice_synthesizer_on'] is not None:
            pass

    

    ##
    # Description:
    # processes the Skype event
    def show_skype_event_handler( self, skype_event ):
        event_string = str(skype_event)
        print event_string
        if event_string == "ROUTING" \
                or event_string == "EARLYMEDIA":
            self.change_phone_state( 'dialing' )
        elif event_string == "RINGING":
            self.change_phone_state( 'ringing' )
        elif event_string == "INPROGRESS":
            self.change_phone_state( 'in_phone_call' )
        elif event_string == "FINISHED" or event_string == "REFUSED" \
                or event_string == "FAILED" or event_string:
            self.change_phone_state( 'phone_available' )
        elif event_string == "LOCALHOLD" or event_string == "REMOTEHOLD" \
                or event_string == "ONHOLD":
            self.change_phone_state( 'on_hold' )


            
        


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    gui_thread = tbh_gui_thread()

    # my_ui = pyqt_gui.Ui_MainWindow()
    # app.setMainWidget( ui )
    #gui_manager = tbh_gui_manager()


    #gui_manager.show()
    #app.exec_loop()
    sys.exit(app.exec_())
