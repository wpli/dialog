
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

# general stuff
import gobject
import threading
import pygtk, gtk
import pickle

# tbh specific stuff
import tbh_speech_recognizer
import tbh_audio_listener
import tbh_audio_listener_gui
# import tbh_output_interface

import tbh_dialog_manager


# Start the GUI
# It needs to be on its own thread
gui_manager = tbh_audio_listener_gui.tbh_gui_manager()
gui_manager_thread = threading.Thread( target = gui_manager.gui.main )

# Start the dialog manager
dm = tbh_dialog_manager.tbh_dialog_manager_t()
dm.add_processed_nbest_event_handler( gui_manager.execute_action_handler )

# Start speech recognizer
# It does not need to be on its own thread
sr = tbh_speech_recognizer.tbh_speech_recognizer_t()
sr.add_processed_audio_event_handler( gui_manager.show_nbest_handler )
sr.add_processed_audio_event_handler( dm.process_nbest_handler )

# Add handlers to the tbh_audio_listener
# al = tbh_audio_listener.tbh_audio_listener_t()
gui_manager.audio_listener.add_audio_listener_handler( sr.process_raw_audio_handler )
gui_manager.audio_listener.add_audio_listener_handler( gui_manager.end_of_audio_stream_handler )
gui_manager.audio_listener.add_start_of_audio_handler( gui_manager.start_of_audio_handler )

# Add handlers to the speech recognizer


al_thread = threading.Thread( target=gui_manager.audio_listener.run )
al_thread.start()



# Add a speech recognizer function to the thread



gtk.gdk.threads_init()
gtk.main()
