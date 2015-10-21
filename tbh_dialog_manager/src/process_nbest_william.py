## Description
# dialog management system, largely using system logic
import sys
sys.path.append( '../../tbh_action_map/src/' )
import tbh_action_map 

import tbh_answer_text_manager
import re
import math
from math import log
import numpy as np

## For unit testing only
sys.path.append( '../../tbh_top_level/src/' )
import tbh_user_profile 


WAKE_UP_CODE = 24
YES_CODE = 22
NO_CODE = 23
MINIMUM_CONFIRMATION_THRESHOLD = 0.50

INFORMATION_CONFIDENCE = 0.94
PHONE_CONFIDENCE = 0.99

class process_nbest_list():
   
    def __init__( self, user_profile=None, test_mode=False ):

        self.speech_to_action_map = \
            tbh_action_map.get_speech_to_action_map()

        if test_mode:
            self.user_profile = tbh_user_profile.tbh_user_profile_t( 0 )
        else:
            self.user_profile = user_profile

        self.intent_matrix = self.initialize_intent_matrix()

        self.answer_text_manager = \
            tbh_answer_text_manager.tbh_answer_text_manager_t()


    def determine_action( self, nbest_list, state_information ):

        # For now, we
        # will simply use the best hypothesis and discard score
        # information
        input_text = nbest_list[0]['text'].replace( "_", " " )

        # make state and intent vectors easier to refer to
        system_state = state_information['system_state']
        intent_vector = state_information['input_intent_vector']        

        # Initialize the intent vector if it is None
        # This allows to initialize the vector in this class
        # instead of in the higher-level dialog manager
        # Currently, we initialize the intent vector to have 
        # uniform probability over all possible user goals
        if intent_vector == None:
            self.intent_vector = self.initialize_intent_vector()

        # Future commands here could change the intent vector based on
        # the system state or other factors
        action_dict = { 'gui_answer' : None, 
                        'voice_synthesizer_answer': None,
                        'gui_suggestions': None, 
                        #'gui_change_system_state': False,
                        #'gui_desired_system_state': None,
                        'gui_new_system_state': None,
                        'speech_recognizer_new_system_state': None,
                        #'speech_recognizer_change_system_state': False,
                        #'speech_recognizer_new_system_state': None,
                        #'gui_change_voice_synthesizer_state': False,
                        #'gui_desired_voice_synthesizer_state': None,
                        'gui_new_voice_synthesizer_state': None,
                        'dialog_manager_reset_dialog_state': False,
                        'skype_manager_operate_phone': False,
                        'skype_manager_phone_action': None,
                        'gui_ask_for_keyword': False,
                        'gui_did_not_understand': False,
                        'data_storage_keep_audio_file': True
                        #'output_intent_vector': None
                        }

        output_intent_vector = None
        # The presence determines whether the segment is accepted
        # This is entirely deterministic
        # the self.find_keyword function returns True if:
        # the keyword rule is met OR 
        # the system is in "attentive" state
        keyword_found = self.find_keyword( 
            input_text, \
                state_information['system_state'] )
    

        # a keyword not found means that the system should ask for the
        # keyword
        if keyword_found == False:

            if system_state == 'sleeping':
                action_dict['data_storage_keep_audio_file'] = False
            
            else:
                action_dict['gui_answer'] = \
                    "Please say a keyword before your command."

                action_dict['voice_synthesizer_answer'] = \
                    "Please say a keyword before your command."

                action_dict['data_storage_store_audio_file'] = False

                action_dict['gui_suggestions'] = self.determine_suggestions()
                action_dict['gui_ask_for_keyword'] = True

        # If the keyword is detected, then we can go through the
        # action decision process
        else:
            
            # Parse the transcript to determine the appropriate action
            # code
            action_code = self.find_action( input_text )
           
            # The only command that will trigger anything while the
            # system is sleeping is if the command is to wake up the
            # system
            if system_state == 'sleeping':
                # This is an entirely deterministic decision
                if action_code == WAKE_UP_CODE:
                    action_dict['gui_answer'] = "Ready to answer questions."
                    action_dict['voice_synthesizer_answer'] = "Ready to answer questions."
                    # action_dict['gui_change_system_state'] = True
                    action_dict['dialog_manager_reset_dialog_state'] = True
                    action_dict['gui_new_system_state'] = 'awake'

                    # Set the system state variable for the speech system also
                    action_dict['speech_recognizer_new_system_state'] = 'awake'
                    action_dict['data_storage_store_audio_file'] = True
                else:
                    action_dict['data_storage_store_audio_file'] = True

            # If the action code was 0, do nothing
            elif action_code == 0:
                # We will store the data because the keyword was
                # detected, which strongly suggests that an utterance
                # was heard
                action_dict['data_storage_store_audio_file'] = True


            # If the system is awake or attentive, then we can process
            # other possible actions
            else:
                action_dict['data_storage_store_audio_file'] = True

                if action_code not in self.intent_vector.keys():

                    inverted_dict = dict( \
                        map( lambda item: (item[1],item[0]),self.intent_vector.items() ) )

                    max_key = inverted_dict[max(inverted_dict.keys())]

                    # Ask for confirmation if there is a potential intent
                    # that exceeds a certain minimum threshold
                    if max( self.intent_vector ) > MINIMUM_CONFIRMATION_THRESHOLD:

                        if action_code == YES_CODE:

                            numerator_entries = {}
                            for c in self.intent_vector.keys():
                                numerator_entries[c] = \
                                    self.intent_vector[c] + \
                                    self.intent_matrix[c][max_key]

                            denominator = np.logaddexp.reduce( \
                                numerator_entries.values() )

                            for code in self.intent_vector.keys():
                                self.intent_vector[code] = \
                                    numerator_entries[code] - denominator

                            category = self.speech_to_action_map[max_key]['category']


                        elif action_code == NO_CODE:

                            # Reset the intent vector
                            self.intent_vector = self.initialize_intent_vector()                    
                            action_dict['dialog_manager_reset_dialog_state'] = True
                            action_dict['gui_answer'] = "Ready to answer questions."
                            # If the system is already awake, then
                            # we determine the probabilities of
                            # each possible intent P(intent|code)
                            # = P(code|intent)P(intent)/P(code)

                else:

                    numerator_entries = {}
                    for c in self.intent_vector.keys():
                        numerator_entries[c] = \
                            self.intent_vector[c] + self.intent_matrix[c][action_code]

                    denominator = np.logaddexp.reduce( numerator_entries.values() )

                    for code in self.intent_vector.keys():
                        self.intent_vector[code] = numerator_entries[code] - denominator

                    # print self.intent_vector[action_code]


                inverted_dict = dict( \
                    map( lambda item: (item[1],item[0]),self.intent_vector.items() ) )

                max_key = inverted_dict[max(inverted_dict.keys())]

                #print "Action with highest probability: %s" % \
                #    self.speech_to_action_map[max_key]['action']
                #print "Probability: %s" % exp( self.intent_vector[max_key] )


                # Invert the dictionary and print max key
                inverted_dict = dict( \
                    map( lambda item: (item[1],item[0]),self.intent_vector.items() ) )

                max_key = inverted_dict[max(inverted_dict.keys())]
                # print max_key
                # print math.exp( self.intent_vector[max_key] )

                category = self.speech_to_action_map[max_key]['category']
                print category
                if category in ( 'time', 'activities', 'weather', 'menus' ):
                    confidence = INFORMATION_CONFIDENCE
                elif category in ( 'phone_call', 'digits' ):
                    confidence = PHONE_CONFIDENCE
                else:
                    confidence = INFORMATION_CONFIDENCE
                

                if self.intent_vector[max_key] > log( confidence ):

                    output_text = \
                        self.answer_text_manager.get_answer_text( \
                        max_key )
                    

                    if category in ( 'phone_call', 'digits' ):

                        action_dict['skype_manager_operate_phone'] = True
                        action_dict['skype_manager_phone_action'] = \
                            self.speech_to_action_map[max_key]['action']

                


                    # action_dict['gui_change_system_state'] = True
                    action_dict['gui_new_system_state'] = 'awake'

                    # action_dict['speech_recognizer_change_system_state'] = True
                    action_dict['speech_recognizer_new_system_state'] = 'awake'

                    
                    # Reset the intent vector                    
                    self.intent_vector = self.initialize_intent_vector()
                    action_dict['dialog_manager_reset_dialog_state'] = True

                else:

                    output_text = self.get_confirmation_text( max_key )
                    action_dict['gui_new_system_state'] = 'attentive'
                    # action_dict['gui_change_system_state'] = True
                    action_dict['speech_recognizer_new_system_state'] = 'attentive'
                    # action_dict['speech_recognizer_new_system_state_recognizer_change_system_state'] = True

                    # The dialog is not over
                    action_dict['dialog_manager_reset_dialog_state'] = False


                    #action_dict['output_intent_vector'] = self.intent_vector
                    output_intent_vector = self.intent_vector

                # print output_text
                action_dict['gui_answer'] = output_text
                action_dict['voice_synthesizer_answer'] = output_text

 
        return output_intent_vector, action_dict



    ##
    # Description:
    # Gets the confirmation text for the item
    def get_confirmation_text( self, max_key ):
        confirmation_string = "Do you want %s?" % self.speech_to_action_map[max_key]['confirmation_predicate'] 
        return confirmation_string


    ##
    # Description:
    # Gets the possible entries for the intent belief vector and 
    # belief-to-action matrix
    def get_intents( self ):
        speech_dict = tbh_action_map.get_speech_to_action_map()

        # print intent_vector
        information_codes = []
        system_codes = []
        phone_call_codes = []
        

        for code in speech_dict.keys():
            category = speech_dict[code]['category'] 
            if category in ( 'time', 'activities', 'weather', 'menus' ):
                information_codes.append( code )
            elif category in ( 'system', 'voice_synthesizer' ):
                system_codes.append( code )
            elif category  in ( 'phone_call', 'digits' ):
                phone_call_codes.append( code )

        possible_intents = information_codes + \
            system_codes + phone_call_codes

        return possible_intents


    ## 
    # Description:
    # A vector that describes the possible intents
    def initialize_intent_vector( self ):
   
        #for key, item in speech_dict.items():
        #    print key, item
        
        # These are dialog-relevant codes
        # Treat them as special cases
        #not_action_code = ( 22, 23, 35, 48, 49, 50, 51, 52, 53, 54, 55, \
        #                        56 )
        

        # Create a vector of intents
        #intent_vector_values = speech_dict.keys()
        #intent_vector.sort()
        #print intent_vector
        #for code in not_action_code:
        #    intent_vector_values.remove( code )

        intent_vector_values = self.get_intents()

        intent_vector_dict = {}

        number_of_intents = len( intent_vector_values )
        for item in intent_vector_values:
            intent_vector_dict[item] = log(1) - log(float(number_of_intents))    

        return intent_vector_dict


    def initialize_intent_matrix( self ):
        speech_dict = tbh_action_map.get_speech_to_action_map()
        intent_keys = speech_dict.keys()
        intent_matrix = {}
        for item in intent_keys:
            intent_matrix[item] = {}

        # Create intent matrix that maps codes to actions. This is a
        # conditional probability table with a high value along its
        # diagonals and low probabilities off diagonal
        possible_intents = self.get_intents()
            
        MATCH_VALUE = 0.95
        for i in possible_intents:
            for j in possible_intents:
                if j == i:
                    intent_matrix[i][j] = log( MATCH_VALUE )
                else:
                    intent_matrix[i][j] = \
                        log ( 1 - MATCH_VALUE ) - \
                        log( len( possible_intents ) - 1 )

        return intent_matrix


    ##
    # Description:
    # Look for keyword in the first position of the word
    def find_keyword( self, input_text, system_state ):        
        # If the system is in "attentive" mode, there is no 
        # need for keywords
        if system_state == 'attentive':
            return True
        else:
            try: 
                words = input_text.split()
                if words[0] in self.user_profile.keywords:
                    return True
                else:
                    return False
            except IndexError:
                return False
            else:
                return False

    
    
    ##
    # Description:
    # Returns meaningful suggestions to the user on the GUI
    def determine_suggestions( self ):
        return None

    ##
    # Description:
    # For a given string, find the appropriate action code
    def find_action( self, statement ):

        action_dict = self.speech_to_action_map
        candidate_action_codes = []
        for possible_action, action_info in action_dict.items():
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


#########################################################
##
# Global functions


## Description
# Generic string find function
# Looks for entire words/strings
# If the given query is found, returns true

def string_find( statement, query_string ):
    string_found = False
    temp_statement = repr( statement )
    raw_statement_string = temp_statement[1:-1]
    temp_query_string = repr( query_string )
    raw_query_string = temp_query_string[1:-1]

    if re.search(r'\b' + raw_query_string + r'\b', raw_statement_string):
	string_found = True


    return string_found







#########################################################


if __name__ == '__main__':
    x = process_nbest_list( test_mode=True )
    # dummy state_info
    state_info = { 'system_state': 'awake', 
                   'intent_vector': None
                   }
    nbest_list = [{'text':"chair what time is it"}]

    x.determine_action( nbest_list, state_info )


    nbest_list = [{'text':"chair what is today's date"}]

    x.determine_action( nbest_list, state_info )

    nbest_list = [{'text':"chair what is for lunch tomorrow"}]

    x.determine_action( nbest_list, state_info )

    nbest_list = [{'text':"chair go to sleep"}]
    x.determine_action( nbest_list, state_info )



    # print v
