##
# tbh_output_interface contains GUI-related classes and functions

##    * classes
##         o tbh_gui_manager --> sets states and contains a tbh_gui 
##           subclass that contains the GUI
##            + output_as_answer_text( self, text ) --> outputs in answer frame
##    * functions
##         o output_as_speech( text )

import pygtk
pygtk.require('2.0')
import gtk
import pango
import datetime
import time
import gobject
from tbh_speech_interface import *

import threading
import functools



## 
# Description: Thread that "touches" the GUI Otherwise, PyGTK and
# threading supposedly don't play nicely together See
# http://faq.pygtk.org/index.py?req=show&file=faq20.006.htp 
# NOTE:  
# We are not using this class (there do not seem to be issues with our
# current implementation; the motivation for adding this thread was a
# bug that turned out to have a different cause)

class gui_thread( threading.Thread ):
    def __init__( self, gui_manager ):
        super(gui_thread, self).__init__()
        self.gui_manager = gui_manager
        self.quit = False

    def update_label(self, counter):
        self.gui_manager.gui.answer.set_text("Counter: %i" % counter)
        return False

    def run(self):
        counter = 0
        while not self.quit:
            counter += 1
            gobject.idle_add(self.update_label, counter)
            time.sleep(0.1)





class tbh_gui_manager:
    def __init__(self, time_update=20, test_mode=False ):

        # The system may be 'sleeping', 'awake' or 'attentive'
        # Set initial system state to 'sleeping'
        self.system_state = None
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

        # Create the GUI as a subclass
        self.gui = tbh_gui()
        
        # Run unit tests with key presses
        if test_mode:
            self.load_unit_tests()
            self.gui.window.connect( "key_press_event", self.on_key_press )
            

        # self.main_timer = gobject.timeout_add( time_update*1000, self.gui.get_current_time )        
        # self.audio_starter = gobject.timeout_add( time_update*1000, self.start_audio )
        



    def start_audio( self ):
        pass

    # Handler that changes state when the speech recognizer is processing 
    def end_of_audio_stream_handler( self, audio_object ):
        if self.system_state != 'sleeping':
            self.change_system_state( 'processing' )

    def start_of_audio_handler( self ):
        if self.system_state != 'sleeping':
            self.change_system_state( 'listening' )

    def activate_system( self ):
        self.change_system_state( 'awake' )
        print "AWAKE VS STATE", self.awake_voice_synthesizer_state
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
                self.gui.system_state.set_text( \
                   self.gui_system_state_lookup['text'][desired_state] )
                self.gui.system_state_box.modify_bg( \
                    gtk.STATE_NORMAL, gtk.gdk.color_parse( \
                    self.gui_system_state_lookup['colors'][desired_state] ) )   
            else:
                desired_state = None

        return desired_state


    def change_phone_state( self, desired_state ):
        self.phone_state = desired_state
        #print "new system state", self.phone_state
        if desired_state in self.phone_state_lookup['text'].keys():
            self.gui.phone_state.set_text( \
               self.phone_state_lookup['text'][desired_state] )
            self.gui.phone_state_box.modify_bg( \
                gtk.STATE_NORMAL, gtk.gdk.color_parse( \
                self.phone_state_lookup['colors'][desired_state] ) )   
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
                self.gui.voice_synthesizer_state.set_text( \
                   self.voice_synthesizer_state_lookup['text'][desired_state] )
                self.gui.voice_synthesizer_state_box.modify_bg( \
                    gtk.STATE_NORMAL, gtk.gdk.color_parse( \
                    self.voice_synthesizer_state_lookup['colors'][desired_state] ) )   
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
        if line_break_count >= 6:
            self.gui.answer_font = self.answer_font = pango.FontDescription( 'Sans 14' )
            self.gui.answer.modify_font( self.gui.answer_font )
        else:
            self.gui.answer_font = self.answer_font = pango.FontDescription( 'Sans 20' )
            self.gui.answer.modify_font( self.gui.answer_font )

        print text
        self.gui.answer.set_text( text )        
        
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
            'phone_available': 'Phone Available', 
            'phone_unavailable': 'Phone Unavailable',
            'connecting': 'Connecting',
            'in_phone_call': 'In Phone Call',
            'on_hold': 'On Hold',
            'voice_dial': 'Voice Dial'
            }
        self.phone_state_lookup['colors'] = {
            'phone_available': 'yellow', 
            'phone_unavailable': 'gray',
            'connecting': 'orange',
            'in_phone_call': 'green',
            'on_hold': 'pink',
            'voice_dial': 'cyan'
            }

    def load_unit_tests( self ):
        self.unit_tests = []
        """
        method = getattr( self, 'activate_system' )
        self.unit_tests.append( [ method, None ] )

        for item in self.gui_system_state_lookup['text'].keys():
            method = getattr( self, 'activate_system' )
            self.unit_tests.append( [ method, None ] )
            method = getattr( self, 'change_system_state' )        
            self.unit_tests.append( [ method, item ] )

        for item in self.gui_system_state_lookup['text'].keys():
            method = getattr( self, 'sleep_system' )
            self.unit_tests.append( [ method, None ] )
            method = getattr( self, 'change_system_state' )        
            self.unit_tests.append( [ method, item ] )

        method = getattr( self, 'activate_system' )
        self.unit_tests.append( [ method, None ] )
        method = getattr( self, 'change_phone_state' )
        for item in self.phone_state_lookup['text'].keys():
            self.unit_tests.append( [ method, item ] )

        method = getattr( self, 'sleep_system' )
        self.unit_tests.append( [ method, None ] )

        method = getattr( self, 'change_phone_state' )
        for item in self.phone_state_lookup['text'].keys():
            self.unit_tests.append( [ method, item ] )


        """
        method = getattr( self, 'activate_system' )
        self.unit_tests.append( [ method, None ] )
        method = getattr( self, 'change_voice_synthesizer_state' )
        self.unit_tests.append( [ method, self.system_state, 'voice_on' ] )
        method = getattr( self, 'activate_system' )
 
        method = getattr( self, 'sleep_system' )
        self.unit_tests.append( [ method, None ] )

        method = getattr( self, 'activate_system' )
        self.unit_tests.append( [ method, None ] )


        self.unit_tests.append( [ method, 'voice_on' ] )

        method = getattr( self, 'activate_system' )
        self.unit_tests.append( [ method, None ] )






        """
        method = getattr( self, 'activate_system' )
        self.unit_tests.append( [ method, None ] )
        method = getattr( self, 'change_voice_synthesizer_state' )
        for item in self.voice_synthesizer_state_lookup['text'].keys():
            self.unit_tests.append( [ method, item ] )

        method = getattr( self, 'sleep_system' )
        self.unit_tests.append( [ method, None ] )
        method = getattr( self, 'change_voice_synthesizer_state' )
        for item in self.voice_synthesizer_state_lookup['text'].keys():
            self.unit_tests.append( [ method, item ] )

        method = getattr( self, 'activate_system' )
        self.unit_tests.append( [ method, None ] )
        method = getattr( self, 'change_voice_synthesizer_state' )
        for item in self.voice_synthesizer_state_lookup['text'].keys():
            self.unit_tests.append( [ method, item ] )




        self.unit_tests.append( [ method, 'awake' ] )
        method = getattr( self.gui.system_message, 'set_text' )
        self.unit_tests.append( [ method, "Test system message" ] )


        self.unit_tests.append( [ method, 'sleeping' ] )
        method = getattr( self.gui.system_message, 'set_text' )
        self.unit_tests.append( [ method, "Test system message" ] )




        method = getattr( self.gui.answer, 'set_text' )
        self.unit_tests.append( [ method, "Here is a sample answer from the system" ] )
        """
        #method = getattr( self.gui.system_message.set_text ):
        #self.unit_tests.append( [ method, "Test system message" ] )
        




        method = getattr( self, 'activate_system' )
        self.unit_tests.append( [ method, None ] )
        method = getattr( self, 'sleep_system' )
        self.unit_tests.append( [ method, None ] )

        method = getattr( self, 'activate_system' )
        self.unit_tests.append( [ method, None ] )

        method = getattr( self, 'sleep_system' )
        self.unit_tests.append( [ method, None ] )
        
        method = getattr( self.gui, 'get_current_time' )
        self.unit_tests.append( [ method, None ] )


    def on_key_press( self, widget, event ):
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

        self.unit_tests.insert( 0, '' )
        self.unit_tests.insert( 0, '' )
        self.unit_tests.insert( 0, '' )
        self.unit_tests.insert( 0, '' )
        self.unit_tests.insert( 0, '' )
        self.unit_tests.insert( 0, '' )

        if self.placeholder == 0:
            self.activate_system()
        if self.placeholder == 1:
            self.change_voice_synthesizer_state( self.system_state, 'voice_on' )
        if self.placeholder == 2:
            self.change_voice_synthesizer_state( self.system_state, 'voice_off' )
        if self.placeholder == 3:
            self.change_voice_synthesizer_state( self.system_state, 'voice_on' )
        if self.placeholder == 4:
            self.sleep_system()
        if self.placeholder == 5:
            self.activate_system()





        method_to_run = self.unit_tests[index][0]
        arguments = self.unit_tests[index][1]
        print arguments
        if arguments != None:
            self.unit_test_wrapper( method_to_run, self.unit_tests[index][1:] )
        else:
            method_to_run()

        print method_to_run.__name__, arguments



        """
        if event.keyval == gtk.keysyms.space:
            index = self.placeholder
            #print self.placeholder 
            if index == 0:
                print "Change system state"
                self.change_system_state( 'awake' )
            elif index == 1:
                self.change_system_state( 'sleeping' )
            elif index == 2:
                self.change_system_state( 'listening' ) 
            elif index == 3:
                self.change_system_state( 'attentive' ) 
            elif index == 4:
                self.change_system_state( 'processing' )                    
            elif index == 5:
                self.change_system_state( 'awake' )
            elif index == 6:
                pass
            elif index == 7:
                pass
            elif index == 8:
                pass
            elif index == 9:
                pass
            elif index == 9:
                pass
            elif index == 10:
                pass
            elif index == 6:
                pass
            elif index == 6:
                pass
            elif index == 6:
                pass
            elif index == 6:
                pass
            elif index == 6:
                pass
            elif index == 6:
                pass
            elif index == 6:
                pass
            elif index == 6:
                pass
            elif index == 6:
                pass



            else:
                print "No more unit tests"
                    
            """

    ## 
    # Description
    # Shows the nbest list on the gui
    def show_nbest_handler( self , nbest_list ):

        # We don't want to change back to 'awake' until 
        # the information is obtained
        # if self.system_state != 'sleeping':
        #     self.change_system_state( 'awake' )


        nbest_string = ""
        for index, item in enumerate( nbest_list ):
            output_string = \
                "%s, Hypothesis: %s, Score: %.2f" % ( index, item['text'], item['score'] )
            nbest_string = nbest_string + output_string + "\n"
        print nbest_string

        # self.output_answer_as_text( nbest_string )
        

        if 'good_day' in nbest_list[0]['text']:
            self.change_system_state( 'awake' )
        elif 'good_night' in nbest_list[0]['text']:
            self.change_system_state( 'sleeping' )



    ##
    # Description:
    # Shows one-best result for debugging purposes
    def system_message_handler( self, nbest_list ):
        output_string = \
        "%s, Score: %.2f" % ( \
            nbest_list[0]['text'], nbest_list[0]['score'] )
        
        self.gui.system_message.set_text( output_string )


 
    ##
    # Description:
    # Does whatever actions requested by the DM
    def execute_action_handler( self , action_dict ):

        # Handle each of the elements in the action_dict
        if self.system_state != 'sleeping':
            self.change_system_state( 'awake' )
            
        if action_dict['suggestions'] != None:
            # Commands to display suggestion function here
            pass
        else:
            pass
            
        
        if action_dict['change_system_state']:
            if action_dict['desired_system_state'] in ( 'awake', 'sleeping', 'attentive' ):
                self.change_system_state( action_dict['desired_system_state'] )
            else:
                print "ERROR in system state"
                print self.system_state
        else:
            pass


        if action_dict['answer'] != None:
            print "OUTPUT:", action_dict['answer']

            self.output_answer_as_text( action_dict['answer'] )
        else:
            pass

        if action_dict['change_voice_synthesizer_state']:
            if action_dict['desired_voice_synthesizer_state'] in \
                    ( 'voice_on', 'voice_off' ):
                pass
                
            



class tbh_gui:

    
    def __init__(self):
        # pass
        self.create_gui()



    def delete_event(self, widget, event, data=None):
        # If you return FALSE in the "delete_event" signal handler,
        # GTK will emit the "destroy" signal. Returning TRUE means
        # you don't want the window to be destroyed.
        # This is useful for popping up 'are you sure you want to quit?'
        # type dialogs.
        print "delete event occurred"

        # Change FALSE to TRUE and the main window will not be destroyed
        # with a "delete_event".
        return False

    def destroy(self, widget, data=None):
        #print "destroy signal occurred"
        gtk.main_quit()

    

    def create_gui( self ):

        # create a new window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL) 

        # When the window is given the "delete_event" signal (this is given
        # by the window manager, usually by the "close" option, or on the
        # titlebar), we ask it to call the delete_event () function
        # as defined above. The data passed to the callback
        # function is NULL and is ignored in the callback function.
        self.window.connect("delete_event", self.delete_event)
    
        # Here we connect the "destroy" event to a signal handler.  
        # This event occurs when we call gtk_widget_destroy() on the window,
        # or if we return FALSE in the "delete_event" callback.
        self.window.connect("destroy", self.destroy)
    
        # Sets the border width of the window.
        self.window.set_border_width(10)


        # Set the default size of the window
        self.window.set_default_size(800, 480)

        # Set the title of the window
        self.window.set_title("The Boston Home - Resident Voice Interface")

        # Set the background color of the window
        self.window.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("white"))


        ## 
        # 0. TOP-LEVEL ARCHITECTURE
        # gtk.VBox() to hold several "rows" of items
        interface_vbox =  gtk.VBox()
        interface_vbox.set_size_request(800,480)
        self.window.add( interface_vbox )
        interface_vbox.show()

        ##
        # Insert items into the GUI 
        # 1. TOP-LINE BOX
        #Should show the date/time and state (dialog and phone)          
        top_hbox = gtk.HBox()
        top_hbox.set_size_request(800,70)
        interface_vbox.pack_start( top_hbox )
        top_hbox.show()

        #This is the label that shows the current date and time
        self.date_time = gtk.Label()
        self.date_time.show()
        top_hbox.pack_start( self.date_time )       
        top_label_height = 50
        self.date_time.set_size_request(400, top_label_height)
        self.date_time.set_alignment(xalign=0.5, yalign=0.5) 
        self.date_time_size = pango.FontDescription('Sans 18')                  
        date_time_text = self.get_current_time()
        self.date_time.set_text( date_time_text )
        self.date_time.set_alignment( xalign=0.5, yalign=0.5 ) 
        self.date_time.set_size_request( 450,top_label_height )
        self.date_time.modify_font(self.date_time_size)

        # Place a spacer label between the date_time label and the system state label
        spacer_labels = []
        spacer_labels.append( gtk.Label() )
        spacer_labels[0].set_size_request( 1, top_label_height ) 
        spacer_labels[0].show()
        top_hbox.pack_start( spacer_labels[0] )


        # This is the label that shows the current system state (i.e. sleeping, awake, etc.)
        self.system_state = gtk.Label()
        self.system_state.set_text( "Sleeping" )
        self.system_state_font = pango.FontDescription( 'Sans 18' )
        self.system_state.modify_font( self.system_state_font )
        self.system_state_box = gtk.EventBox()
        self.system_state_box.add( self.system_state )
        self.system_state.show()
        self.system_state_box.show()
        self.system_state_box.modify_bg( gtk.STATE_NORMAL, gtk.gdk.color_parse("yellow") )
        top_hbox.pack_start( self.system_state_box ) 
        
        # Place a spacer label between the system_state label and the 
        # voice_synthesizer label
        spacer_labels.append( gtk.Label() )
        spacer_labels[1].set_size_request( 1, top_label_height ) 
        spacer_labels[1].show()
        top_hbox.pack_start( spacer_labels[1] )

       
        # This is the label that shows the current system state (i.e. sleeping, awake, etc.)
        self.voice_synthesizer_state = gtk.Label()
        self.voice_synthesizer_state.set_text( "Voice Off" )
        self.voice_synthesizer_state_font = pango.FontDescription( 'Sans 18' )
        self.voice_synthesizer_state.modify_font( self.voice_synthesizer_state_font )
        self.voice_synthesizer_state_box = gtk.EventBox()
        self.voice_synthesizer_state_box.add( self.voice_synthesizer_state )
        self.voice_synthesizer_state.show()
        self.voice_synthesizer_state_box.show()
        self.voice_synthesizer_state_box.modify_bg( \
            gtk.STATE_NORMAL, gtk.gdk.color_parse("yellow") )
        top_hbox.pack_start( self.voice_synthesizer_state_box ) 
        
        ## 
        # 2. PHONE STATUS LINE
        phone_frame = gtk.Frame(label=None)
        phone_frame.show()
        interface_vbox.pack_start( phone_frame )
        phone_hbox = gtk.HBox()
        phone_hbox.show()
        phone_frame.add( phone_hbox )
        phone_label_height = 50

        self.phone_state = gtk.Label()
        self.phone_state.show()
        self.phone_state_box = gtk.EventBox()
        self.phone_state_box.show()
        self.phone_state_box.add( self.phone_state )
        self.phone_state_box.set_size_request( 200, phone_label_height )
        self.phone_state_box.modify_bg( \
            gtk.STATE_NORMAL, gtk.gdk.color_parse("yellow"))

        self.phone_state.set_text("No Phone Call")
        self.phone_state.modify_font(pango.FontDescription('Sans 18'))

        self.phone_message = gtk.Label()
        self.phone_message.show()
        self.phone_message_font = pango.FontDescription( 'Sans 16' )
        self.phone_message.modify_font( self.phone_message_font )
        self.phone_message.set_size_request( 350, phone_label_height )

        phone_hbox.pack_start( self.phone_state_box )
        phone_hbox.pack_start( self.phone_message )

        ##
        # 3. SYSTEM MESSAGES
        system_message_frame = gtk.Frame(label=None)
        system_message_frame.show()
        interface_vbox.pack_start( system_message_frame )
        self.system_message = gtk.Label()
        self.system_message.show()
        system_message_frame.add( self.system_message )
        self.system_message_font = pango.FontDescription('Sans 16')
        self.system_message.modify_font( self.system_message_font )
        self.system_message.set_size_request(550, 50)

        ##
        # 4. SYSTEM DIALOG AND SUGGESTIONS
        system_response_hbox = gtk.HBox()
        system_response_hbox.show()
        system_response_hbox.set_size_request( 800, 300 )
        interface_vbox.pack_start( system_response_hbox )
        answer_frame = gtk.Frame( label=None )
        answer_frame.set_size_request( 500, 300 )
        answer_frame.show()
        system_response_hbox.pack_start( answer_frame )
        self.answer = gtk.Label()
        self.answer.set_size_request( 500, 300 )
        self.answer.set_line_wrap( True )
        self.answer_font = pango.FontDescription( 'Sans 20' )
        
        self.answer.modify_font( self.answer_font )
        self.answer.show()
        answer_frame.add( self.answer )
        

        self.suggestions_table = gtk.Table( 6, 1, True)
        self.suggestions_table.show()
        self.suggestions_table.set_size_request(250,300)
        suggestions_font = pango.FontDescription('Sans 13')

        self.suggestions_title = gtk.Label('Suggestions:')            
        self.suggestions_title.show()
        self.suggestions_title.set_size_request(250,50)
        suggestions_title_font = pango.FontDescription('Sans 16')
        self.suggestions_title.modify_font(suggestions_title_font)

        suggestions_frame = gtk.Frame(label=None)
        suggestions_frame.show()
        suggestions_frame.add(self.suggestions_table)
        system_response_hbox.pack_start(suggestions_frame)

        self.suggestions_table.attach(self.suggestions_title, 0, 1, 0, 1)

        self.possible_suggestions_list = \
            ['chair, good day', 'chair, wake up', '', '', '', '']

        self.possible_suggestions = []
        for index in range(0,5):
            self.possible_suggestions.append( gtk.Label( \
                    self.possible_suggestions_list[index] ) )
            self.possible_suggestions[index].set_size_request(250,50)
            self.possible_suggestions[index].modify_font(suggestions_font)
            self.possible_suggestions[index].set_line_wrap( True )
            self.possible_suggestions[index].show()

            self.suggestions_table.attach(self.possible_suggestions[index],\
                                              0, 1, index + 1, index + 2)

        ##
        # Display the window    
        #gtk.gdk.threads_enter()


        self.window.show()
        self.window.set_keep_above( True )       

        #gtk.gdk.threads_leave()

    ## 
    # Description
    # Returns the current datetime as a text string as desired by the GUI
    def get_current_time( self ):
        current_datetime = datetime.datetime.now()
        current_datetime_string = current_datetime.strftime( \
            "%a, %b %e, %Y, %I:%M %p " )
        # Set the time on the interface
        self.date_time.set_text( current_datetime_string )
        print current_datetime_string
        return current_datetime_string

    def main( self ):
        # All PyGTK applications must have a gtk.main(). Control ends here
        # and waits for an event to occur (like a key press or mouse event).
        pass
        # gtk.main()







# If the program is run directly or passed as an argument to the python
# interpreter then create an instance of it
if __name__ == "__main__":
    
    #output_as_speech( "Testing one two three" )
    x = speech_synthesizer()

    test_gui_manager = tbh_gui_manager( test_mode=True )
    #Change system state
    test_gui_manager.gui.main()
    gtk.main()


