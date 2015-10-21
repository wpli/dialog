#!/usr/bin/python
import numpy
import scipy.io
import solve_qmdp

NO_CODE = 3
YES_CODE = 4

# return vector of new beliefs 

def check_sizes( pomdp, current_belief, action, observation ):
    # CHECK SIZES OF POMDP ELEMENTS
    if pomdp.nrStates != current_belief.shape[0]:
        raise Exception('Number of states does not match size of belief vector')
    if action >= pomdp.nrActions:
        raise Exception('Invalid action')
    
    if observation >= pomdp.nrObservations:
        raise Exception('Invalid observation')

def belief_update( pomdp, current_belief, action, observation, confidence_in_hypothesis=1, use_confidence_scores = True, high_confidence_model = None, low_confidence_model = None ):
    
    check_sizes( pomdp, current_belief, action, observation )

    prior_belief = numpy.dot( pomdp.transition[:,:,action], current_belief )

    #print "PRIOR BELIEF"
    #print prior_belief
    #print "OBSERVATION"
    #print pomdp.observation[:,action,observation]

    # Compute belief

    #print action, observation
    #print pomdp.observation[:,action,observation]
    
    log_unnormalized_new_belief = \
        numpy.log( \
        pomdp.observation[:,action,observation] ) + \
            numpy.log( prior_belief )

    new_belief = lognormalize( log_unnormalized_new_belief )

    #print new_belief
    #print "###"

    # interpolate the new_belief based on the confidence level

    if use_confidence_scores:
        if high_confidence_model == None:
            new_belief = confidence_in_hypothesis * new_belief + \
                ( 1 - confidence_in_hypothesis ) * prior_belief

        else:
            confidence_score_bin = \
                int( confidence_in_hypothesis * len( low_confidence_model[0] ) )
            if confidence_score_bin == len( low_confidence_model[0] ):
                confidence_score_bin -= 1

            low_confidence_probability = float( low_confidence_model[0][confidence_score_bin] ) / \
                float( sum( low_confidence_model[0] ) )

            confidence_vector = numpy.ones( pomdp.nrStates ) * low_confidence_probability

            yes_observation_index = 62
            no_observation_index = 63
            starting_action = 124

            high_confidence_probability = \
                float( high_confidence_model[0][confidence_score_bin] ) \
                / float( sum( high_confidence_model[0] ) )

            if observation < pomdp.nrStates:
                #print high_confidence_probability
                confidence_vector[ observation ] = high_confidence_probability

            elif observation == yes_observation_index:
                if action > pomdp.nrStates and action < starting_action:
                    confidence_vector[ action - observation ] = \
                        high_confidence_probability
                else:
                    pass


            elif observation == no_observation_index:
                if action > pomdp.nrStates and action < starting_action:
                    confidence_vector = numpy.ones( pomdp.nrStates ) \
                        * high_confidence_probability

                    confidence_vector[ action - observation + 1 ] = low_confidence_probability

                else:
                    pass

            else:
                pass
                
                
            log_unnormalized_new_belief_with_confidence = \
                log_unnormalized_new_belief + \
                numpy.log( confidence_vector )

            #print observation

            #print log_unnormalized_new_belief_with_confidence

            #print "TEST"
            new_belief = lognormalize( log_unnormalized_new_belief_with_confidence )
            
            # This is where we incorporate the beliefs


    return new_belief



def lognormalize(x):
    a = numpy.logaddexp.reduce(x)
    return numpy.exp(x - a)

def get_matlab_dialog_data( matlab_file ):
    dialog_data = scipy.io.loadmat( matlab_file, struct_as_record = False )
    return dialog_data

def get_pomdp( dialog_data ):
    pomdp = dialog_data['pomdp'][0,0]
    pomdp.belief = pomdp.start_dist[ :, 0 ]
    return pomdp

def get_Q( dialog_data ):
    return dialog_data['Q']

def example_solve_qmdp( qmdp_belief_point, pomdp, Q, ):
    # iterate over states
    # qmdp_belief_points is the number of different beliefs we will sample to determine the optimal policy
    
    for k in range(0, pomdp.nrStates):
        for j in range( 0, qmdp_belief_points ):
            focus_belief_value = j / qmdp_belief_points


# This solves the qmdp
def solve_qmdp( belief_vector, pomdp, Q ):
    # belief_vector is an np_array
    # Q is a two dimensional vector with nrActions rows and nrStates columns
    #print numpy.shape( belief_vector )
    if numpy.shape( belief_vector )[0] != pomdp.nrStates:
        raise Exception( "Belief vector must have same length as pomdp.nrStates" )    
    else:
        for i in range( 0, pomdp.nrActions ):
            #print Q
            #print belief_vector.shape, Q[:,i].shape

            qmdp_value = numpy.dot( belief_vector, Q[:,i] )
            if i == 0:
                best_action = 0
                best_qmdp_value = qmdp_value
            elif qmdp_value > best_qmdp_value:
                best_action = i
                best_qmdp_value = qmdp_value
        
    return best_action
 
def reset_belief( pomdp ):
    return pomdp.start_dist[ :, 0 ]

if __name__ == '__main__':

    # UNIT TESTS
    dialog_data = get_matlab_dialog_data( 'dialog_data.mat' )
    # pomdp is a data structure with reward, observation, transition, start_dist, \
    # nrStates, nrActions, gamma
    pomdp = get_pomdp( dialog_data )
    #print pomdp.observation[:,0,5]
    
    Q = get_Q( dialog_data )
    belief = pomdp.start_dist
    #pomdp.belief

    #print pomdp.transition.shape
    new_belief = belief_update( pomdp, belief, action=124, observation=0 )
    #print new_belief.shape
    print new_belief
    #print pomdp.observation[0][0]
    """
    for a in range(pomdp.observation.shape[0]):
        for b in range(pomdp.observation.shape[1]):
            for c in range(pomdp.observation.shape[2]):
                if pomdp.observation[a,b,c] < 0:
                    print pomdp.observation[a,b,c],a,b,c

    """



      


    

    



