##
# Description: 
# Compute statistics based on the nbest list scores
def compute_feature_set( nbest_list ):
    
    # get all the scores
    score_list = []
    for item in nbest_list:
        score_list.append( item['score'] )

    feature_set = {}
    # compute some basic things
    try:
        feature_set[ 'max' ] = max( score_list )
        feature_set[ 'min' ] = min( score_list )
        feature_set[ 'mean' ] = sum( score_list ) / len( score_list )
    except:
        feature_set[ 'max' ] = 'NaN'
        feature_set[ 'min' ] = 'NaN'
        feature_set[ 'mean' ] = 'NaN'

    # return
    return feature_set
