import cPickle

TAG_DICT = '../../tbh_output_interface/bin/tag_dict_full.pkl'
CONFIDENCE_DICT = '../../tbh_output_interface/bin/confidence_dict.pkl' 


import sys
sys.path.append( '../../tbh_dialog_manager/src/' )
import tbh_pomdp_manager
import numpy
LOGISTIC_PARAMETERS = [ -0.0876,-1.0227 ]


class tbh_demonstration_interface:
    def __init__( self, tag_dict, confidence_dict ):
        # Data sources for demonstration purposes

        f = open( tag_dict, 'r' )
        self.tag_dict = cPickle.load( f ) 
        f.close()
        
        g = open( confidence_dict, 'r' )
        self.confidence_dict = cPickle.load( g )
        g.close()

    def get_nbest_features( self, prefix, filename ):
        file_key = "%s_%s" %( prefix, filename )
        tag_dict_entry = self.tag_dict[file_key]

        param_dict = {}
        
        # Make the n-best list
        nbest_list = []
        
        for result_entry in tag_dict_entry['result']['full']:

            nbest_list.append( { 'text': result_entry['transcript'] } )

        param_dict['nbest_list'] = nbest_list
        param_dict['filename'] = 'temp'

        return param_dict


    def get_adaboost_score( self, prefix, filename ):
        file_key = "%s_%s" %( prefix, filename )
        confidence_features_dict = self.confidence_dict[file_key]
        return confidence_features_dict['adaboost']

    def determine_confidence_in_hypothesis( self, adaboost_score, logistic_parameters ):
        constant = float( logistic_parameters[0] )
        coefficient = float( logistic_parameters[1] )

        confidence_in_hypothesis = float(1) / \
            float( 1 + numpy.exp(constant + \
                                     coefficient * float( adaboost_score ) ) )

        #print "adaboost: %s; confidence: %s" %( adaboost_score, confidence_in_hypothesis )

        return confidence_in_hypothesis



    def get_nbest_features_full_filename( self, full_filename ):

        file_key = full_filename
        tag_dict_entry = self.tag_dict[file_key]

        param_dict = {}
        
        # Make the n-best list
        nbest_list = []
        
        for result_entry in tag_dict_entry['result']['full']:

            nbest_list.append( { 'text': result_entry['transcript'] } )

        param_dict['nbest_list'] = nbest_list
        param_dict['filename'] = 'temp'

        return param_dict


    def get_adaboost_score_full_filename( self, full_filename ):
        file_key = full_filename
        confidence_features_dict = self.confidence_dict[file_key]
        return confidence_features_dict['adaboost']


    
if __name__ == '__main__':
    x = tbh_demonstration_interface( tag_dict=TAG_DICT, confidence_dict=CONFIDENCE_DICT )

    confidence_score_dict = {}

    g = open( CONFIDENCE_DICT, 'r' )
    cd = cPickle.load( g )




    for entry in x.confidence_dict.keys():

        if 1:

            adaboost_score = x.get_adaboost_score_full_filename( \
            entry )
            confidence_score = x.determine_confidence_in_hypothesis( adaboost_score, LOGISTIC_PARAMETERS )
            confidence_score_dict[entry] = confidence_score
        #except:
        #    pass

    print x.confidence_dict[entry]
    print len( confidence_score_dict )

    import cPickle
    f = open('confidence_scores.pkl', 'w')
    cPickle.dump(confidence_score_dict, f)
    f.close()




        


