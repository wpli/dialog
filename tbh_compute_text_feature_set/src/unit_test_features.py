## 
# Description
# Allows user to input a string, and prints out the features

import tbh_compute_text_feature_set
import pprint

if __name__ == '__main__':
    while 1:
        x = raw_input( "Type in a string " + \
                           "(lowercase, no commas or periods, " + \
                           "compose words if necessary, q to exit): " )

        # Create an artificial nbest list
        nbest_list = []
        for index in range(0,10):
            nbest_list.append( { 'text': x, 'score': 0 } )

        #print nbest_list

        feature_set = tbh_compute_text_feature_set.compute_feature_set( nbest_list, ['tbh_first_word', 'tbh_keyword', 'tbh_keyword_sequence', 'tbh_digits' ]  )

        #for feature_type in feature_set: 
        #    for feature in feature_set[ feature_type ]:                
        #        print feature_type, feature, feature_set[ feature_type ][ feature ]
        # print in a human-readable way
        pp = pprint.PrettyPrinter(indent=4)
        pprint.pprint( feature_set )   
