function ll_set = check_action_agreement( action_set , obs_set , test_pomdp , sol )
% function ll = check_action_agreement( action_set , obs_set , test_pomdp , sol )
% counts the number of actions that agree with the optimal action in a set
% of histories
beta = 1;

% loop through histories
ll_set = zeros( 1 , numel( action_set ) );
for rep = 1:numel( action_set )
    
    % initialize stuffs
    action_history = action_set{ rep };
    obs_history = obs_set{ rep };
    bel = test_pomdp.start';
    ll = 0;
    for iter = 1:length( action_history )
        action = action_history( iter );
        a = getAction( bel' , sol.Vtable );
        ll = ll + beta * ( a == action );
        
        % update the belief with the action and observation
        obs = obs_history( iter );
        bel = updateBelief( test_pomdp , bel, action, obs );        
    end
    ll_set( rep ) = ll;
end

