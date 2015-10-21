import tbh_dialog_manager

import sys
sys.path.append( '../../tbh_top_level/src/' )
import tbh_user_profile


if __name__ == '__main__':
    user_profile = tbh_user_profile.tbh_user_profile_t( 0 )
    feature_type_list = [ 'tbh_keyword' , 'tbh_first_word' , \
                              'tbh_keyword_sequence', 'score_statistic' ]
    


    dialog_manager = tbh_dialog_manager.tbh_dialog_manager_t( user_profile, \
                                                                  feature_type_list )


    while 1:
        input_sentence = raw_input( "Type in a string " + \
                           "(lowercase, no commas or periods, " + \
                           "compose words if necessary, q to exit): " )

        if input_sentence == 'q':
            break
        else:
            # Turn into artificial param_dict with n-best list
            param_dict = {}       
            # Create an artificial nbest list
            nbest_list = []
            for index in range(0,10):
                nbest_list.append( { 'text': input_sentence, 'score': 0 } )
            param_dict['nbest_list'] = nbest_list

            dialog_manager.process_nbest_handler( param_dict )

            print dialog_manager.action_dict[ 'action_code' ]
            print dialog_manager.action_dict[ 'gui_answer_text' ]



            
