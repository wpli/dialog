# file where the key words/phrases are stored: each line contains
# phrase_type: "phrase1" "phrase2" "phrase3"; if any of the phrases appear,
# then phrase_type = True, else phrase_type = False
keyword_file = "../../tbh_compute_text_feature_set/src/tbh_mapped_keyword.txt"

##
# Description: 
# Look for a relevant word (i.e. chair) anywhere in the first line of
# the nbest list

def load_keywords():
    keyword_fid = open( keyword_file )
    keywords = []
    for line in keyword_fid.readlines():
        keyword = line.strip()
        if(keyword.find('//')==0):
            continue
        elif(len(keyword)==0):
            break
        else:
            keywords.append(eval(keyword))

    keyword_fid.close()
    return keywords

# finale! change to take in phrase type list
def compute_feature_set( nbest_list ):
    input_text = nbest_list[0]['text'].replace( "_", " " ).replace( "'s", " " )#.split()
    #keyword_fid = open( keyword_file )
    feature_set = {}
    keywords= []
    keywords = load_keywords()

    for keyword in keywords:
        try:
            feature_set[ keyword['label'] ] = False
            for i in keyword['phrases']:
                '''if input_text.find(i.strip())>=0:
                    print "Found " , i, input_text
                    print "Found"
                    feature_set[keyword['label']] = True'''
                if(set(i.split()).intersection(set(input_text.split())) == set(i.split())):
                    #print "Found " , i, input_text
                    feature_set[keyword['label']] = True
        except IndexError:
            feature_set[ keyword.strip() ] = False
    
    return feature_set
