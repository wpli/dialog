#!/usr/bin/python
import numpy
import tbh_pomdp_util



class qmdp:
    def __init__( self, nrStates ):
        self.nrStates = nrStates
        self.policy = []
  
class pomdp:
    def __init__( self, nrStates, nrActions ):
        self.nrStates = nrStates
        self.nrActions = nrActions

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
            qmdp_value = numpy.dot( belief_vector, Q[:,i] )
            if i == 0:
                best_action = 0
                best_qmdp_value = qmdp_value
            elif qmdp_value > best_qmdp_value:
                best_action = i
                best_qmdp_value = qmdp_value
        
    return best_action
 
    
if __name__ == '__main__':
    #solve_qmdp( [], [], [] )
    
    #test_pomdp = pomdp( nrStates=3, nrActions=2  )

    #matlab_policy = numpy.genfromtxt( 'policy.txt', dtype=int )
    #Q = numpy.genfromtxt( 'Q.txt' )
    dialog_data = tbh_pomdp_util.get_matlab_dialog_data( 'dialog_data.mat' )
    #matlab_policy = dialog_data['policy']
    Q = dialog_data['Q']
    #print matlab_policy
    #print Q

    
    nrStates = Q.shape[0]
    nrActions = Q.shape[1]
    dialog_pomdp = pomdp( nrStates, nrActions )

    belief_vector = numpy.ones( [1, nrStates ] )
    belief_vector = belief_vector *  1/nrStates 
    #print belief_vector


    # Example only
    #belief_vector = numpy.array( [ .3, .2, .5 ] )
    #q = numpy.array( [[5, 2, 7],[ 4, 5, 6 ]] )


    # compute a policy table
    qmdp_belief_points = 10
    qmdp_belief_values = numpy.array( [] )
    policy_array = numpy.zeros( (nrStates, qmdp_belief_points), dtype=int )

    for j in range( 1, qmdp_belief_points + 1 ):
        focus_belief_value = float(j) / float(qmdp_belief_points)
        qmdp_belief_values = numpy.append( qmdp_belief_values, focus_belief_value )

    counter = 0

    # iterate over all the states


    for k in range( 0, nrStates ):


        # iterate over the different belief values we want to test        
        for belief_index, j in enumerate(qmdp_belief_values):
            belief_vector = [0] * nrStates

            for belief_vector_index, belief_vector_value in enumerate( belief_vector ):
                if belief_vector_index == k:
                    belief_vector[belief_vector_index] = j
                else:
                    belief_vector[belief_vector_index] = (float(1) - float(j)) / float( nrStates - 1 )
            # solve the QMDP for this belief
            numpy_belief_vector = numpy.array( belief_vector )
            
            policy_array[k,belief_index] = solve_qmdp( numpy_belief_vector, dialog_pomdp, Q )

    print policy_array
    #print matlab_policy


    
