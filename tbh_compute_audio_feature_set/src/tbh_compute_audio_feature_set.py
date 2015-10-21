# This module is the top level module for taking input text and
# converting it into a set of features.  The nbest list should be a
# list with each item being a dictionary with 'text' and 'score'
# entries; the function compute_feature_set will break if an unknown
# type of feature is requested

import basic_statistics

##
# Description
# Takes an nbest list and converts it to features
def compute_feature_set( audio_power_list ):
    feature_set = dict()
    feature_set['basic_statistics'] = basic_statistics.compute_feature_set( audio_power_list )
    return feature_set
