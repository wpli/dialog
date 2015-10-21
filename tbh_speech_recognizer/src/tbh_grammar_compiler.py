## Grammar Compiler

##     * runs when called
##     * grammar object has a unique grammar_tag
##     * phoneme_map: object with a value for every pairwise set of phonemes, and phoneme_map_tag
##     * compile_grammar( grammar_file_address , phoneme_map ) outputs grammar object
##     * adjust_grammar_weights( grammar_file_address , new weights ) writes new grammar file with new weights, returns new grammar
##     * adjust_phoneme_map( phoneme_map ) returns new phoneme_map object 

import sys
import os
sys.path.append( "../../tbh_api/src" )
from tbh_api import *

##
# Description
# Compiles a new grammar
@tbh_api_callable
def compile_grammar( grammar_file_stem , phoneme_map ):
    grammar = tbh_api.data_model.grammar_t()
    grammar.phoneme_map = phoneme_map;
    grammar.weight_list = None

    # finale! for now we don't actually use the weights or the phoneme
    # map in the compilation!!

    # store the grammar file as text
    f = open( grammar_file_stem + '.jsgf' )
    grammar.original_jsgf = f.read()
    f.close()

    # finale! need a path to the compiler! and grammar file!

    # run the grammar compiler
    os.system( 'buildrec ' + grammar_file_stem + '.jsgf' )

    # read in the compiled files
    f = open( grammar_file_stem + '.cfg' )
    grammar.compiled_cfg = f.read()
    f.close()
    f = open( grammar_file_stem + '.pfst' )
    grammar.compiled_pfst = f.read()
    f.close()

    return grammar

# ** there are path issues with where scripts are **
#    should be addressed to a local place
#    start out with speech_recognizer
#    install_grammar_builder.sh
#    build_rec name_of_file
#    test folder .jsgf file is the text version of the grammar file
#    produces a cfg and pfst file required for recognizer


    


