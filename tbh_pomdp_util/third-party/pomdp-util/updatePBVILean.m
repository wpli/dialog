function [backupStats aL vL] = updatePBVILean(problem, S,h,backupStatsIn,TAO,epsilon,saveQ,useEps)
% function [backupStats aL vL] =
% updatePBVILean(S,h,backupStatsIn,TAO,epsilon)
% runs the point-based value iteration algorithm on Lean solution
%  S - set of beliefs
%  h - number of additional backups to perform
%  backupStatsIn - previous iterations
%  TAO - action/observation transition structure, see createTAO function
%  epsilon for convergence
%  below (idea: if dynamics are unchanged, we can reuse this structure)
%
% backup stats stores our solution and intermediate computations
%   backupStats.Q{ iter, belief number }(:, action ) = gamma^a_b 
%   backupStats.Vtable{ iter }.alphaList( :,i ) = unique alpha vector list
%   backupStats.Vtable{ iter }.alphaAction(i) = action for alpha i
%
% all vectors are COLUMN VECTORS
backupStats = backupStatsIn;

% create TAO if not given
if nargin < 5
    TAO = createTAO(problem,S);
    saveQ = true;
end

backupStats = backupQLean(problem,S,backupStats,TAO,0);
[a1 v1] = getAction( S, backupStats.Vtable );
aL = a1'; vL = v1';

% perform additional dynamic programming backups
for i = 2:h
    % disp(['starting backup ' num2str(i)]);
    backupStats = backupQLean(problem,S,backupStats,TAO,saveQ);

    if nargin > 5
        [a2 v2] = getAction( S, backupStats.Vtable );
        aL = [aL ; a2']; vL = [vL ; v2'];
        conver = sum(abs(v2-v1)); v1 = v2;
        if conver < epsilon && useEps
            return;
        end
        disp([ 'did backup ' num2str([i conver]) ]);
    end
    
    
end

%------------------------------------------------------------------------
function TAO = createTAO(problem,S)
% when TAO{action}{obs} is multiplied by backupStats.Vtable{1}.alphaList,
% we get gammaA
    TAO = cell(problem.nrActions,problem.nrObservations);    
     for action = 1:problem.nrActions
        for obs = 1:problem.nrObservations
     
            % compute transition matrix                        
            tprob = problem.transition(:,:,action);
            oprob = problem.observation(:,action,obs);
            for i = 1:problem.nrStates
                tprob(:,i) = tprob(:,i) .* (oprob);
            end
            tprob = tprob * problem.gamma;
            TAO{action}{obs} = tprob';
        end
     end
    
%------------------------------------------------------------------------
function backupStats = backupQLean(problem,S,backupStatsIn,TAO,saveQ)
    % computes the Q vectors for the next backup
    alphaCount = size(backupStatsIn.Vtable{1}.alphaList,2);

    % first compute gammoAO, (return if are in state s, see o, do a)
    gammaAO = cell(problem.nrActions,1);
    for action = 1:problem.nrActions
        for obs = 1:problem.nrObservations
            gammaAO{action}{obs} = TAO{action}{obs} * backupStatsIn.Vtable{1}.alphaList;
        end
    end

    % next pick q vectors for each belief
    for action = 1:problem.nrActions

        % add expected return for each obs + action
        gammaAB = repmat( problem.reward(:,action)  ,1,size(S,1)  );
        for obs = 1:problem.nrObservations
            [ vals inds ] = max( S * gammaAO{action}{obs},[],2 );
            gammaAB = gammaAB + gammaAO{action}{obs}(:, inds);
        end
        Q(:,:,action) = gammaAB';
    end


    % update the V
    backupStats = updateBestQLean(problem,S,Q);
    if saveQ
        backupStats.Q = Q;
    end

    % get rid of huge gamma structure
    clear gammaAO;
    
%------------------------------------------------------------------------
function backupStats = updateBestQLean(problem,S,Q)
    % updates backup stats for each q vector, belief
    
    % first determine best alpha vector for each belief
    for ac = 1:problem.nrActions
        vals(:,ac) = sum( Q(:,:,ac) .* S,2 );
    end
    [maxVal action] = max(vals');
    for a = 1:problem.nrActions % select the best actions
        mask(:,:,a) = repmat( transpose(action == a), 1, problem.nrStates );
    end
    v = squeeze(sum( Q.*mask,3));
    a = action';
    clear mask;

    % next prune the list to a unique set
    [ alphaList ind1 ind2 ] = unique( v, 'rows' );
    backupStats.Vtable{1}.alphaList = alphaList';
    backupStats.Vtable{1}.alphaAction = a( ind1 );
    