
# -------------------------- #
#    IMPORTS AND SETTINGS    #
# -------------------------- #
# ---- IMPORTS ---- #
# general adds
import threading
import time
import gobject
import gtk

import sys
import functools
gobject.threads_init()

import PyQt4

# tbh specific stuff
sys.path.append( '../../tbh_data_storage/src/' )
sys.path.append( '../../tbh_output_interface/src/' )
sys.path.append( '../../tbh_audio_listener/src/' )
sys.path.append( '../../tbh_speech_recognizer/src/' )
sys.path.append( '../../tbh_dialog_manager/src/' )
sys.path.append( '../../tbh_skype_interface/src/' )
sys.path.append( '../../tbh_pomdp_util/src/' )
sys.path.append( '../../dialog_system_tools/src/' )
import tbh_speech_recognizer
import tbh_audio_listener
import tbh_output_interface_experiments as tbh_output_interface
import tbh_dialog_manager_experiments as tbh_dialog_manager
import tbh_skype_interface
import tbh_data_storage_experiments as tbh_data_storage
import tbh_pomdp_data_viz
import analysis_tools

## Load Skype contacts
skype_contacts_dict = tbh_skype_interface.load_skype_contacts( \
    'skype_contact_names_00.txt' )

# -------------------- #
#    INITIALIZATION    #
# -------------------- #
# ---- INITIALIZE THINGS ---- #
# Initialize the dialog manager
feature_type_list = [ 'tbh_keyword' , 'tbh_first_word' , 'tbh_keyword_sequence', 'score_statistic', 'tbh_digits', 'tbh_skype_contact' ]

data_path = '../../dialog_system_tools/bin/20120118/'

tag_dict_pickle = data_path + 'round1and2.pkl'
confidence_dict_pickle = data_path + 'round1and2.073.confidence_scores_for_dialog.pkl'
states_text_file = data_path + 'decision_process_files/states.txt'
actions_text_file = data_path + 'decision_process_files/actions.txt'
observations_text_file = data_path + 'decision_process_files/observations.txt'
partition_dict_pickle = data_path + 'partition_dict.pkl'
test_set = 2

use_all_hypotheses = True
use_two_confidence_model = True
use_confidence_scores_in_pomdp = True
sample_from_confidence_model = True
terminate_upon_fulfilling_user_goal = True
use_test_set_only = False

( state_list, action_list, observation_list ) = \
    analysis_tools.build_states_actions_observations_lists( \
    states_text_file, actions_text_file, observations_text_file )

( high_confidence_histogram, low_confidence_histogram ) = analysis_tools.get_histograms( \
        tag_dict_pickle, confidence_dict_pickle, observation_list, \
            partition_dict_pickle, use_all_hypotheses, use_test_set_only, test_set )

dm = tbh_dialog_manager.tbh_dialog_manager_t( \
    feature_type_list = feature_type_list, \
        skype_contacts_dict = skype_contacts_dict, \
        high_confidence_histogram = high_confidence_histogram, \
        low_confidence_histogram = low_confidence_histogram )

# Initialize speech recognizer
sr = tbh_speech_recognizer.tbh_speech_recognizer_t( \
    starting_grammar = 'full', default_grammar = 'full' )

# Initialize Skype manager
# Pass in the text file containing the contact names
sm = tbh_skype_interface.tbh_skype_interface_t( contacts_file = skype_contacts_dict )

# Initialize the audio listener, has its own thread
al = tbh_audio_listener.tbh_audio_listener_t( \
    microphone_name = 'stereo', temp_audio_storage_path = \
        '../../tbh_top_level/audio_files' )

al_thread = threading.Thread( target=al.run )
al_thread.start()

# Initialize the storage module
ds = tbh_data_storage.tbh_data_storage_t( '../logfiles' )

# ---- SET UP CALLBACKS ---- #
# 1. Once the audio listener has created an utterance, it passes an
# audio WAV file to the speech recognizer, saves the audio
al.add_end_of_audio_handler( sr.process_raw_audio_handler )
al.add_poll_audio_handler( dm.process_raw_audio_handler )

# 2. Once the speech recognizer has processed the WAV file, it passes
# the n-best list of speech hypotheses to the dialogue manager, save
sr.add_processed_audio_event_handler( dm.process_nbest_handler )

# 3. Once the dialogue manager has processed the n-best list, it
# passes a set of actions to: 
dm.add_processed_nbest_event_handler( al.process_action_handler )
dm.add_processed_nbest_event_handler( sr.process_action_handler )
#dm.add_processed_nbest_event_handler( ds.nbest_action_storage_handler )
#dm.add_processed_nbest_event_handler( pdv.execute_action_handler )

dm.add_processed_audio_event_handler( al.process_action_handler )
#dm.add_processed_audio_event_handler( ds.audio_action_storage_handler )
# dm.add_operate_phone_event_handler( sm.execute_action_handler )

# ---- SET UP GUI, CALLBACKS ---- #

app = PyQt4.QtGui.QApplication(sys.argv)
gui_thread = tbh_output_interface.tbh_gui_thread()

# At the start of an utterance, the GUI's system_state label indicates
# that it is "listening" (unless it is asleep)
al.add_start_of_audio_handler( gui_thread.gui_manager.start_of_audio_handler )

# At the end of an utterance, the GUI's system_state label indicates
# that it is "thinking" (unless it is asleep)
al.add_end_of_audio_handler( gui_thread.gui_manager.end_of_audio_handler )

# Once the speech recognizer determines the n-best hypotheses, the GUI
# shows some representation of the n-best list (currently, just the
# best hypothesis)
sr.add_processed_audio_event_handler( gui_thread.gui_manager.show_nbest_handler )
sr.add_processed_audio_event_handler( gui_thread.gui_manager.system_message_handler )
dm.add_processed_nbest_event_handler( gui_thread.gui_manager.execute_action_handler )
dm.add_processed_nbest_event_handler( gui_thread.gui_manager.end_of_processing_handler )

# for plotting the belief vector
# An event for the plotting function
dm.add_processed_nbest_event_handler( gui_thread.pomdp_data_viz.update_belief_handler )

# when we reset a belief
gui_thread.gui_manager.add_reset_belief_event_handler( dm.start_new_dialog_handler )
gui_thread.gui_manager.add_reset_belief_event_handler( gui_thread.pomdp_data_viz.reset_belief_handler )


#gui_thread.gui_manager.add_reset_belief_event_handler( ds.start_new_dialog_handler )


# Skype callbacks to the GUI
#sm.add_skype_event_handler( gui_thread.gui_manager.show_skype_event_handler )
#sm.add_skype_event_handler( sr.process_skype_event_handler )

# 
dm.add_experiment_event_handler( gui_thread.gui_manager.experiment_event_handler ) 


# ---- START THE MAIN LOOP ---- #
gtk.main()
sys.exit(app.exec_())


