function [ transition ] = dialog_transition_function( pomdp )
    % In general, dialog does not change states as a function of the action
    % basically, every square matrix is identity
% In this model, the transition function is invariant to the number
% of actions that exist
% This is invariant over the three models that we are using
% T(s',s,a)   
    for i=1:pomdp.nrActions
        transition( : , : , i ) = eye( pomdp.nrStates );
    end
    
    return

    



end

