function controller_state = update_controller( sol , problem, controller_type , ...
    controller_state , action , observation )
% function controller_state = update_controller( sol , problem, controller_type , ...
%     controller_state , action , observation );
% controller_type is fsc or belief
switch controller_type
    case 'fsc'
        controller_state = sample_multinomial( ... 
            sol.transition( : , controller_state , observation ) );
    case 'belief'
        action_update = problem.transition(:,:,action) * controller_state;
        controller_state = action_update .* problem.observation( : , action , observation );
        if sum( controller_state ) == 0
            controller_state = action_update;
            disp( 'update controller: warning! invalid observation!' )
        else
            controller_state = controller_state / sum( controller_state );
        end
end
    