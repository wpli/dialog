function [ reward ] = dialog_reward_function( pomdp )    
    %get_intent_correct = 15;
    %get_intent_wrong = -70;
    %repeat_initial_question = -3;
    %fail_dialog = -5;   
    %ask_confirmation_right = -1;
    %ask_confirmation_wrong = -4;
    
    get_intent_correct = pomdp.reward_params(1);
    get_intent_wrong = pomdp.reward_params(2);
    repeat_initial_question = pomdp.reward_params(3);
    fail_dialog = pomdp.reward_params(4);
    ask_confirmation_right = pomdp.reward_params(5)
    ask_confirmation_wrong = pomdp.reward_params(6);
    
    % make the states and actions correspond numerically for
    % elegance
    % i.e. when s=a, the get_intent_correct reward should be
    % applied
    % r(s,a)
    reward = ones( pomdp.nrStates, pomdp.nrStates ) * ...
             get_intent_wrong;

    if pomdp.type == 1 or pomdp.type == 2
        
        for i=1:pomdp.nrStates
            reward( i, i ) = get_intent_correct; 
        end
        
        repeat_reward = ones( pomdp.nrStates, 1 ) * ...
            repeat_initial_question;
        fail_reward = ones( pomdp.nrStates, 1 ) * fail_dialog; 
    end
    
        
        
    if pomdp.type == 1
        % add the repeat and fail_dialog states
        reward = horzcat( reward, repeat_reward, fail_reward );
             
    
    
    % add confirmation functions      
    elseif pomdp.type == 2
        confirmation_reward = ones( pomdp.nrStates, pomdp.nrStates ...
                                    ) * ask_confirmation_wrong;
        for i=1:pomdp.nrStates
            confirmation_reward( i, i ) = ask_confirmation_right; 
        end
        
        reward = horzcat( reward, confirmation_reward, repeat_reward, ...
                          fail_reward);

    elseif pomdp.type == 3
        % Construct the reward matrix
        % S X A
        % S X ( 2 + 2*S )

        reward = zeros( pomdp.nrStates, pomdp.nrActions );
            
        for i = 1:pomdp.nrStates
            for j = 1:pomdp.nrActions
                if j <= pomdp.nrStates
                    if i==j
                        reward( i, j ) = get_intent_correct;
                    else
                        reward( i, j ) = get_intent_wrong;
                    end
                elseif j <= (2*pomdp.nrStates)
                    if j == i + pomdp.nrStates
                        reward( i, j ) = ask_confirmation_right;
                    else
                        reward( i, j ) = ask_confirmation_wrong;
                    end
                elseif j == ( 2*pomdp.nrStates + 1 )
                    reward( i, j ) = repeat_initial_question;
                elseif j == ( 2*pomdp.nrStates + 2 )
                    reward( i, j ) = fail_dialog; 
                    
                end
            end
            
        end
        
                
                
                
                
                
                        
                
               
                        
                        
                    
                
            
        
        

        % first part: repeat question
        %repeat_reward = ones( pomdp.nrStates, pomdp.nrGeneralActions ...
                              %) * repeat_initial_question;
        
        % second part: submit an answer
        %submit_reward = ones( pomdp.nrStates, pomdp.nrStates ) * ...
        %    get_intent_wrong; 
                      
        %for i=1:pomdp.nrStates
        %    submit_reward( i, i ) = get_intent_correct;
        %end
        
        
        % third part: confirmation
        %confirmation_reward = ones( pomdp.nrStates, pomdp.nrStates ...
        %                            ) * ask_confirmation_wrong;
        
        %for i=1:pomdp.nrStates
            %confirmation_reward( i, i ) = ask_confirmation_right;
        %end
        
        %reward = horzcat( repeat_reward, submit_reward, confirmation_reward ...
        %                  );
           
        
        
        
    end


    return 
    
    

        
end

