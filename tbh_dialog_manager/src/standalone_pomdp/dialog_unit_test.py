
DIALOG_DATA_PATH = 'dialog_data.mat' 

# k_high = CORRECT_MODEL_PARAMETER
CORRECT_MODEL_PARAMETER = 1
# e^{(k_{high}(x-1)} 

# k_low = INCORRECT_MODEL_PARAMETER
INCORRECT_MODEL_PARAMETER = 1
# e^{-k_{low}x}

# for the feature set
import sys

import numpy
# action code management

#import tbh_pomdp_manager_experiments as tbh_pomdp_manager

# These imports are CUSTOM for your DM
import re
from math import log

# Import the POMDP utilities
import tbh_pomdp_util
import time

class tbh_dialog_manager_t:
    ##
    # Description
    # Initalizes dialog manager
    def __init__( self, dialog_data_path = DIALOG_DATA_PATH, \
                      high_confidence_histogram = None, \
                      low_confidence_histogram = None ): 

        # --- CUSTOM --- #
        # for confidence modeling
        # self.high_confidence_histogram = high_confidence_histogram
        # self.low_confidence_histogram = low_confidence_histogram

        # This is for the POMDP dialog manager
        dialog_data = tbh_pomdp_util.get_matlab_dialog_data( dialog_data_path )
        self.pomdp = tbh_pomdp_util.get_pomdp( dialog_data )       
        self.number_of_states = self.pomdp.nrStates[0][0]

        # special observation codes
        self.yes_code = self.number_of_states
        self.no_code = self.number_of_states + 1
        self.noise_code = self.number_of_states + 2

        # special action codes
        self.starting_action = self.number_of_states * 2 + 1
        self.Q = tbh_pomdp_util.get_Q( dialog_data )

        # start a new dialog
        self.start_new_dialog()

    def start_new_dialog( self ):
        self.reset_belief()
        self.current_action = self.starting_action
    
    def reset_belief( self ):
        self.current_belief = self.pomdp.start_dist[ :, 0 ]
        
    def update_belief( self, observation, confidence_score ):
        action = self.current_action
        prior_belief = \
            numpy.dot( self.pomdp.transition[:,:,action], self.current_belief )

        log_unnormalized_new_belief = \
            numpy.log( \
            self.pomdp.observation[:,action,observation] ) + \
            numpy.log( prior_belief )

        confidence_vector = numpy.ones( self.number_of_states ) * \
            self.incorrect_confidence_model( confidence_score )
        
        yes_observation_index = self.number_of_states
        no_observation_index = self.number_of_states + 1
        noise_observation_index = self.number_of_states + 2

        if observation < self.number_of_states:
            confidence_vector[ observation ] = self.correct_confidence_model( confidence_score )
        
        elif observation == yes_observation_index:
            if action > self.number_of_states and action < self.starting_action:
                confidence_vector[ action - observation ] = \
                    self.correct_confidence_model( confidence_score )
            else:
                pass

        elif observation == no_observation_index:
            if action > self.number_of_states and action < self.starting_action:
                confidence_vector = numpy.ones( self.number_of_states ) \
                    * self.correct_confidence_model( confidence_score )
                confidence_vector[ action - observation + 1 ] = self.incorrect_confidence_model( confidence_score )
            else:
                pass

        
        new_belief = lognormalize( log_unnormalized_new_belief + numpy.log( confidence_vector ) )
        self.current_belief = new_belief

    def choose_action( self ):
        # use QMDP to find the optimal action
        qmdp_best_action = self.solve_qmdp( self.current_belief, self.pomdp, self.Q )
        self.current_action = qmdp_best_action
        return qmdp_best_action


    def incorrect_confidence_model( self, confidence_score ):
        return numpy.exp( -1 * INCORRECT_MODEL_PARAMETER * confidence_score )

    def correct_confidence_model( self, confidence_score ):
        return numpy.exp( CORRECT_MODEL_PARAMETER * ( confidence_score - 1 ) )

    # This solves the qmdp
    def solve_qmdp( self, belief_vector, pomdp, Q ):
        # belief_vector is an np_array
        # Q is a two dimensional vector with nrActions rows and nrStates columns
        #print numpy.shape( belief_vector )
        if numpy.shape( belief_vector )[0] != pomdp.nrStates:
            raise Exception( "Belief vector must have same length as pomdp.nrStates" )    
        else:
            for i in range( 0, pomdp.nrActions ):
                qmdp_value = numpy.dot( belief_vector, Q[:,i] )
                if i == 0:
                    best_action = 0
                    best_qmdp_value = qmdp_value
                elif qmdp_value > best_qmdp_value:
                    best_action = i
                    best_qmdp_value = qmdp_value

        return best_action






        
        






# ------------------- GLOBAL UTILS --------------------- #
## Description
# Generic string find function Looks for entire words/strings If the
# given query is found, returns true
def lognormalize(x):
    a = numpy.logaddexp.reduce(x)
    return numpy.exp(x - a)


def string_find( statement, query_string ):
    string_found = False
    temp_statement = repr( statement )
    raw_statement_string = temp_statement[1:-1]
    temp_query_string = repr( query_string )
    raw_query_string = temp_query_string[1:-1]
    if re.search(r'\b' + raw_query_string + r'\b', raw_statement_string):
	string_found = True
    return string_found

def get_utterance_to_observation_map( number_of_states ):
    utterance_to_observation_map = {}
    utterance_to_observation_map['y'] = number_of_states
    utterance_to_observation_map['n'] = number_of_states + 1
    utterance_to_observation_map['x'] = number_of_states + 2
    for j in range( number_of_states ):
        utterance_to_observation_map[ str( j ) ] = j
    return utterance_to_observation_map

def parse_utterance( utterance, utterance_to_observation_map ):
    if utterance in utterance_to_observation_map.keys():
        return utterance_to_observation_map[ utterance ] 
    else:
        # return code corresponding to noise
        return utterance_to_observation_map['x']

def get_observation_to_description_map( number_of_states ):
    observation_to_description_map = {}
    for i in range( number_of_states ):
        observation_to_description_map[i] = str( i )
        
    observation_to_description_map[number_of_states] = "YES"
    observation_to_description_map[number_of_states+1] = "NO"
    observation_to_description_map[number_of_states+2] = "NOISE"
    return observation_to_description_map

def get_action_to_description_map( number_of_states ):
    action_to_description_map = {}
    for i in range( number_of_states ):
        action_to_description_map[i] = "DO %s" % i
    
    for i in range( number_of_states, 2*number_of_states ):
        action_to_description_map[i] = "CONFIRM %s" % str( i - number_of_states )
    
    action_to_description_map[ 2*number_of_states ] = "ASK USER TO REPEAT"
    action_to_description_map[ 2*number_of_states + 1 ] = "GREET USER"
    return action_to_description_map

if __name__ == '__main__':
    dialog_manager = tbh_dialog_manager_t()
                                             
    print "Welcome to the dialog manager!\n"
    number_of_states = dialog_manager.number_of_states
    utterance_to_observation_map = get_utterance_to_observation_map( number_of_states )
    observation_to_description_map = get_observation_to_description_map( number_of_states )

    action_to_description_map = get_action_to_description_map( number_of_states )

    while 1:
        print "-----------"
        print "NEW DIALOG"
        instructions = 'There are %s goals, numbered 0 to %s. This demo currently allows you to type "utterances" corresponding to one of these numbers.' % ( number_of_states, number_of_states - 1 )
        print instructions
        
        action = dialog_manager.starting_action

        print "\n\tSystem prompt: %s" % action_to_description_map[action]
 
        while 1:

            # text input from user

            while 1:
                utterance = raw_input( "\nWhat would you like to say? Please specify a goal number (0 to %s), yes (y), no (n), or noise (x): " % str( number_of_states - 1 ) )
                if utterance in [ str(i) for i in range( number_of_states ) ] + ['y', 'n', 'x']:
                    break
                else:
                    print "Invalid input. Try again."

            while 1:
                confidence_score_string = raw_input( "Please specify a confidence score between 0 and 1: " )
                try:
                    confidence_score = float( confidence_score_string )
                    if confidence_score >= 0 and confidence_score <= 1:
                        break
                    else:
                        print "Please enter a number between 0 and 1. Try again."
                except ValueError:
                    print "Please enter a number between 0 and 1. Try again."
            



            print '\n\tYou said "%s" with a confidence score of %s' %( utterance, confidence_score )

            # determine which observation
            observation = parse_utterance( utterance, utterance_to_observation_map )
            print "\tThe dialog manager interprets this as mapping to observation %s with confidence %s" % \
                ( observation_to_description_map[observation], confidence_score )

            # update the belief
            print "\tNow updating the belief distribution..."
            dialog_manager.update_belief( observation, confidence_score )
            print "\t\tTop five states with the highest probabilities in the belief distribution:"
            belief_argsort = numpy.argsort( dialog_manager.current_belief )
            for i in range( 5 ):
                state_index = belief_argsort[-1-i] 
                print "\t\tstate %s: p = %.4f" % ( state_index, dialog_manager.current_belief[state_index] )

            # choose an action based on the belief distribution
            action = dialog_manager.choose_action()
            print action
            print "\tSystem prompt: %s" % action_to_description_map[action]
            
            if action < number_of_states:
                print "\nEnd of dialog. Starting new dialog..."
                dialog_manager.start_new_dialog()
                break
