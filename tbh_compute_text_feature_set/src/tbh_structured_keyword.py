# file where the key words/phrases are stored: each line contains
# phrase_type: "phrase1" "phrase2" "phrase3"; if any of the phrases appear,
# then phrase_type = True, else phrase_type = False
keyword_file = "../../tbh_compute_text_feature_set/src/tbh_structured_keyword.txt"

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
        else:
            keywords.append(eval(keyword))
    keyword_fid.close()
    return keywords

#returns a more structured list - broken up in to actions and properties - not a true false type 
def compute_feature_set( nbest_list ):
    input_text = nbest_list[0]['text'].replace( "_", " " ).replace( "'s", " " )#.split()
    #keyword_fid = open( keyword_file )
    feature_set = {}
    
    keywords = load_keywords()

    print keywords

    feature_set['action'] = []
    feature_set['property'] = []
    
    input_set = set(input_text.split())
    
    for keyword in keywords:
        try:
            #feature_set[ keyword['label'] ] = False
            for i in keyword['phrases']:
                #checks if all words in the phrases column are present in the phrase 
                #might need a different solution if wwe want to match consequtively
                if(set(i.split()).intersection(input_set) == set(i.split())):
                    #print "Found " , i, input_text
                    if feature_set.has_key(keyword['type']):
                        feature_set[keyword['type']].append(keyword['label'])
                    else:
                        feature_set[keyword['type']] = [keyword['label']]
        except IndexError:
            #feature_set[ keyword.strip() ] = False
            print "Index Error : nbest list parser"
    
    #if there are keywords that are sub words of a larger keyword - take them out

    matched_keywords = feature_set['property']
    filtered_keywords = []

    print "Matched Keywords"
    print matched_keywords

    if(len(matched_keywords) > 1):
        for i in matched_keywords:
            for j in matched_keywords:
                if i == j:
                    continue
                i_set = set(i.replace( "_", " " ).split())
                j_set = set(j.replace( "_", " " ).split())
                if(i_set.intersection(j_set) == i_set or j_set.intersection(i_set) == j_set):
                    if(len(i_set) < len(j_set)):
                        print "Found subset keyword"
                    else:
                        filtered_keywords.append(i)
                else:
                    filtered_keywords.append(i)
                
        feature_set['property'] = filtered_keywords

    else:
       filtered_keywords = matched_keywords

    print "Filtered Keywords"
    print filtered_keywords
    
    return feature_set
