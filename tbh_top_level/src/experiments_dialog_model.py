states_text_file = \
    "../../dialog_system_tools/bin/20120118/decision_process_files/states.txt"
actions_text_file = "../../dialog_system_tools/bin/20120118/decision_process_files/actions.txt"
observations_text_file = \
    "../../dialog_system_tools/bin/20120118/decision_process_files/observations.txt"

import sys
sys.path.append( '../../dialog_system_tools/src/' )

import analysis_tools


import os
import subprocess

import scipy.io

if __name__ == '__main__':
    reward_array = [ 10, 100, 10, 15, 2, 11 ]

    ( state_list, action_list, observation_list ) = \
    analysis_tools.build_states_actions_observations_lists( \
    states_text_file, actions_text_file, observations_text_file )

    terminal_reward_value = reward_array[0]
    incorrect_reward_value = reward_array[1]
    ask_initial_question_cost = reward_array[2]
    terminate_dialog_cost = reward_array[3]
    confirm_correct_cost = reward_array[4]
    confirm_incorrect_cost = reward_array[5]

    action_cost_dict = analysis_tools.get_action_cost_dict_parameterized( \
    action_list, incorrect_reward_value, \
        ask_initial_question_cost, \
        confirm_incorrect_cost  )

    reward_function = analysis_tools.get_reward_function_parameterized( \
        state_list, action_list, action_cost_dict, terminal_reward_value, \
            confirm_correct_cost )

    scipy.io.savemat( 'reward_function.mat', \
                          {'reward_function': reward_function } )

    os.system( 'matlab -nodisplay -r "create_dialog_pomdp_command_line"' )


