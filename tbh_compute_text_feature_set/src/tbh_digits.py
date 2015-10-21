# file where the key words/phrases are stored: each line contains
# phrase_type: "phrase1" "phrase2" "phrase3"; if any of the phrases appear,
# then phrase_type = True, else phrase_type = False
keyword_file = "../../tbh_compute_text_feature_set/src/tbh_digits.txt"

##
# Description: 
# Look for a relevant word (i.e. chair) anywhere in the first line of
# the nbest list

# finale! change to take in phrase type list
def compute_feature_set( nbest_list ):
    input_text = nbest_list[0]['text'].replace( "_", " " ).split()
    features_fid = open( keyword_file )
    feature_set = {}
    digits_dict = { 'one': '1',
                        'two': '2', 
                        'three':'3' , 
                        'four': '4', 
                        'five': '5', 
                        'six': '6', 
                        'seven': '7',
                        'eight': '8',
                        'nine': '9',
                        'zero': '0',
                        'oh': '0' }
    for feature in features_fid.readlines():
        if feature.strip() == 'digits_detected':
            # look for a list of digits
            # go through each word and verify that it is a digit
            feature_set[ 'digits_detected' ] = True
            for word in input_text:
                if word not in digits_dict.keys():
                    feature_set['digits_detected'] = False

        if feature.strip() == 'digits':
            if feature_set['digits_detected']:
                digits_string = ''
                for digit in input_text:
                    digits_string += digits_dict[digit]
                feature_set['digits'] = digits_string
            else: 
                feature_set['digits'] = None

    return feature_set
