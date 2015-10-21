function [ observation ] = dialog_observation_function( pomdp )
             
   top_observation_value = 0.6;
   remaining_observation_value = ( 1 - top_observation_value ) / ( pomdp.nrObservations - 1 );    

   confirmation_matched = 0.9;
   confirmation_unmatched = ( 1 - confirmation_matched ) / pomdp.nrStates / 5; 
   remaining_observation_for_confirmation = ( 1 - confirmation_matched ...
                                              - confirmation_unmatched ...
                                              ) / ( pomdp.nrStates ...
                                                    - 2 );
   % Desired behavior
   % observation(s,a,o)
   % action space
   % i = submit_i
   % 2*i = confirm_i 
   % 2*i + 1 repeat_initial_question
   % 2*i + 2 fail_dialog
   
   
               
        % in general, the observation can be a function of the action
        % in a POMDP, but we are not treating it in that manner
        % therefore, the observation function is invariant with respect to 
        % the action

        

        if pomdp.type == 1
            % sets all of the values to the remaining observation value
            observation( :, :, : ) = ones( pomdp.nrStates, ...
                                               pomdp.nrActions, ...
                                           pomdp.nrObservations ) * remaining_observation_value
                           
            for i=1:pomdp.nrStates
                observation( i, : , i ) = ones( 1, pomdp.nrActions ...
                                                ) * top_observation_value;
            end

            
            
            return      

            
        elseif pomdp.type == 2
            %replace the observation functions between
            %pomdp.nrStates + 1 to pomdp.nrStates*2
            
            %for i=1:pomdp.nrStates            
            %for submission actions
            observation( :, 1:pomdp.nrStates, : ) = ones( pomdp.nrStates, ...
                                                          pomdp.nrStates, ...
                                                          pomdp.nrObservations ...
                                                          ) * ...
                remaining_observation_value; 
              
           
            for i=1:pomdp.nrStates
                observation( i, 1:pomdp.nrStates, i ) = ones( 1, ...
                                                              pomdp.nrStates, i ...
                                                ) * top_observation_value;
            end
            


            % the confirmation states
            first_confirmation_action = pomdp.nrStates + 1;
            last_confirmation_action = pomdp.nrStates * 2;
            observation( :, first_confirmation_action: ...
                         last_confirmation_action, : ...
                         ) = ones( pomdp.nrStates, pomdp.nrStates, ...
                                   pomdp.nrObservations ) * remaining_observation_for_confirmation; 

            for i=1:pomdp.nrStates
                % replace the matching value with the
                % confirmation_unmatched value
                observation( i, i + pomdp.nrStates, pomdp.nrStates ...
                             + 2 ) = confirmation_unmatched;
                
                % replace the matching value with the
                % confirmation_matched value
                observation( i, i + pomdp.nrStates, pomdp.nrStates ...
                             + 1 ) = confirmation_matched;
                
            end
                     
            
            % add the repeat_initial_question and fail_dialog
            % questions at the end
            repeat_index = pomdp.nrActions - 1;
            fail_index = pomdp.nrActions;
            observation( :, repeat_index:fail_index, : ) = ones( pomdp.nrStates, ...
                                                          2, ...
                                                          pomdp.nrObservations ...
                                                          ) * ...
                remaining_observation_value; 
              
           
            for i=1:pomdp.nrStates
                observation( i, repeat_index:fail_index , i ) = ones( 1, 2 ...
                                                ) * top_observation_value;
            end
            
            

        elseif pomdp.type == 3
            % Recall this is O(s,a,o)
            % s X a X o tensor
            % s X (2s+2) X (s+3) tensor
            % 96 X 194 X 101
            % Strategy: create blocks of matrices that will be
            % concatenated

            
            % corresponding_observation_matrix: for observations
            % directly associated with a state
            % in the tensor cube, this will take the entries:
            % ( 1:s, 1:(s), 1:(s+3) )                                  
            % ( 1:96, 1:99, 1:101 )
            
            % Create entire tensor with the remaining observation
            % value            
            nrNonConfirmationActions = pomdp.nrActions - pomdp.nrStates;
            
            corresponding_observation_tensor = ones( pomdp.nrStates, ...
                                                     nrNonConfirmationActions, ...
                                                     pomdp.nrObservations ...
                                                     ) * ...
                remaining_observation_value;
            
            for i=1:pomdp.nrStates
                corresponding_observation_tensor( i, 1:nrNonConfirmationActions, ...
                                                  i + ...
                                                  pomdp.nrGeneralObservations ...
                                                  ) = ones( 1, nrNonConfirmationActions, 1 ) * top_observation_value;
                
                
                
                
            end


            % CONFIRMATION
            % In the tensor cube, this will take the entries:
            % ( 1:96, 99:194, 1:101 )                                  
            %                        
            confirmation_yes = 0.4;
            matching_question = 0.4;
            confirmation_no = ( 1 - confirmation_yes - ...
                                       matching_question ) / ( ...
                                           pomdp.nrObservations - 2 ) / 5
            
                                  
            remaining_observation_for_confirmation = ( 1 - ...
                                                       confirmation_yes ...
                                                       - matching_question ...
                                                       - ...
                                                       confirmation_no ...
                                                       ) / ( pomdp.nrObservations - 2 )
            
            
            confirmation_tensor = zeros( pomdp.nrStates, pomdp.nrStates, ...
                                        pomdp.nrObservations );

            
            % for confirmations not corresponding to the true state
            false_confirmation_no = 0.4;
            false_matching_question = 0.4;
            false_confirmation_yes = ( 1 - false_confirmation_no - ...
                                       false_matching_question ) / ...
                ( pomdp.nrObservations - 2 ) / 5
            false_remaining_observation_for_confirmation = ( 1 - ...
                                                       confirmation_yes ...
                                                       - matching_question ...
                                                       - ...
                                                       confirmation_no ...
                                                       ) / ( pomdp.nrObservations - 2 )
            
            
            for i=1:pomdp.nrStates
                % replace the matching value with the
                % confirmation_unmatched value
                for j=1:pomdp.nrStates
                    if i==j
                        % confirming the actual state
                        confirmation_tensor( i, j, : ) = ones( 1, ...
                                                               1, ...
                                                               pomdp.nrObservations ) * remaining_observation_for_confirmation;
                        
                        % answer no
                        confirmation_tensor( i, j, 4 ) = confirmation_no;

                        
                       
                        % replace the matching value with the
                        % confirmation_matched value
                        confirmation_tensor( i, j, 5 ) = ...
                            confirmation_yes;

                        
                        confirmation_tensor( i, j, ...
                                             pomdp.nrGeneralObservations ...
                                             + i ) = matching_question;
                        
                    else
                        confirmation_tensor( i, j, : ) = ones( 1, ...
                                                               1, ...
                                                               pomdp.nrObservations ) * false_remaining_observation_for_confirmation;
                        

                        % answer no
                        confirmation_tensor( i, j, 4 ) = false_confirmation_no;

                        
                       
                        % replace the matching value with the
                        % confirmation_matched value
                        confirmation_tensor( i, j, 5 ) = ...
                            false_confirmation_yes;

                        
                        confirmation_tensor( i, j, ...
                                             pomdp.nrGeneralObservations ...
                                             + i ) = false_matching_question;
                        

                    end

                    
                    normalizer = sum( confirmation_tensor( i, ...
                                                               j, : ...
                                                               ) );
                    confirmation_tensor( i, j, : ) = ...
                        confirmation_tensor( i, j, : ) / normalizer ...
                            ;                        
                
                    
                
            end
            

            % Remaining
            % ( 1:96, 1:99, 1:5)
            % These correspond to observations that do not change
            % the belief
            % 1: no change, did not parse - "say keyword and please repeat" 
				      
            % 2: no change, detected keyword but did not parse - "please repeat"
            % 3: understood but did not detect keyword - "please say keyword before your command."
            % 4: "no" but a confirmatory question was not asked - "repeat question"
            % 5: "yes" but a confirmatory question was not asked - "repeat question"

            unchanged_distribution_value = 1 / pomdp.nrObservations;
            remaining_observation_tensor = ones( pomdp.nrStates, ...
                                                 nrNonConfirmationActions, ...
                                                 pomdp.nrGeneralObservations ) * unchanged_distribution_value;
               
            
            
            % Put the entire tensor together 
            observation = zeros( pomdp.nrStates, pomdp.nrActions, ...
                                 pomdp.nrObservations );
            
            observation( 1:pomdp.nrStates, 1:nrNonConfirmationActions, ...
                         1:pomdp.nrGeneralObservations ) = remaining_observation_tensor;
            
            % observations corresponding to actions
            % ( 1:96, 1:98, 1:100 )                                             
            observation_starting_index = pomdp.nrGeneralObservations + 1;            
            observation_ending_index = pomdp.nrGeneralObservations + pomdp.nrStates;
            
            
            observation( 1:pomdp.nrStates, 1:nrNonConfirmationActions, ...
                         1:pomdp.nrObservations ) = corresponding_observation_tensor;

            
            % observations corresponding to confirmations
            % ( 1:96, 99:194, 1:100 )                                             
            %99
            first_confirmation_action = pomdp.nrGeneralActions + ...
                pomdp.nrStates + 1;
            
            
            % 194
            last_confirmation_action = pomdp.nrGeneralActions + ...
                pomdp.nrStates * 2;
                     
            observation( 1:pomdp.nrStates, first_confirmation_action ...
                         : last_confirmation_action, 1:pomdp.nrObservations ...
                         ) = confirmation_tensor;
                            
                                         
            
        end

                        
end


