
# This deals with the mechanics of the POMDP
import sys
sys.path.append( '../../tbh_pomdp_util/src/' )
import tbh_pomdp_util

# POMDP dialog utilities
import tbh_pomdp_action_code_manager # for POMDP actions
import tbh_action_code_manager # for POMDP observations


# numpy for computing confidence scores
import numpy

LOGISTIC_PARAMETERS = [ -0.0876,-1.0227 ]

def process_result_reset( pomdp ):
    pomdp_dict = unit_test_reset_belief( pomdp )
    return pomdp_dict

def process_result( pomdp, observation, machine_action, Q, param_dict, use_confidence_scores=False, skype_contacts_dict=None ):
    '''
    # Take the action_code and translate it into an observation
    ( observation_code, machine_action_code ) = \
        translate_into_pomdp_codes( observation, machine_action )

        # Run the belief update
    '''
    # Determine the desired action from the policy (perhaps solve the QMDP \
    # for this particular belief)

    # Return data structure   

    # Sandbox: The POMDP does not do anything
    #( new_belief, action_code ) = sandbox_result( belief, observation )
    
    # More sophisticated result


    action_code_list = tbh_pomdp_action_code_manager.get_pomdp_action_code_number_list()
    observation_list = tbh_action_code_manager.get_action_code_number_list()


    if machine_action is None:
        machine_action = [ 'null', ['yes_record']]

    machine_action_number = tbh_pomdp_action_code_manager.get_number_action_code( \
        action_code_list, machine_action )

    '''
    # Confidence scores using n-best lists
    if use_confidence_scores:

        # simplified confidence scoring method
        # 0.5 for top result
        # 0.2 for second result
        # 0.1 for third result

        observation_number_list = []
        probability_list = [ 0.55, 0.25, 0.1 ]

        for i in range(0,3):
            observation_number = tbh_action_code_manager.get_number_action_code( \
                observation_list, observation[i] )

            observation_number_list.append( { observation_number : \
                                                  probability_list[i] } )


        # We now have the machine_action_numbeor, the observation_number, and the current belief
        # We can do a belief update!

        

        belief_for_policy = tbh_pomdp_util.belief_update_with_confidence_scores( pomdp, pomdp.belief, \
                                                       machine_action_number, \
                                                       observation_number_list )

        #print pomdp.belief.shape
        #print belief_for_policy.shape

        pomdp_dict = pomdp_choose_action( pomdp, Q, \
                                              belief_for_policy, action_code_list )

    '''                                              

    if use_confidence_scores:

        # determine the observation number in question
        observation_number = tbh_action_code_manager.get_number_action_code( \
            observation_list, observation )

        # determine the confidence value
        confidence_in_hypothesis = determine_confidence_in_hypothesis( \
            param_dict['adaboost_score'], LOGISTIC_PARAMETERS )

        # using the confidence in the hypothesis

        # We now have the machine_action_number, 
        # the observation_number, and the current belief
        # We can do a belief update!
        belief_for_policy = \
            tbh_pomdp_util.belief_update( \
            pomdp, pomdp.belief, \
                machine_action_number, \
                observation_number, \
                confidence_in_hypothesis )



        #print pomdp.belief.shape
        #print belief_for_policy.shape

        pomdp_dict = pomdp_choose_action( pomdp, Q, \
                                              belief_for_policy, action_code_list )

        pomdp_dict['confidence_in_hypothesis'] = confidence_in_hypothesis

    else:
        observation_number = tbh_action_code_manager.get_number_action_code( \
            observation_list, observation )

        # We now have the machine_action_number, the observation_number
        # and the current belief
        # We can do a belief update!
        belief_for_policy = tbh_pomdp_util.belief_update( pomdp, pomdp.belief, \
                                                       machine_action_number, \
                                                       observation_number )

        pomdp_dict = pomdp_choose_action( pomdp, Q, \
                                              belief_for_policy, action_code_list )

    return pomdp_dict


def determine_confidence_in_hypothesis( adaboost_score, logistic_parameters ):
    constant = float( logistic_parameters[0] )
    coefficient = float( logistic_parameters[1] )

    confidence_in_hypothesis = float(1) / \
        float( 1 + numpy.exp(constant + \
                                 coefficient * float( adaboost_score ) ) )

    #print "adaboost: %s; confidence: %s" %( adaboost_score, confidence_in_hypothesis )
    
    return confidence_in_hypothesis


"""
def process_result_confidence( pomdp, recent_observation_list, machine_action, Q, use_confidence_scores=False, skype_contacts_dict=None ):

    action_code_list = tbh_pomdp_action_code_manager.get_pomdp_action_code_number_list()
    if machine_action is None:
        machine_action = [ 'null', ['yes_record']]
    machine_action_number = tbh_pomdp_action_code_manager.get_number_action_code( \
        action_code_list, machine_action )


    observation_list = tbh_action_code_manager.get_action_code_number_list()

    #observation = recent_observation_list[0]
    observation_nbest = []
    for observation in recent_observation_list:
        try:
            observation_number = tbh_action_code_manager.get_number_action_code( \
                observation_list, observation ) 
        except:
            pass
        observation_nbest.append( observation_number )


    # Compute a belief, based on voting
    
    observation_number = observation_nbest[0]
 
    #print "ACTION/OBSERVATION", machine_action_number, observation_number
    # We now have the machine_action_number, the observation_number, and the current belief
    # We can do a belief update!
    belief_for_policy = tbh_pomdp_util.belief_update( pomdp, pomdp.belief, \
                                                   machine_action_number, \
                                                   observation_number )
    #print pomdp.belief.shape
    #print belief_for_policy.shape


    pomdp_dict = pomdp_choose_action( pomdp, Q, belief_for_policy, action_code_list )


    return pomdp_dict
"""



def pomdp_choose_action( pomdp, Q, belief_for_policy, action_code_list ):
  
    new_machine_action_number = tbh_pomdp_util.solve_qmdp( belief_for_policy, pomdp, Q ) 
    new_machine_action = action_code_list[new_machine_action_number]
    
    #print "ACTION NO., ACTION", new_machine_action_number, new_machine_action
 
    # Determine if we need to reset the policy
    reset_belief = determine_reset_belief( new_machine_action )

    if reset_belief:        
        final_belief = tbh_pomdp_util.reset_belief( pomdp )
    else:
        final_belief = belief_for_policy


    pomdp_dict = { 'belief_for_policy': belief_for_policy, 
                   'final_belief': final_belief,                   
                   'new_machine_action': new_machine_action,
                   'reset_belief': reset_belief }

    return pomdp_dict

def unit_test_reset_belief( pomdp ):
  
    final_belief = tbh_pomdp_util.reset_belief( pomdp )

    pomdp_dict = { 'belief_for_policy': final_belief, 
                   'final_belief': final_belief,                   
                   'new_machine_action': None,
                   'reset_belief': True }

    return pomdp_dict



def determine_reset_belief( new_machine_action ):
    if new_machine_action[1][0] in \
            ( 'yes_record', 'no_record', 'request_keyword', 'request_confirmation' ):
        return False
    else:
        return True
                       
def sandbox_result( belief, observation ):

    # Sandbox example: the observation is simply the action, \
    #    and the belief vector is unchanged
    return ( belief, observation )
    
def translate_into_pomdp_codes( observation, machine_action ):
    observation_code = None
    machine_action_code = None
    return ( observation_code, machine_action_code )

import tbh_answer_text_manager

def process_code( action_code, skype_contacts_dict=None ):
    action_dict = {}
    base_code = action_code[0]
    parameter = action_code[1][0]
    parameter_list = action_code[1]

    # Set the action code
    action_dict[ 'dialog_manager_action_code' ] = action_code

    # Set the other values to their defaults
    action_dict[ 'speech_recognizer_grammar' ] = None
    action_dict[ 'speech_recognizer_recompute_nbest' ] = False
    action_dict[ 'audio_listener_power_threshold' ] = None
    action_dict[ 'audio_listener_holdover_threshold' ] = None
    action_dict[ 'audio_listener_minspeech_threshold' ] = None
    action_dict[ 'audio_listener_prespeech_threshold' ] = None
    action_dict[ 'gui_suggestions' ] = None
    action_dict[ 'gui_answer_text' ] = None 
    action_dict[ 'gui_voice_synthesizer_on' ] = False
    action_dict[ 'gui_state' ] = None
    action_dict[ 'data_storage_reset_dialog' ] = False
    action_dict[ 'skype_manager_phone_action' ] = None
    action_dict[ 'data_storage_store_audio_file' ] = False

    # Long set of cases to fill in stuff that should be changed from
    # the default value (including how to fill in the text).  
    # if the action code null, something probably happening, store data
    if base_code == 'null':
        if parameter == 'yes_record':
            action_dict['data_storage_store_audio_file'] = True

    # for system stuff re keywords
    elif base_code == 'system' and parameter == 'request_keyword':
        action_dict['gui_answer_text'] = \
                    "Please say a keyword before your command."
        action_dict['data_storage_reset_dialog'] = False

    # for other system stuff ( wake up/sleep )
    elif base_code == 'system':
        action_dict['gui_answer_text'] = tbh_answer_text_manager.get_answer_text( action_code )
        if parameter == 'wake_up':
            action_dict['data_storage_store_audio_file'] = True
            action_dict['data_storage_reset_dialog'] = True
            action_dict['gui_state'] = 'awake'
            action_dict['data_storage_store_audio_file'] = True
        elif parameter == 'go_to_sleep':
            action_dict['gui_state'] = 'sleeping'
            action_dict['data_storage_store_audio_file'] = True
            action_dict['data_storage_reset_dialog'] = True

        elif parameter == 'request_confirmation':
            action_dict['data_storage_store_audio_file'] = True


            if parameter_list[1] == 'hang_up':
                action_dict['gui_answer_text'] = "Do you want to hang up? (yes/no)"
                action_dict['data_storage_reset_dialog'] = False

            elif parameter_list[1] == 'call_contact':
                action_dict['gui_answer_text'] = "Do you want to call " + \
                    skype_contacts_dict[int(parameter_list[2])]['spoken_name'].title() + \
                    "? (yes/no)"
                action_dict['data_storage_reset_dialog'] = False

            # Set GUI to attentive mode
            action_dict['gui_state'] = 'attentive'
            action_dict['speech_recognizer_grammar'] = 'full'





    # for providing information
    elif base_code in ( 'time', 'activities', 'menus', \
                                 'breakfast', 'lunch', 'dinner', 'weather' ):
        action_dict['data_storage_store_audio_file'] = True
        action_dict['gui_answer_text'] = tbh_answer_text_manager.get_answer_text( action_code )
        action_dict['data_storage_reset_dialog'] = True

        action_dict['gui_state'] = 'awake'
        action_dict['data_storage_store_audio_file'] = True
   
    # for making calls
    elif base_code in ( 'phone', 'voice_dial' 'digits', 'call_contact' ):
        action_dict['gui_answer_text'] = tbh_answer_text_manager.get_phone_call_text( action_code, skype_contacts_dict )
        action_dict['data_storage_store_audio_file'] = True

        if base_code in ( 'voice_dial', 'digits' ):
            action_dict['speech_recognizer_grammar'] = 'skype'
        elif parameter == 'show_contacts':
            action_dict['speech_recognizer_grammar'] = 'call_contact'
            action_dict['data_storage_store_audio_file'] = True
            action_dict['data_storage_reset_dialog'] = True
        elif parameter == 'hang_up':
            action_dict['speech_recognizer_grammar'] = 'full'
            action_dict['data_storage_store_audio_file'] = True
            action_dict['data_storage_reset_dialog'] = True
        elif parameter == 'cancel':
            action_dict['speech_recognizer_grammar'] = 'full'
            action_dict['data_storage_store_audio_file'] = True
            action_dict['data_storage_reset_dialog'] = True
        elif parameter == 'make_phone_call':
            action_dict['speech_recognizer_grammar'] = 'call_contact'
            action_dict['data_storage_store_audio_file'] = True
            action_dict['data_storage_reset_dialog'] = False
        elif parameter == 'hold_call':
            action_dict['data_storage_store_audio_file'] = True
            action_dict['data_storage_reset_dialog'] = True
        elif parameter == 'resume_call':
            action_dict['data_storage_store_audio_file'] = True
            action_dict['data_storage_reset_dialog'] = True         
        elif parameter == 'next_page':
            action_dict['data_storage_store_audio_file'] = True
            action_dict['data_storage_reset_dialog'] = False
        elif parameter == 'fullscreen_video':
            action_dict['data_storage_store_audio_file'] = True
            action_dict['data_storage_reset_dialog'] = True        
        elif parameter == 'unfullscreen_video':
            action_dict['data_storage_store_audio_file'] = True
            action_dict['data_storage_reset_dialog'] = True
        else:
            action_dict['speech_recognizer_grammar'] = None
            action_dict['data_storage_reset_dialog'] = True


        # only certain functions work write now
        if base_code == 'phone':
            if parameter in ( 'hold_call', 'resume_call', 'hang_up', 'make_phone_call', 'show_phone_list', 'next_page', 'fullscreen_video', 'unfullscreen_video'  ):
                action_dict['skype_manager_phone_action'] = action_code
                #action_dict['data_storage_store_audio_file'] = True
                #action_dict['data_storage_reset_dialog'] = True



                

        # Call contact
        if base_code == 'call_contact': 
            action_dict['data_storage_store_audio_file'] = True
            action_dict['data_storage_reset_dialog'] = True


            action_dict['gui_answer_text'] = \
                tbh_answer_text_manager.get_call_contact_text( \
                action_code, skype_contacts_dict )
            if parameter != 'unknown':
                action_dict['skype_manager_phone_action'] = action_code
            else:
                pass

            action_dict['speech_recognizer_grammar'] = 'full'



    # return the action dictionary    

    return action_dict
