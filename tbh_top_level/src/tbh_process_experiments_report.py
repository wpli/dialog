import sys

sys.path.append( '../../tbh_dialog_manager/src' )

import tbh_experiment_controller

import cPickle
import random


def meanstdv(x):
    from math import sqrt
    n, mean, std = len(x), 0, 0
    for a in x:
        mean = mean + a
    mean = mean / float(n)
    for a in x:
        std = std + (a - mean)**2
    std = sqrt(std / float(n-1))
    return mean, std

def get_confidence_score( confidence_score ):
    return confidence_score - random.random()/10

def calculate_elapsed_time( experiment ):
    start_time = experiment.start_time
    expname = experiment.experiment_name[1].split()
    end_time = None
    for x in experiment.turn_list:
        if x.system_response == expname:
            end_time = x.time
            break

    if end_time == None:
        return None

    else:
        return ( end_time - start_time )


def calculate_total_words( experiment ):
    word_count = 0
    for x in experiment.turn_list:
        word_count += len( x.utterance_hypothesis.split() )
        if x.system_response == experiment.experiment_name[1].split():
            return word_count
        

    # if unsuccessful dialog return None
    return None

        


def calculate_actual_turns( experiment_name, turn_list ):
    counter = 0
    for x in turn_list:
        counter += 1
        #print experiment_name[1].split(), x.system_response
        if x.system_response == experiment_name[1].split():
            break
    #print "DONE"
    return counter

def determine_success( experiment ):
    system_response_list = []
    for x in experiment.turn_list:
        system_response_list.append( x.system_response )


    if experiment.experiment_name[1].split() in system_response_list:
        return True
    else:
        #print system_response_list
        #print experiment.experiment_name[1].split()

        return False
        

if __name__ == '__main__':
    f = open( sys.argv[1], 'r' )
    x = cPickle.load( f )

    """
    for i in x:
        print "\n-----------------------------------------"
        print "DIALOG:", i.experiment_name
        print "Time: ", calculate_elapsed_time( i )
        print ( i.end_time - i.start_time ) 
        try: 
            print  ( i.end_time - i.start_time ) / calculate_elapsed_time( i )  
        except:
            pass

        for index, t in enumerate( i.turn_list ):
            confidence_score = get_confidence_score( t.confidence_score )

            print "TURN", index
            print "hypothesis: %s | filename: %s | confidence score: %s | system response: %s " % ( t.utterance_hypothesis, t.param_dict['filename'], confidence_score, t.system_response )
            for a in t.param_dict['nbest_list']:
                print a['text']
       """
             

    # compute statistics

    pomdp_time_list = []
    threshold_time_list = []

    pomdp_turn_list = []
    threshold_turn_list = []

    pomdp_success_list = [0,0]
    threshold_success_list = [0,0]
    

    pomdp_word_list = []
    threshold_word_list = []

    for i in x:
        elapsed_time = calculate_elapsed_time( i )
        #print elapsed_time

        #elapsed_time =  i.end_time - i.start_time

        turns = calculate_actual_turns( i.experiment_name, i.turn_list )
        words = calculate_total_words( i )

        success = determine_success( i )

        if i.experiment_name[0] == 'POMDP':
            if elapsed_time != None:
                pomdp_time_list.append( elapsed_time )

            if words != None:
                pomdp_word_list.append( words )

                


            pomdp_turn_list.append( turns )
            if success:
                pomdp_success_list[0] += 1
            else:
                pomdp_success_list[1] += 1

        elif i.experiment_name[0] == 'THRESHOLD':
            if elapsed_time != None:
                threshold_time_list.append( elapsed_time )
            
            threshold_turn_list.append( turns )
            if success:
                threshold_success_list[0] += 1
            else:
                threshold_success_list[1] += 1

            if words != None:
                threshold_word_list.append( words )




        else:
            print "ERROR!", i.experiment_name

    #print "POMDP"
    ms_pomdp_time = meanstdv( pomdp_time_list )
    ms_pomdp_turns = meanstdv( pomdp_turn_list )

    #print "\n"
    #print "THRESHOLD"
    ms_threshold_time = meanstdv( threshold_time_list )
    ms_threshold_turns = meanstdv( threshold_turn_list )
    #print threshold_success_list


    print "%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s" % ( \
        sys.argv[1],
        pomdp_success_list[0], 
        pomdp_success_list[1], 
        ms_pomdp_time[0],
        ms_pomdp_time[1],
        ms_pomdp_turns[0], 
        ms_pomdp_turns[1], 
        threshold_success_list[0], 
        threshold_success_list[1], 
        ms_threshold_time[0],
        ms_threshold_time[1],
        ms_threshold_turns[0], 
        ms_threshold_turns[1] )

    print meanstdv( pomdp_word_list )
    print meanstdv( threshold_word_list )
