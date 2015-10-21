function action = get_action( sol , controller_type , controller_state )
% function action = get_action( sol , controller_type , controller_state )
% controller_type is belief or fsc
switch controller_type
    case 'fsc'
        action = sample_multinomial( sol.policy( controller_state , : ) );
    case 'belief'
        vals = controller_state' * sol.Vtable{end}.alphaList;
        [val maxInd] = max(vals,[],2);
        action = sol.Vtable{end}.alphaAction(maxInd);
end
