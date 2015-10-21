ls

clearvars qmdp;
clearvars pomdp;

addpath( '../third-party/util' );
addpath( '../third-party/pomdp-util/' )


% --- create a very simple POMDP --- %
% basic stuff: the start_dist is a parameter used in simulations for where
% the real start state should be (can be different from the assumed start)


% states correspond to intents, i.e. time, activities
pomdp.nrStates = 62;
pomdp.gamma = 0.95;

% action space:

% type of dialog pomdp
% 1:  no confirmations, just submit/repeat/failo
% 2: 1 + confirmation questions
% 3: compatible with the python tbh dialog
% pomdp.type = 1;
pomdp.type = 3;

if pomdp.type == 1
    pomdp.nrActions = pomdp.nrStates + 2;
    pomdp.nrObservations = pomdp.nrStates;
elseif pomdp.type == 2
    pomdp.nrActions = pomdp.nrStates * 2 + 2;
    pomdp.nrObservations = pomdp.nrStates + 2;
elseif pomdp.type == 3
   
    pomdp.nrGeneralActions = 2;
    
    % the actual observations
    % includes, potentially, confirmation questions for every
    % state  
    pomdp.nrActions = pomdp.nrGeneralActions + 2 * ...
        pomdp.nrStates;     
    
    % yes, no, null yes_record, null no_record, null say_keyword
    pomdp.nrGeneralObservations = 3;
    pomdp.nrObservations = pomdp.nrGeneralObservations + pomdp.nrStates;
   
    
end


% Initialize the starting distribution, uniform over states

pomdp.start = ones( 1, pomdp.nrStates ) * 1/pomdp.nrStates;
pomdp.start;
pomdp.start_dist = pomdp.start'; % transpose of vector


% the transition(s',s,a) , observation(s,a,o) , rewards(s,a)
pomdp.reward = dialog_reward_function( pomdp );

% transitions are all self-transitions because the state (user's intent) in
% a dialog does not change
pomdp.transition = dialog_transition_function( pomdp );

% observations relate the speech recognition output (observation) to the
% underlying user's intent
pomdp.observation = dialog_observation_function_new( pomdp );
pomdp.maxReward = max( pomdp.reward(:) );

% --- solve the POMDP --- %
% uses pbvi to solve the POMDP (kinda dated, but works fine for small
% models): the %structure sol contains the alpha vectors and actions
%belief_count = 100; pbvi_iter_count = 15;
%belief_set = sampleBeliefs( pomdp , belief_count );
%[TAO vL sol] = runPBVILean( pomdp , belief_set , pbvi_iter_count );

% --- run trials with the POMDP --- %
% the sim_pomdp is the "real environment" in case you want the real
% environment to be different from the POMDP model that you used above, the
% max iter count is the maximum number of iterations a trial can last
%rep_count = 10; 
%max_iter_count = 10;
%sim_pomdp = pomdp;
%[ reward_set sum_reward_set iter_count_set history_set ] = testPOMDP( pomdp , ...
%    sim_pomdp , sol , rep_count , max_iter_count );

% --- solving the MDP --- %
% for fun, we can also solve the underlying MDP; where policy gives the
% action to take in each state, and Q(s,a) and V(s) give the action-value
% and the value functions, respectively
addpath( '../third-party/mdp-util/' )
[ V Q policy ] = value_iteration( pomdp );

% compute Q-MDP for different values
% Assume varying amounts of probability for one particular belief
% and the remaining belief distributed uniformly over the other states
% Note the effect on the reward - should basically be a threshold model
% create policy table: pomdp.transition( : , : , 1 ) = [ 1 0 ; 0 1 ];

qmdp_belief_points = 10;
%qmdp = solve_qmdp( qmdp_belief_points, pomdp, Q ); 
qmdp = solve_qmdp_two_competing_states( qmdp_belief_points, pomdp, ...
                                        Q )
qmdp.policy



    





