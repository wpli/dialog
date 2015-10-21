
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
from tbh_output_interface import *



import gobject
import threading
import pygtk, gtk
import pickle

def audio_handler( audio_object ):

    # speech recognizer audio_handler function
    try:
        count_file = open( 'count.pkl', 'r' )
        count = pickle.load( count_file )
        count_file.close()
    except:
        count = 0
        count_file = open( 'count.pkl', 'w' )
        pickle.dump( count, count_file )

    current_file_name = str(count) + '.wav'
              
    f = open( str(count) + '.wav', 'w')
    f.write( audio_object )
    f.close()
    
    #Increment the counter
    count = count + 1
    count_file = open( 'count.pkl', 'w' )
    pickle.dump( count, count_file )
    count_file.close()

    # pass file to the speech recognizer
    nbest_list = sr.recognize_audio_sync( current_file_name, 'full' )
 
    nbest_string = ""
    for index, item in enumerate( nbest_list ):
        output_string = \
            "%s, Hypothesis: %s, Score: %.2f" % ( index, item['text'], item['score'] )
        nbest_string = nbest_string + output_string + "\n"
    
    print nbest_string
        
    # 
    if gui_manager.system_state != 'sleeping':
        gui_manager.change_system_state( 'awake' )
    
    gui_manager.output_answer_as_text( nbest_string )

    if 'good_day' in nbest_list[0]['text']:
        gui_manager.change_system_state( 'awake' )
    elif 'good_night' in nbest_list[0]['text']:
        gui_manager.change_system_state( 'sleeping' )




# Start speech recognizer
# It does not need to be on its own thread
sr = tbh_speech_recognizer_t()

# Start the GUI
# It needs to be on its own thread
gui_manager = tbh_gui_manager()
gui_manager_thread = threading.Thread( target = gui_manager.gui.main )


# Start the tbh_audio_listener
al = tbh_audio_listener_t()
al.add_audio_listener_handler( audio_handler )
al.add_audio_listener_handler( gui_manager.end_of_audio_stream_handler )
al.add_start_of_audio_handler( gui_manager.start_of_audio_handler )

al_thread = threading.Thread( target=al.run )
al_thread.start()



# Add a speech recognizer function to the thread



gtk.gdk.threads_init()
gtk.main()
