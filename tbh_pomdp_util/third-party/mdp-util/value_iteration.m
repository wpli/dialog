function [ V Q policy ] = value_iteration( mdp )
% value iteration
% requires: model mdp with .transition( s' , s , a ) , .reward( s , a )
% and discount factor gamma; maximum iterations capped at 500.
max_iter_count = 500;
action_count = size( mdp.transition , 3 );
gamma = mdp.gamma;

% initialize the value function
V = max( mdp.reward , [] ,2 );

% loop
for iter = 1:max_iter_count
    V_old = V;
    for a = 1:action_count
        Q( : , a ) = mdp.reward( : , a ) + gamma * ...
            transpose( V' * mdp.transition( : , : , a ) ); 
    end
    [ V policy ] = max( Q , [] , 2 );
    if norm( V_old  - V )/norm( V_old + V ) < 1e-04 % stopping criterion
        disp([ 'VI converged after ' num2str( iter ) ' iterations']);
        return
    end
end

