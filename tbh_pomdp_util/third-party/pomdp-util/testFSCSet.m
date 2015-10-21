function [ history weight_set ] = testFSCSet( sim_pomdp , test_set , test_param_set , weight_set )
% function history = testPOMDP( sim_pomdp , test_set , test_param_set , weight_set )
% note: if given many fscs, then just picks randomly

% initialization -- in general
reward = 0; 
iter_count = 0; 
if ( ( nargin == 3 ) || isempty( weight_set ) )
    weight_set = ones( 1 , numel( test_set ) );
end
weight_set = weight_set / sum( weight_set );
state = sample_multinomial( sim_pomdp.start_dist , 1 );

% initialization -- for the fscs
current_node_set = ones( numel( test_set ) );

% loop until maxed or done
keep_running = true;
while( keep_running )

    % get an action 
    if iscell( test_set )
        fsc_index = sample_multinomial( weight_set );
        action = sample_multinomial( test_set{ fsc_index }.policy( ...
            current_node_set( fsc_index ) , : ) );
    else
        action = ceil( rand * sim_pomdp.nrActions );
    end
    
    % store your action, q variance
    history(iter_count+1, 2) = action;
    
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
    history(iter_count+1, 5) = 0;
    
    % update controller nodes
    if iscell( test_set )
        for fsc_index = 1:numel( test_set )
            if length( size( test_set{ fsc_index }.transition ) ) == 3            
                current_node_set( fsc_index ) = sample_multinomial( ...
                    test_set{ fsc_index }.transition( : , ...
                    current_node_set( fsc_index ) , obs ) );
            else
                current_node_set( fsc_index ) = sample_multinomial( ...
                    test_set{ fsc_index }.transition( : , ...
                    current_node_set( fsc_index ) , obs , action ) );
            end
        end
    end
    
    % update the iters and stop if max reward
    iter_count = iter_count + 1;
    keep_running = ( iter_count < test_param_set.max_iter_count );
    if new_reward == sim_pomdp.maxReward
        keep_running = false;
    end
end

% reset for next runs
current_node_set = ones( numel( test_set ) );



