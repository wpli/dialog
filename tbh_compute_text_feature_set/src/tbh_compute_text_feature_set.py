# This module is the top level module for taking input text and
# converting it into a set of features.  The nbest list should be a
# list with each item being a dictionary with 'text' and 'score'
# entries; the function compute_feature_set will break if an unknown
# type of feature is requested

##
# Description
# Takes an nbest list and converts it to features
def compute_feature_set( nbest_list , feature_type_list ):
    feature_set = {}
    feature_set['nbest_list'] = nbest_list

    for feature_type in feature_type_list:
        exec "import " + feature_type

        # This is where all the values of the features are determined
        # All of the decision processes for setting values for
        # features are in <feature_type>.py
        feature_set[ feature_type ] = eval( feature_type + ".compute_feature_set( nbest_list )" )
    return feature_set



