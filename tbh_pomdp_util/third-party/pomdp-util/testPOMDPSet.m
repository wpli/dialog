function [ history test_param_set weight_set ] = testPOMDPSet( sim_pomdp , ...
    test_set , test_param_set , weight_set )
% function [ history test_param_set weight_set ] = testPOMDPSet( sim_pomdp , ...
%    test_set , test_param_set , weight_set )


% initialization -- in general
reward = 0; 
iter_count = 0; 
if ( ( nargin == 4 ) || isempty( weight_set ) )
    weight_set = ones( 1 , numel( test_set ) );
end
weight_set = weight_set / sum( weight_set );
state = sample_multinomial( sim_pomdp.start_dist , 1 );

% loop until maxed or done
keep_running = true;
while( keep_running )

    % get an action
    [ action q_var test_param_set was_greedy ] = getActionSet( test_set , weight_set , test_param_set , sim_pomdp.nrActions );

    % store your action, q variance
    history(iter_count+1, 2) = action;
    history(iter_count+1, 5) = q_var; 
    history(iter_count+1, 6) = was_greedy;
    
    % sample a transition and update reward
    new_reward = sim_pomdp.reward( state, action );
    reward = reward + new_reward;
    if iscell( sim_pomdp.transition )
        state = sample_multinomial( sim_pomdp.transition{ action }( :, state ), 1 );
    else
        state = sample_multinomial( sim_pomdp.transition(:, state, action ), 1 );
    end
    
    % sample an observation from the current state
    if iscell( sim_pomdp.observation )
        obs = sample_multinomial( sim_pomdp.observation{ action }( state , :), 1 );
    else
        obs = sample_multinomial( sim_pomdp.observation( state, action, :), 1 );
    end
    
    % store the reward, state, and obs you received out
    history(iter_count+1, 4) = state;
    history(iter_count+1, 1) = obs;   
    history(iter_count+1, 3) = new_reward;

    % update belief over pomdps
    if iscell( test_set )
        for i = 1:numel( test_set )
            p_obs( i ) = test_set{ i }.bel' * test_set{ i }.pomdp.observation( : , action , obs );
        end
        
        % finale! hack!
        if sum( p_obs ) > eps
            weight_set = weight_set .* p_obs;
            weight_set = weight_set / sum( weight_set );
        end
    end
    
    % update belief over states
    test_set = updateBeliefSet( test_set , action , obs );
    
    % update the iters, reset if we've reached the max reward
    iter_count = iter_count + 1;
    keep_running = ( iter_count < test_param_set.max_iter_count );
    if new_reward == sim_pomdp.maxReward
        state = sample_multinomial( sim_pomdp.start_dist , 1 );
        keep_running = false;
    end   
end

% reset things for the next run
if iscell( test_set )
    for i = 1:numel( test_set )
        test_set{ i }.bel = test_set{ i }.pomdp.start';
    end
end



