function [ action qvar was_greedy ] = getMDPAction( test_set , weight_set , param_set , action_count )
% function action = getMDPAction( test_set , weight_set , param_set , action_count ) 
weight_set = weight_set / sum( weight_set );
qvar = NaN; was_greedy = NaN; action = NaN; greedy_action = NaN;

% check if test set has samples in it
if ~iscell( test_set )
    action = ceil( rand * action_count );
else
     
    % log variance in Q values, compute the greedy action for comparison
    for m = 1:numel( test_set )
        Q( m , : ) = test_set{ m }.Q( test_set{ m }.state , : );
    end
    if size( Q , 1 ) > 1
        qvar = sum( var( Q ) );
    end
    weight_set = weight_set / sum( weight_set );
    flat_Q = weight_set * Q;
    [ val greedy_action ] = max( flat_Q );
    
    % choose real action based on the input
    switch param_set.action_selection_type
        
        % pick the greedy action or do something random
        case 'epsilon_greedy'
            action = greedy_action;
            
        % pick the first model always
        case 'strens'
            model_index = 1;
            action = test_set{ model_index }.policy( test_set{ model_index }.state );
            
        % pick a random model
        case 'weighted_stochastic'
            model_index = sample_multinomial( weight_set );
            action = test_set{ model_index }.policy( test_set{ model_index }.state );
            
        % best of sampled set
        case 'boss'
            for m = 1:numel( test_set )
                state_count = size( test_set{ m }.mdp.reward , 1 );
                belief_set{ m } = zeros( state_count , 1 );
                belief_set{ m }( test_set{ m }.state ) = 1;
            end            
            for action_index = 1:action_count
                val = score_action( test_set , action_index , ...
                    param_set.search_depth , belief_set , action_count );
                boss_value( action_index ) = val;
            end
            [ val action ] = max( boss_value );
    end
end
was_greedy = ( action == greedy_action );
if rand < param_set.r_epsilon
    action = ceil( rand * action_count );
end

% ----------------------------------------------------------------------- %
function val = score_action( test_set , action , depth , belief_set , action_count )
gamma = test_set{ 1 }.mdp.gamma;

% if the depth is zero, then return the best of the values
if depth == 0
    q_set = compute_value( test_set , action , belief_set );
    val = max( q_set );
else
    
    % grab our current rewards, update belief
    current_reward = max( compute_reward( test_set , action , belief_set ) );
    next_belief_set = update_belief( test_set , action , belief_set );
            
    % try all next actions
    for next_action = 1:action_count
        future_reward( next_action ) = score_action( test_set , next_action , depth - 1 , next_belief_set , action_count );
    end
    
    % choose the best
    val = current_reward + gamma * max( future_reward );
end

% ----------------------------------------------------------------------- %
function r = compute_reward( test_set , action , belief_set );
for m = 1:numel( belief_set )
    r( m ) = sum( belief_set{ m } .* test_set{ m }.mdp.reward( : , action ) );
end

% ----------------------------------------------------------------------- %
function belief_set = update_belief( test_set , action , belief_set );
for m = 1:numel( belief_set )
    belief_set{ m } = test_set{ m }.mdp.transition( : , : , action ) * ...
        belief_set{ m };
end

% ----------------------------------------------------------------------- %
function q = compute_value( test_set , action , belief_set );
for m = 1:numel( belief_set )
    q( m , : ) = belief_set{ m }' * test_set{ m }.Q( : , action );
end




