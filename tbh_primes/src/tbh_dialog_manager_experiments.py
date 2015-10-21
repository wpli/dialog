# Anything called a "dialog manager" must support the following callbacks/handlers:
# * process_nbest_handler( self , param_dict ) callback that populates
#   the action_dict of the param_dict once the nbest list in
#   param_dict is there
# * add_processed_nbest_event_handler( self, handler ) that takes in
#   functions that should be called after the nbest is processed
# * add_operate_phone_event_handler( self , handler ) that takes in
#   functions that should be called if phone needs operating
#
# The action_dict must have the following fields; in all cases, a
# field marked with None means that the system should keep any
# previously stored or default value
# * audio_listener_(minspeech, prespeech, holdover, power)_threshold: numbers
# * speech_recognizer_grammar: name of the grammer
# * speech_recognizer_recompute_nbest: redo the nbest
# * gui_suggestions: text to print out in the suggestions panel
# * gui_answer_text: text to print out in the response panel
# * dialog_manager_answer_code: coding of the type of action taken 
# * gui_state: what the gui's new state should be 
# * gui_voice_synthesizer_on: boolean
# * data_storage_keep_audio_file: boolean
# * dialog_manager_reset_dialog: boolean
# * skype_manager_phone_action: stuff for skype

# These imports are COMMON for all DMs
# general imports
import threading
import functools

# for the feature set
import sys
sys.path.append( '../../tbh_compute_text_feature_set/src/' )
import tbh_compute_text_feature_set
sys.path.append( '../../tbh_compute_audio_feature_set/src/' )
import tbh_compute_audio_feature_set

import numpy

# action code management
import tbh_action_code_manager_experiments as tbh_action_code_manager
import tbh_action_dict_manager_experiments as tbh_action_dict_manager
import tbh_pomdp_manager_experiments as tbh_pomdp_manager

# These imports are CUSTOM for your DM
import re
from math import log

import tbh_experiment_controller


# Import the tbh_skype_interface in order to get the load_skype_contacts function
sys.path.append( '../../tbh_skype_interface/src/' )
import tbh_skype_interface


# Import the POMDP utilities
sys.path.append( '../../tbh_pomdp_util/src/' )
import tbh_pomdp_util

import time

DIALOG_DATA_PATH = '../../tbh_top_level/src/dialog_data.mat' 

USE_CONFIDENCE_SCORES = True
USE_SYNTHETIC_DATA = False
USE_DATA_OBSERVATION_FUNCTION = False

#-------------------------------------------------
## 
# Description:
# Handles the dialog and how the system responds to inputs of natural
# language text
class tbh_dialog_manager_t:
    ##
    # Description
    # Initalizes dialog manager
    def __init__( self, feature_type_list, dialog_data_path = DIALOG_DATA_PATH, \
                      skype_contacts_dict=None, \
                      high_confidence_histogram = None, \
                      low_confidence_histogram = None ): 

        # --- COMMON --- #
        # These internal state you probably want in any dialog manager
        self._processed_nbest_event_handler_list = []
        self._processed_audio_event_handler_list = []
        self._operate_phone_event_handler_list = []
        self.feature_type_list = feature_type_list


        # --- FOR EXPERIMENTS --- #
        self._experiment_event_handler_list = []

        # --- CUSTOM --- #
        # These internal state are specific to this dialog manager
        self.system_state = 'sleeping'
        self.window_size = 50;
        self.audio_power_list = [];
        
        # for confidence modeling
        self.high_confidence_histogram = high_confidence_histogram
        self.low_confidence_histogram = low_confidence_histogram

        # For our simple dialog system, we have a confirmation buffer
        # the user needs to confirm in order to complete the above action
        self.confirmation_buffer = None
        
        if skype_contacts_dict != None: 
            self.skype_contacts_dict = skype_contacts_dict
        else:
            self.skype_contacts_dict = None
        
        # --- CUSTOM --- # 
        # This is for the POMDP dialog manager
        dialog_data = tbh_pomdp_util.get_matlab_dialog_data( dialog_data_path )
        self.pomdp = tbh_pomdp_util.get_pomdp( dialog_data )       
        self.Q = tbh_pomdp_util.get_Q( dialog_data )
        self.machine_action = None

        # FOR EXPERIMENTS
        self.experiment_controller = \
            tbh_experiment_controller.experiment_controller()

        self.current_experiment_log = None

        """
        # Initialize a new experiment log
        self.current_experiment_log = \
            tbh_experiment_controller.experiment_log( \
            self.experiment_controller.get_current_experiment() )
        """

    # ---------------- COMMON HANDLER FUNCTIONS -------------- #
    # These are probably going to be same for every dialog manager;
    # you don't need to adjust these
    # Description
    # Stuff for managing the speech recognizer events/callbacks
    def _processed_nbest_event( self, param_dict ):
        for handler in self._processed_nbest_event_handler_list:
            t = threading.Thread( target=functools.partial( handler , param_dict ) )
            t.start()

    # Description
    # Stuff for managing the speech recognizer events/callbacks
    def _processed_audio_event( self, param_dict ):
        for handler in self._processed_audio_event_handler_list:
            t = threading.Thread( target=functools.partial( handler , param_dict ) )
            t.start()

    ##
    # Description
    # Stuff for managing the speech recognizer events/callbacks
    def _process_phone_event( self, phone_action ):
        for handler in self._operate_phone_event_handler_list:
            t = threading.Thread( \
                target=functools.partial( handler , phone_action ) )
            t.start()

    def _experiment_event( self, experiment_controller ):
        for handler in self._experiment_event_handler_list:
            t = threading.Thread( \
                target=functools.partial( handler , experiment_controller  ) )
            t.start()

    ##
    # Description
    # Adds more handlers for when nbest stuff needs processing
    def add_processed_nbest_event_handler( self, handler ):
        self._processed_nbest_event_handler_list.append( handler )

    ##
    # Description
    # Adds more handlers for when nbest stuff needs processing
    def add_processed_audio_event_handler( self, handler ):
        self._processed_audio_event_handler_list.append( handler )

    ##
    # Description
    # Adds more handlers for when skype stuff needs processing
    def add_operate_phone_event_handler( self, handler ):
        self._operate_phone_event_handler_list.append( handler )

    ##
    # Description
    # Adds more handlers for when skype stuff needs processing
    def add_experiment_event_handler( self, handler ):
        self._experiment_event_handler_list.append( handler ) 

    # ---------------- DM CALLBACK FUNCTION/SUPPORT -------------- #
    # Top level/most important dm function: takes in a param_dict with
    # an nbest_list, populates with action_dict, and then passes the
    # calls the handlers.  (You probably want to keep the last line
    # the same, but the rest is the customized dialog management code)

    ## 
    # Description
    # Takes a raw audio power and decides what should happen
    def process_raw_audio_handler( self , param_dict ):

        # store the audio into our buffer
        self.audio_power_list.append( param_dict[ 'audio_power' ] )
        if len( self.audio_power_list ) > self.window_size:
            self.audio_power_list = self.audio_power_list[1:]

        # compute audio features
        feature_set = tbh_compute_audio_feature_set.compute_feature_set( self.audio_power_list )
        param_dict[ 'feature_set' ] = feature_set
        
    ##
    # Description 
    # Takes an nbest list and decides what should happen.  This
    # function should be COMMON for all DMs EXCEPT for any changes to
    # the system state.  Cusomize determine_action below to customize
    # the choices that your DM makes
    def process_nbest_handler( self , param_dict ):
        
        # ----- COMMON TO ALL DMs ----- #                        
        # Fill in action parts away from defaults: 
        # Using confidence scores 
        feature_set_list = []

        # if we want all 10 hypotheses:
        # use this for computing confidence scores

        ### custom for this experiment ###
        ### for computing the confidence score
        action_code_list = []
        for index, nbest_item in enumerate( param_dict['nbest_list'] ):
            feature_set = \
                tbh_compute_text_feature_set.compute_feature_set( \
                [ nbest_item ], self.feature_type_list )
            action_code = self.determine_action_code( feature_set )
            action_code_list.append( action_code )

        if len( action_code_list ) > 0:
            top_action_code = action_code_list[0]
            confidence_score = 0
            for code in action_code_list:
                if code == top_action_code:
                    confidence_score += 0.1
            confidence_score = confidence_score / float( len( action_code_list ) ) * 10 - 0.03
        else:
            confidence_score = 0

        print "CONFIDENCE SCORE:", confidence_score

        ### end of computing confidence score



        #### LOAD ENTRIES INTO PARAM_DICT
        param_dict['confidence_score'] = confidence_score
        feature_set = \
            tbh_compute_text_feature_set.compute_feature_set( \
            param_dict['nbest_list'] , self.feature_type_list )
        # add feature set to param_dict for storage and other purposes
        param_dict[ 'feature_set' ] = feature_set


        # for the pomdp
        # Search over the features to determine the right action

        # --- CUSTOM TO YOUR DM --- #
        # Adjust things based on this action dictionary and send to
        # everyone who might want to use it

        # ----- COMMON TO ALL DMs ----- #
        # Send the action_dict to everyone that might need it: common
        # to all dialog managers; you probably don't want to change
        # this part of the code.

        #if action_dict['skype_manager_phone_action'] is not None:
        #    self._process_phone_event( action_dict['skype_manager_phone_action'] )


        if self.current_experiment_log.experiment_name[0] == "POMDP":
            action_dict = self.determine_action_confidence( param_dict )
            self.machine_action = action_dict['pomdp_dict']['new_machine_action']
            self.belief_for_policy = action_dict['pomdp_dict']['belief_for_policy']

            print "\n================="
            print "CURRENT POLICY"
            print self.belief_for_policy
            print "================="

            #print "==========BELIEF=========="
            #print self.belief_for_policy
            #print "=========================="

            # Update the belief as appropriate
            self.pomdp.belief = action_dict['pomdp_dict']['final_belief']

            current_turn = tbh_experiment_controller.experiment_turn( \
                time = time.time(), \
                    utterance_file = None, \
                    param_dict = param_dict, \
                    utterance_hypothesis = param_dict['nbest_list'][0]['text'],
                    hypothesis_code = \
                    self.determine_action_code( param_dict['feature_set'] ), \
                    confidence_score = confidence_score, \
                    system_response = \
                    action_dict['pomdp_dict']['new_machine_action'] )

        elif self.current_experiment_log.experiment_name[0] == "THRESHOLD":
            threshold = 0.75
            action_dict = self.determine_action_threshold( param_dict, threshold )
            self.belief_for_policy = tbh_pomdp_util.reset_belief( self.pomdp )
            self.pomdp.belief = tbh_pomdp_util.reset_belief( self.pomdp )

            if confidence_score < threshold:
                self.machine_action = action_dict['pomdp_dict']['new_machine_action']

                current_turn = tbh_experiment_controller.experiment_turn( \
                    time = time.time(), \
                        utterance_file = None, \
                        param_dict = param_dict, \
                        utterance_hypothesis = param_dict['nbest_list'][0]['text'],
                        hypothesis_code = \
                        self.determine_action_code( param_dict['feature_set'] ), \
                        confidence_score = confidence_score, \
                        system_response = \
                        action_dict['pomdp_dict']['new_machine_action'] )

            else:
                self.machine_action = action_dict['pomdp_dict']['new_machine_action']

                current_turn = tbh_experiment_controller.experiment_turn( \
                    time = time.time(), \
                        utterance_file = None, \
                        param_dict = param_dict, \
                        utterance_hypothesis = param_dict['nbest_list'][0]['text'],
                        hypothesis_code = \
                        self.determine_action_code( param_dict['feature_set'] ), \
                        confidence_score = confidence_score, \
                        system_response = \
                        self.determine_action_code( param_dict['feature_set'] ) )

        else:
            raise NameError( 'neither option as name of experiment' )


        self.current_experiment_log.turn_list.append( current_turn )

        # print self.current_experiment_log.turn_list

        # add this to the param_dict
        param_dict[ 'action_dict' ] = action_dict      
        
        if len( self.current_experiment_log.turn_list ) > 0:
            for turn in self.current_experiment_log.turn_list:
                print turn.time, turn.utterance_file, turn.utterance_hypothesis, turn.hypothesis_code, turn.confidence_score, turn.system_response

        self._processed_nbest_event( param_dict )

    ## CALLBACK FROM THE GUI
    def start_new_dialog_handler( self ):
        pomdp_dict = tbh_pomdp_manager.unit_test_reset_belief( self.pomdp )
        action_dict = {}
        action_dict[ 'pomdp_dict' ] = pomdp_dict
        self.machine_action = pomdp_dict['new_machine_action']        
        self.belief_for_policy = pomdp_dict['belief_for_policy']
        self.pomdp.belief = pomdp_dict['final_belief']


        # write the log to file
        if self.current_experiment_log != None:
            self.current_experiment_log.add_end_time( time.time() )
            self.experiment_controller.current_log.append( self.current_experiment_log )
            self.experiment_controller.write_log()

        # we should also be doing new data storage here
        # as opposed to relying on the output interface to do this

        # experiment controller
        self.experiment_controller.increment_counter()

        # create a new experiment log
        self.current_experiment_log = \
            tbh_experiment_controller.experiment_log( \
            self.experiment_controller.get_current_experiment() )

        self._experiment_event( self.experiment_controller )




    def determine_action_threshold( self, param_dict, threshold ):
        confidence_score = param_dict['confidence_score']
        if confidence_score < threshold:
            action_code = [ 'null', 'yes_record' ]
            confidence_score = 0.5
        else:
            action_code = self.determine_action_code( param_dict['feature_set'] )
            confidence_score = 0.999

        pomdp_dict = self.determine_pomdp_dict( \
            action_code, param_dict, \
            use_confidence_scores=True, \
                confidence_score=confidence_score )

        action_dict = \
            tbh_action_dict_manager.process_code( \
            pomdp_dict['new_machine_action'] )

        action_dict['pomdp_dict'] = pomdp_dict
        return action_dict

    ## 
    # Description
    # uses confidence scores
    def determine_action_confidence( self, param_dict ):

        # determine the action code in question
        action_code = self.determine_action_code( param_dict['feature_set'] )

        confidence_score = param_dict['confidence_score']

        pomdp_dict = self.determine_pomdp_dict( \
            action_code, param_dict, \
            use_confidence_scores=True, \
                confidence_score=confidence_score )

        # Include the belief vector in the action_dict also
        action_dict = \
            tbh_action_dict_manager.process_code( \
            pomdp_dict['new_machine_action'] )

        action_dict['pomdp_dict'] = pomdp_dict
        
        return action_dict    


    def determine_action_code( self, feature_set ):
        self.system_state == 'awake'
        action_code = [ 'null', 'yes_record' ]


        if 1:
            # Consider each of the possible actions Note: the
            # else-if structure means that only one action code is
            # possible in this current dialog manager

            #for item in feature_set['tbh_keyword_sequence'].keys():
            #    print item, feature_set['tbh_keyword_sequence'][item]

            ## SYSTEM COMMANDS
            if ( feature_set['tbh_keyword']['yes'] or \
                feature_set['tbh_keyword']['yeah'] or \
                feature_set['tbh_keyword']['confirming'] ):
                action_code = [ 'confirmatory', 'yes']
            elif feature_set['tbh_keyword']['no'] or \
                    feature_set['tbh_keyword']['nope']:
                action_code = [ 'confirmatory', 'no' ]
            elif feature_set['tbh_keyword_sequence']['wake_up'] or \
                    feature_set['tbh_keyword_sequence']['good_day']:
                action_code = [ 'system', 'wake_up' ]
            elif feature_set['tbh_keyword_sequence']['go_to_sleep'] or \
                    feature_set['tbh_keyword_sequence']['good_night']:
                action_code = [ 'system', 'go_to_sleep' ]
            #elif feature_set['tbh_keyword_sequence']['listen_up'] or \
            #        feature_set['tbh_keyword_sequence']['enter_attentive_mode']:
            #    action_code = [ 'system', 'enter_attentive_mode' ]
            #elif feature_set['tbh_keyword_sequence']["that's_all"] or \
            #        feature_set['tbh_keyword_sequence']['exit_attentive_mode']:
            #    action_code = [ 'system', 'exit_attentive_mode' ]
            else:

                self.system_state = 'awake'

                ## VOICE SYNTHESIZER COMMANDS             
                if feature_set['tbh_keyword_sequence']['audio_on'] or \
                        feature_set['tbh_keyword_sequence']['voice_on']:
                    action_code = [ 'voice_synthesizer', 'audio_on' ]
                elif feature_set['tbh_keyword_sequence']['audio_off'] or \
                        feature_set['tbh_keyword_sequence']['voice_off']:
                    action_code = [ 'voice_synthesizer', 'audio_off' ]
                elif feature_set['tbh_keyword']['interrupt'] or \
                        feature_set['tbh_keyword_sequence']['be_quiet'] or \
                        feature_set['tbh_keyword']['quiet']:
                    action_code = [ 'voice_synthesizer', 'interrupt' ]
                elif feature_set['tbh_keyword_sequence']['speak_it'] or \
                        feature_set['tbh_keyword_sequence']['say_it'] or \
                        feature_set['tbh_keyword_sequence']['speak_text_on_screen'] or \
                        feature_set['tbh_keyword_sequence']['say_text_on_screen'] or \
                        ( feature_set['tbh_keyword']['say'] and \
                              feature_set['tbh_keyword']['again'] ):
                    action_code = [ 'voice_synthesizer', 'speak_text_on_screen' ]

                ## ACTIVITIES
                elif feature_set['tbh_keyword']['activity'] or \
                        feature_set['tbh_keyword']['activities'] or \
                        feature_set['tbh_keyword']['schedule'] or \
                        feature_set['tbh_keyword']['events']:

                    # Determine which day of the week
                    day = self.determine_day( feature_set )
                    action_code = [ 'activities', day ]

                ## MEALS
                elif feature_set['tbh_keyword']['breakfast']:
                    day = self.determine_day( feature_set )
                    action_code = ['breakfast', day ]

                elif feature_set['tbh_keyword']['lunch']:
                    day = self.determine_day( feature_set )
                    action_code = ['lunch', day ]

                elif feature_set['tbh_keyword']['dinner'] or feature_set['tbh_keyword']['supper']:
                    day = self.determine_day( feature_set )
                    action_code = [ 'dinner', day ]

                # Note that the search for "menus" comes after
                # 'breakfast', 'lunch', 'dinner' or 'supper'; this
                # means that none of those keywords appeared, and that
                # the user wants "general" menus
                #elif feature_set['tbh_keyword']['menus'] or \
                #        feature_set['tbh_keyword']['menu']:
                #    day = self.determine_day( feature_set )
                #    action_code = [ 'menus', day ]

                ## WEATHER
                elif feature_set['tbh_keyword']['weather'] or \
                        feature_set['tbh_keyword']['forecast'] or \
                        feature_set['tbh_keyword']['temperature']:                        
                    if feature_set['tbh_keyword_sequence']['three_day'] or \
                            feature_set['tbh_keyword_sequence']['four_day']:
                        parameter = 'three_day'
                    else:
                        parameter = self.determine_day( feature_set )
                    action_code = [ 'weather', parameter ]

                ## TIME/DATE
                elif feature_set['tbh_keyword']['time']:
                    action_code = [ 'time', 'time' ]

                elif feature_set['tbh_keyword']['date'] or \
                        feature_set['tbh_keyword']['day']:
                    action_code = [ 'time', 'date' ]                

                # SKYPE PHONE OPERATIONS
                elif feature_set['tbh_keyword_sequence']['make_phone_call'] or \
                        feature_set['tbh_keyword_sequence']['make_a_phone_call']:
                    action_code = [ 'phone', 'make_phone_call' ]

                elif feature_set['tbh_keyword_sequence']['resume_call'] or \
                        feature_set['tbh_keyword']['resume']:
                    action_code = [ 'phone', 'resume_call' ]

                elif feature_set['tbh_keyword_sequence']['answer_phone'] or \
                        feature_set['tbh_keyword']['answer']:
                    action_code = [ 'phone', 'answer_phone' ]

                #elif feature_set['tbh_keyword']['extension'] and \
                #        ( feature_set['tbh_keyword']['dial'] or \
                #              feature_set['tbh_keyword']['call'] ):
                #    action_code = [ 'phone', 'dial_extension' ]

                elif feature_set['tbh_keyword_sequence']['who_can_i_talk_to'] or \
                        feature_set['tbh_keyword_sequence']['whom_can_i_talk_to'] or \
                        feature_set['tbh_keyword_sequence']['show_phone_list'] or \
                        feature_set['tbh_keyword_sequence']['show_contacts']:
                    action_code = [ 'phone', 'show_contacts' ]

                elif feature_set['tbh_keyword']['hold'] and \
                        feature_set['tbh_keyword']['call']:
                    action_code = [ 'phone', 'hold_call' ]

                elif feature_set['tbh_keyword_sequence']['hang_up'] or \
                        feature_set['tbh_keyword_sequence']['end_call']:

                    action_code = [ 'phone', 'hang_up' ]

                elif feature_set['tbh_keyword_sequence']['full_screen_video'] or \
                        feature_set['tbh_keyword_sequence']['maximize_video']:
                    action_code = [ 'phone', 'fullscreen_video']
                elif feature_set['tbh_keyword_sequence']['minimize_video']:
                    action_code = [ 'phone', 'unfullscreen_video']

                #elif feature_set['tbh_keyword_sequence']['next_page']:
                #    action_code = [ 'phone', 'next_page' ]
                ## VOICE DIAL
                #elif feature_set['tbh_keyword']['cancel'] or \
                #        feature_set['tbh_keyword']['exit']:
                #    action_code = [ 'voice_dial', 'cancel' ]

                #elif feature_set['tbh_keyword']['dial'] and \
                #        feature_set['tbh_keyword']['number']:
                #    action_code = [ 'voice_dial', 'dial_number' ]

                #elif feature_set['tbh_keyword']['finished']:
                #    action_code = [ 'voice_dial', 'finished' ]

                #elif feature_set['tbh_keyword']['restart'] or \
                #        feature_set['tbh_keyword_sequence']['start_over'] or \
                #        feature_set['tbh_keyword_sequence']['start_again']:
                #    action_code = [ 'voice_dial', 'start_over' ]


                ## CALL CONTACT
                # Note that the search for 'call' comes after the phone call commands
                #elif feature_set['tbh_keyword']['call']:                    
                #    contact = self.determine_user_specific_contact( feature_set )

                    # Confirmation buffer code
                    # This will now be handled by the POMDP
                    '''

                    if contact != 'unknown':
                        self.confirmation_buffer = [ 'call_contact', [ contact ] ]
                        action_code = [ 'system', \
                                            ['request_confirmation', \
                                                 'call_contact', contact ] ]
                    else:
                        action_code = [ 'call_contact', 'unknown' ]
                    '''

                #    if contact != 'unknown':
                #        action_code = [ 'call_contact', [ str( contact ) ] ]
                #    else:
                #        action_code = [ 'call_contact', 'unknown' ]


                #    self.system_state = 'attentive'

                #elif feature_set['tbh_keyword']['cancel']:
                #    action_code = ['system', 'wake_up']

                # Did not parse successfully
                else:
                    action_code = [ 'null', 'yes_record' ]

        return action_code

    def determine_pomdp_dict( self, action_code, \
                                  param_dict=None, \
                                  use_confidence_scores=False, \
                                  confidence_score=1 ):

        # For POMDP dialog manager, pass to a POMDP belief update algorithm
        # Key update: using the confidence scores
        pomdp_dict = tbh_pomdp_manager.process_result( \
            self.pomdp, action_code, self.machine_action, \
                self.Q, param_dict, use_confidence_scores=True, \
                skype_contacts_dict=self.skype_contacts_dict, \
                high_confidence_histogram=self.high_confidence_histogram, \
                low_confidence_histogram=self.low_confidence_histogram, \
                confidence_score=confidence_score )
            
        # This is for the next belief update

        return pomdp_dict

    # ------------------- TEXT PARSING UTILS -------------------- #
    ## 
    # Description: 
    # Get which day of the week should be the parameter argument for
    # weather, activities, and meal choices Note: this function does
    # not consider the case where more than one "day of week" feature
     # is activated; it might
    def determine_day( self, feature_set ):
        possible_days = [ "today", "tomorrow", "monday", "tuesday", \
                              "wednesday", "thursday", "friday", \
                              "saturday", "sunday" ]

        # default day: today
        day = "today"
            
        # Default choice for day is "today"
        for possible_day in possible_days:

            if feature_set['tbh_keyword'][possible_day] or \
                    feature_set['tbh_keyword'][possible_day + "'s"]:
                #print day
                day = possible_day
                break

        # other possibility: 'tonight' maps to 'today' in the days in the set of possible actions
        if feature_set['tbh_keyword']['tonight'] or feature_set['tbh_keyword']["tonight's"]:
            day = 'today'

        return day

    ## 
    # Description:
    # Get the right contact based on the specific user
    def determine_user_specific_contact( self, feature_set ):
        # desired_contact is an integer 
        # between 1 and 20 mapping to the actual desired contact
        desired_contact = 'unknown'

        # Create dictionary mapping keywords to contact id numbers
        spoken_name_to_id_dict = {}
        for key in self.skype_contacts_dict:
            spoken_name_to_id_dict[self.skype_contacts_dict[key]['spoken_name']] = key

        number_map = { 'one' : 1, 
               'two' : 2, 
               'three' : 3,
               'four' : 4,
               'five' : 5,
               'six' : 6,
               'seven': 7,
               'eight': 8,
               'nine': 9,
               'ten' : 10, 
               'eleven': 11, 
               'twelve': 12, 
               'thirteen': 13, 
               'fourteen': 14,
               'fifteen': 15, 
               'sixteen': 16, 
               'seventeen': 17, 
               'eighteen': 18, 
               'nineteen': 19,
               'twenty': 20 }

        # Add the number map
        for word in number_map:
            spoken_name_to_id_dict[word] = number_map[word]


        # Determine who the desired contact is from the feature set        
        for possible_contact in feature_set['tbh_skype_contact'].keys():
            if feature_set['tbh_skype_contact'][possible_contact]:
                desired_contact = spoken_name_to_id_dict[possible_contact]
                break

        # This function returns the desired contact integer code or 'unknown'
        return desired_contact
                
    ##
    # Description:
    # Gets the confirmation text for the item
    def get_confirmation_text( self, max_key ):
        confirmation_string = "Do you want %s?" % self.speech_to_action_map[max_key]['confirmation_predicate'] 
        return confirmation_string

    ##
    # Description:
    # For a given string, find the appropriate action code
    def find_action( self, statement ):
        candidate_action_codes = []
        for possible_action, action_info in self.speech_to_action_map.items():
            #"keywords" is a list of at least length 1                                    
            keywords = action_info['keyword_sets'] 

            # possible keyword is a single keyword, or multiple keywords
            for possible_keyword in keywords:

                # case in which there are multiple keywords that must match
                if ',' in possible_keyword:
                    possible_keyword_list = possible_keyword.split(', ')
                    for keyword in possible_keyword_list:
                        possible_keywords_found = True
                        if string_find( statement, keyword ):
                            pass
                        else:
                            possible_keywords_found = False
                            break

                    if possible_keywords_found:
                        candidate_action_codes.append( [ possible_action, \
                                                             possible_keyword ] )


                else:
                    if string_find( statement, possible_keyword ):
                        candidate_action_codes.append( [ possible_action, \
                                                             possible_keyword ] )


        # pick the action code for which the most keywords matches                                  
        # if there is a tie, there are a few tie-breaking rules:
        #     choose the action with the matching string with the most words
        #     this will allow "good day" to match to "good day" instead of "day"
        #     if it is still tied, just pick the first one
        if len( candidate_action_codes ) == 0:
            action_code = 0
        elif len( candidate_action_codes ) == 1:
            action_code = int( candidate_action_codes[0][0] )
        else:
            most_keywords_matched = 0
            for entry in candidate_action_codes:                

                #keywords_matched = len( entry[1].split( ', ' ) )
                keywords = entry[1].split( ', ' )
                number_of_matching_words = 0
                for word in keywords:
                    individual_words = word.split()
                    number_of_matching_words += len( individual_words ) 

                if number_of_matching_words > most_keywords_matched:                    
                    
                    most_keywords_matched = number_of_matching_words
                    action_code = int( entry[0] )



        return action_code

# ------------------- GLOBAL UTILS --------------------- #
## Description
# Generic string find function Looks for entire words/strings If the
# given query is found, returns true
def string_find( statement, query_string ):
    string_found = False
    temp_statement = repr( statement )
    raw_statement_string = temp_statement[1:-1]
    temp_query_string = repr( query_string )
    raw_query_string = temp_query_string[1:-1]
    if re.search(r'\b' + raw_query_string + r'\b', raw_statement_string):
	string_found = True
    return string_found

# ----- Unit test ------ #
            
