# general stuff
import gobject
import threading
import pygtk, gtk
import pickle
#import pygst
# pygst.require( '0.10' )
# import gst
#gobject.threads_init()
#gtk.gdk.threads_init()



import sys

## 
# Include the tbh_audio_listener
sys.path.append( '../../tbh_audio_listener/src/' )
from tbh_audio_listener import *

##
# Include the tbh_speech_recognizer
sys.path.append( '../../tbh_speech_recognizer/src/' )
from tbh_speech_recognizer import *

##
# Include the GUI
sys.path.append( '../../tbh_output_interface/src/' )
sys.path.append( '../../tbh_audio_listener/src/' )
sys.path.append( '../../tbh_speech_recognizer/src/' )
sys.path.append( '../../tbh_dialog_manager/src/' )




# tbh specific stuff
import tbh_speech_recognizer
import tbh_audio_listener
import tbh_output_interface

import tbh_dialog_manager




# Start the GUI
# It needs to be on its own thread
gui_manager = tbh_output_interface.tbh_gui_manager()

gui_manager_thread = threading.Thread( target = gui_manager.gui.main )


gui_manager.gui.main()




# Start the dialog manager
dm = tbh_dialog_manager.tbh_dialog_manager_t()
# dm.add_processed_nbest_event_handler( gui_manager.execute_action_handler )

# Start speech recognizer
# It does not need to be on its own thread
sr = tbh_speech_recognizer.tbh_speech_recognizer_t()

# Shows the hypothesized output on the GUI for debugging purposes
# sr.add_processed_audio_event_handler( gui_manager.show_nbest_handler )
# sr.add_processed_audio_event_handler( gui_manager.system_message_handler )
sr.add_processed_audio_event_handler( dm.process_nbest_handler )

# Add handlers to the tbh_audio_listener
al = tbh_audio_listener.tbh_audio_listener_t()
al.add_audio_listener_handler( sr.process_raw_audio_handler )
# al.add_audio_listener_handler( gui_manager.end_of_audio_stream_handler )
# al.add_start_of_audio_handler( gui_manager.start_of_audio_handler )

# Add handlers to the speech recognizer

al_thread = threading.Thread( target=al.run )
al_thread.start()

