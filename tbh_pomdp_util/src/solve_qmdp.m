function [ qmdp ] = solve_qmdp( qmdp_belief_points, pomdp, Q )
% iterate over the states
% qmdp_belief_points is the number of different beliefs we will
% sample to determine the optimal policy




        for k=1:pomdp.nrStates
            
            % j  is a counter to iterate over different
            % equally spaced beliefs
            
            for j=1:qmdp_belief_points
                focus_belief_value = j / qmdp_belief_points;
                
                % a vector to store the different sampled belief values
                qmdp.belief_states(j) = focus_belief_value;
                
                other_belief_value = ( 1 - focus_belief_value ) / (pomdp.nrStates-1); 
                belief_distribution = ones( 1 , pomdp.nrStates ) * other_belief_value;
                belief_distribution( k ) = focus_belief_value;
                % determine the best action to take
                for i=1:pomdp.nrActions
                    qmdp_value = sum( dot( belief_distribution, Q( :, i ) ) );
                    if i == 1
                        best_action = 1;
                        best_qmdp_value = qmdp_value;
                    elseif qmdp_value > best_qmdp_value
                        best_action = i;
                        best_qmdp_value = qmdp_value;
                    end
                    
                    qmdp.policy( k, j ) = best_action;
                    
                end
               
                
                %qmdp_policy_table( k, j ) = [ focus_belief_value best_action ];
                
                
            end


            
            
        end
         
    

               
    
    return      
        
end

