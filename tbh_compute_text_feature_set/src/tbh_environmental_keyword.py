# file where the key words/phrases are stored: each line contains
# phrase_type: "phrase1" "phrase2" "phrase3"; if any of the phrases appear,
# then phrase_type = True, else phrase_type = False
keyword_sequence_file = "../../tbh_compute_text_feature_set/src/tbh_environmental_keyword.txt"

##
# Description: 
# Look for a relevant word (i.e. chair) anywhere in the first line of
# the nbest list

# finale! change to take in phrase type list
def compute_feature_set( nbest_list ):
    # Do not split the text because the ordering of words matters
    input_text = nbest_list[0]['text'].replace( "_", " " )
    keyword_fid = open( keyword_sequence_file )
    feature_set = {}
    for keyword in keyword_fid.readlines():
        keyword_sequence = keyword.replace( "_", " " )
        try:
            if keyword_sequence.strip() in input_text:
                feature_set[ keyword.strip() ] = True
            else:
                feature_set[ keyword.strip() ] = False
        except IndexError:
            feature_set[ keyword.strip() ] = False
    keyword_fid.close()
    return feature_set
