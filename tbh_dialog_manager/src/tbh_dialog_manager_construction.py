## Dialog Policy

##     * runs when called, maybe threaded
##     * functions:
##           o self.reset() : clears any internal state and comes back to a default 'sane' initial state
##           o self.update_with_nbest( n_best )
##           o self.get_response( ) outputs an action that the system module can use
##           o set/get parameters for the particular mode
##                 + for example: listenting mode currently active 
##           o get_speech_to_action_map( file_name ): load the speech to action map


import sys
import csv
import re
sys.path.append( "../../tbh_api/src" )
from tbh_api import *

sys.path.append( "../../tbh_action_map/src/" )
from tbh_action_map import get_speech_to_action_map

from UserDict import UserDict

##
# Description:
# Holds information about the current dialog
class tbh_dialog_t:
    def __init__( self ):
        self.history = []
        self.initial_event
    
    def reset_dialog( self ):
        self.history = []

    def add_user_input( self, user_input ):
        self.history.append( user_input )

    def add_system_output( self, system_output ):
        self.history.append( system_output )
    
class tbh_dialog_user_input_t( UserDict ):
    def __init__( self ):
        UserDict.__init__( self )
        self['transcript'] = None
        self['code'] = None

class tbh_dialog_system_output_t( UserDict ):
    def __init__( self ):
        UserDict.__init__( self )
        self['answer'] = None
        self['suggestions'] = None
        self['skype_action'] = None

    



## 
# Description:
# Handles the dialog and how the system responds to inputs of natural
# language text
class tbh_dialog_manager:

    ##
    # Description
    # Internal state variable
    internal_state = None

    ## Description
    # List of previous states
    _previous_states = None

    ## Description
    # List of previous actions
    _previous_actions = None

    ## speech to action mapping
    # A dictionary of dictionaries 
    # { 1: { 'category': 'time', 'keyword_sets': [ 'time', 'date', 'time, date' ] }
    speech_to_action_map = None
    

    ##
    # Description
    # Initalizes dialog manager
    @tbh_api_callable
    def __init__( self ): 
        self.internal_state = None
        self._previous_states = []
        self._previous_actions = []
        self.speech_to_action_map = get_speech_to_action_map()
    
    ##
    # Description
    # Resets the internal state
    @tbh_api_callable
    def reset( self ):
        self.internal_state = None
        self._previous_states.append( self.internal_state )
        self._previous_actions.append( 'reset' )

    ##
    # Description
    # update based on nbest list
    # input: list of nbest dictionaries with the following attributes
    # [ { 'transcript': <str>, 'language_model_score': <float>, ... ]
    # Other attributes may be possible
    # The list position corresponds to the ranking of the input
    # Currently, this function just uses the expected value (top result)
    @tbh_api_callable     
    def update_nbest( self, nbest ):
        desired_action_code = self.find_action( nbest[0]['transcript'] )



    ##
    # Description
    
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


        # pick the action code for which the most keywords matches                                  # if there is a tie, there are a few tie-breaking rules:
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




#==========================================================================



if __name__ == '__main__':
    """
    file_name = sys.argv[1]
    print "Loading", file_name   
    action_list = load_action_file( file_name )
    for row in action_list:
        print row
    """
    dialog_manager = tbh_dialog_manager()

    for item in dialog_manager.speech_to_action_map.keys():
        print dialog_manager.speech_to_action_map[item]

    example_input = "chair good day"

    x = dialog_manager.find_action( "chair good day" )
    desired_action = dialog_manager.speech_to_action_map[x]['action']
    print "Action for '%s': %s, %s" % ( example_input, x, desired_action )  

    while 1:
        input_sentence = raw_input( "Type in a sentence (q to exit): " )
        if input_sentence == 'q':
            break
        else:

            action_code = dialog_manager.find_action( input_sentence )
            desired_action = dialog_manager.speech_to_action_map[action_code]['action']
            print "Action for '%s': %s, %s" % ( input_sentence, action_code, \
                                                    desired_action )  
            
