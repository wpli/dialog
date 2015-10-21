addpath( '../util' );

% --- create a very simple POMDP --- %
% basic stuff: the start_dist is a parameter used in simulations for where
% the real start state should be (can be different from the assumed start)
pomdp.nrActions = 2;
pomdp.nrStates = 4;
pomdp.nrObservations = 3;
pomdp.gamma = .95;
pomdp.start = [ 0 .5 .5 0 ];
pomdp.start_dist = pomdp.start'; % transpose of vector

% the transition(s',s,a) , observation(s,a,o) , rewards(s,a)
pomdp.reward = [ 10 10 ; -1 -1 ; -1 -1 ; -10 -10 ];
pomdp.transition( : , : , 1 ) = [ 1 .8 0 0 ; 0 .2 .8 0 ; 0 0 .2 .8 ; 0 0 0 .2 ];
pomdp.transition( : , : , 2 ) = [ 1 .8 0 0 ; 0 .2 .8 0 ; 0 0 .2 .8 ; 0 0 0 .2 ];
pomdp.observation( : , : , 1 ) = [ .8 .8 ; .1 .1 ; .1 .1 ; .1 .1 ];
pomdp.observation( : , : , 2 ) = [ .1 .1 ; .8 .8 ; .8 .8 ; .1 .1 ];
pomdp.observation( : , : , 3 ) = [ .1 .1 ; .1 .1 ; .1 .1 ; .8 .8 ];
pomdp.maxReward = max( pomdp.reward(:) );

% --- solve the POMDP --- %
% uses pbvi to solve the POMDP (kinda dated, but works fine for small
% models): the structure sol contains the alpha vectors and actions
belief_count = 100; pbvi_iter_count = 15;
belief_set = sampleBeliefs( pomdp , belief_count );
[TAO vL sol] = runPBVILean( pomdp , belief_set , pbvi_iter_count );

% --- run trials with the POMDP --- %
% the sim_pomdp is the "real environment" in case you want the real
% environment to be different from the POMDP model that you used above, the
% max iter count is the maximum number of iterations a trial can last
rep_count = 10; 
max_iter_count = 10;
sim_pomdp = pomdp;
[ reward_set sum_reward_set iter_count_set history_set ] = testPOMDP( pomdp , ...
    sim_pomdp , sol , rep_count , max_iter_count );

% --- solving the MDP --- %
% for fun, we can also solve the underlying MDP; where policy gives the
% action to take in each state, and Q(s,a) and V(s) give the action-value
% and the value functions, respectively
addpath( '../mdp-util/' )
[ V Q policy ] = value_iteration( pomdp );
