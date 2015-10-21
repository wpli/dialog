import threading
import time
import gobject
import gtk

import sys
import functools
gobject.threads_init()

sys.path.append( '../../tbh_output_interface/src/' )
sys.path.append( '../../tbh_audio_listener/src/' )
sys.path.append( '../../tbh_speech_recognizer/src/' )
sys.path.append( '../../tbh_dialog_manager/src/' )



# tbh specific stuff
import tbh_speech_recognizer
import tbh_audio_listener
import tbh_output_interface
import tbh_dialog_manager

# Start the dialog manager
dm = tbh_dialog_manager.tbh_dialog_manager_t()

# Start speech recognizer
# It does not need to be on its own thread
sr = tbh_speech_recognizer.tbh_speech_recognizer_t()

# Add handlers to the tbh_audio_listener
al = tbh_audio_listener.tbh_audio_listener_t()

# Add handlers to the speech recognizer

al_thread = threading.Thread( target=al.run )
al_thread.start()


gui_manager = tbh_output_interface.tbh_gui_manager( test_mode=True )

sr.add_processed_audio_event_handler( gui_manager.show_nbest_handler )
sr.add_processed_audio_event_handler( gui_manager.system_message_handler )
sr.add_processed_audio_event_handler( dm.process_nbest_handler )
al.add_audio_listener_handler( sr.process_raw_audio_handler )
al.add_audio_listener_handler( gui_manager.end_of_audio_stream_handler )
al.add_start_of_audio_handler( gui_manager.start_of_audio_handler )
dm.add_processed_nbest_event_handler( gui_manager.execute_action_handler )

#gui_manager_thread = tbh_output_interface.gui_thread( gui_manager )

gui_manager_thread = threading.Thread( target = gui_manager.gui.main )

gui_manager_thread.start()
gtk.main()
gui_manager_thread.quit = True

