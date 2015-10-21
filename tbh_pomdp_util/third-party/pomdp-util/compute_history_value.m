function v = compute_history_value( pomdp , history )
% function v = compute_history_value( pomdp , history )
% computes the discounted value of the history
T = size( history , 1 );
v = ( pomdp.gamma .^ ( 0:( T - 1 ) ) ) * history( : , 4 );