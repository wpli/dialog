# file where the first words/phrases are stored
keyword_file = "../../tbh_compute_text_feature_set/src/tbh_first_word.txt"

##
# Description: 
# Look for a relevant word (i.e. chair) in the first position of the
# input (i.e. did they start as if a command?), only checks the first
# input of the nbest list
# Returns True if the keyword was found; False if not found
def compute_feature_set( nbest_list ):
    # Look at the 1-best result and determine whether the keyword was there at the start
    input_text = nbest_list[0]['text'].replace( "_", " " ).split()
    # set found word to false initially, then search for any instance
    # of keywords
    feature_set = {}
    found_word = False

    keyword_fid = open( keyword_file )

    # check if the keyword was there at the start
    for keyword in keyword_fid.readlines():
        try:
            if input_text[0].strip() == keyword.strip():
                found_word = True
                break 
        except IndexError:
            pass
    keyword_fid.close()

    
    feature_set['found_word'] = found_word
    return feature_set
