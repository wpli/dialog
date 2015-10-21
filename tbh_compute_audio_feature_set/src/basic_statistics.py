##
# Description: 
# Compute statistics based on the audio power scores
def compute_feature_set( audio_power_list ):
    window_size = len( audio_power_list )
    middle_index = window_size / 2
    feature_set = dict()

    # compute some basic things
    if window_size > 2:
        feature_set[ 'first_max' ] = max( audio_power_list[0:middle_index] )
        feature_set[ 'first_min' ] = min( audio_power_list[0:middle_index] )
        feature_set[ 'first_mean' ] = sum( audio_power_list[0:middle_index] ) / middle_index
        feature_set[ 'last_max' ] = max( audio_power_list[middle_index:window_size] )
        feature_set[ 'last_min' ] = min( audio_power_list[middle_index:window_size] )
        feature_set[ 'last_mean' ] = sum( audio_power_list[middle_index:window_size] ) / ( window_size - middle_index )
    else:
        feature_set[ 'first_max' ] = None
        feature_set[ 'first_min' ] = None
        feature_set[ 'first_mean' ] = None
        feature_set[ 'last_max' ] = None
        feature_set[ 'last_min' ] = None
        feature_set[ 'last_mean' ] = None

    # return
    return feature_set
