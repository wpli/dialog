#!/usr/bin/python
import numpy
import scipy.io
import solve_qmdp

# return vector of new beliefs 
def belief_update( pomdp, current_belief, action, observation ):
    # Check sizes 
    if pomdp.nrStates != current_belief.shape[0]:
        raise Exception('Number of states does not match size of belief vector')

    if action >= pomdp.nrActions:
        raise Exception('Invalid action')
    
    if observation >= pomdp.nrObservations:
        raise Exception('Invalid observation')

    # Compute belief
    unnormalized_new_belief = pomdp.observation[:,action,observation] * \
        numpy.dot( pomdp.transition[:,:,action], current_belief )[0]

    new_belief = unnormalized_new_belief / numpy.linalg.norm( unnormalized_new_belief ) 

    return new_belief

def get_matlab_dialog_data( matlab_file ):
    dialog_data = scipy.io.loadmat( matlab_file )
    return dialog_data


if __name__ == '__main__':
    dialog_data = get_matlab_dialog_data( 'dialog_data.mat' )
    # pomdp is a data structure with reward, observation, transition, start_dist, \
    # nrStates, nrActions, gamma
    pomdp = dialog_data['pomdp'][0,0]
    belief = pomdp.start_dist
    #pomdp.belief

    #print pomdp.transition.shape
    new_belief = belief_update( pomdp, belief, action=5, observation=5 )
    print new_belief
    #print pomdp.observation[0][0]



      


    

    



