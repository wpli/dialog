# This module fills in the remainder of the action dictionary given
# the action code.  Note: this module should be COMMON to all dialog
# managers for a particular application (i.e., TBH).

import tbh_answer_text_manager_pomdp as tbh_answer_text_manager

def process_code( action_code, skype_contacts_dict=None ):
    print action_code
    action_dict = {}
    base_code = action_code[0]
    parameter = action_code[1][0]

    print "ACTION", base_code, parameter

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
    action_dict[ 'environmental_control_action' ] = None



    action_dict[ 'data_storage_store_audio_file' ] = False

    # Long set of cases to fill in stuff that should be changed from
    # the default value (including how to fill in the text).  
    # if the action code null, something probably happening, store data
    if base_code == 'null':
        if parameter == 'yes_record':
            action_dict['data_storage_store_audio_file'] = True
        action_dict['gui_answer_text'] = tbh_answer_text_manager.get_answer_text( action_code )



    # for system stuff re keywords
    elif base_code == 'system' and parameter == 'request_keyword':
        action_dict['gui_answer_text'] \
            = tbh_answer_text_manager.get_answer_text( action_code )
        action_dict['data_storage_reset_dialog'] = False




    # for other system stuff ( wake up/sleep )
    elif base_code == 'system':
        action_dict['gui_answer_text'] \
            = tbh_answer_text_manager.get_answer_text( action_code )
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




    elif base_code == 'environmental_control':
        action_dict['environmental_control_action'] = action_code



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
