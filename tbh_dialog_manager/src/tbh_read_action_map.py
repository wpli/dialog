import csv

#==========================================================================

## 
# Description:
# Name of the file that contains the keyword to actions map
ACTION_CODES = '../../tbh_action_map/src/actions.csv'


#==========================================================================

## 
# Description: 
# Obtains the map between speech (certain keywords) and actions
# Input a CSV file with the following headings
# "rank", "category", "action", "keywords"
# The last heading may have multiple columns (as many as needed)
# corresponding to the keywords that would trigger that action
def build_speech_to_action_map( file_name=ACTION_CODES ):
    # possessive form of these words may also be uttered and recognized
    possessive_words = [ 'today', 'tomorrow', 'monday', 'tuesday',
        'wednesday', 'thursday', 'friday', 'saturday', 'sunday', 'week' ]

    action_file = csv.reader( open( file_name, 'rb' ), delimiter='\t', quotechar='"' )
    action_list = []

    for row in action_file:
        #add a new list to the action_list                                                                                                                             
        if row[0] != '':
            action_list.append( [] )
            for item in row:
                if item != '':
                    action_list[-1].append( item )
                    for word in possessive_words:
                        if word in item:
                            new_item = item.replace( word, word + "'s" )
                            action_list[-1].append( new_item )


                        
    # create a dictionary from this list
    action_dict = {}
    for listing in action_list:
        action_dict[ int( listing[0] ) ] = { 'category': listing[1],
                                             'action': listing[2],
                                             'confirmation_predicate': \
                                                 listing[3],
                                             'keyword_sets': listing[4:] }

    # add action 0 when there are no keywords that match
    action_dict[ 0 ] = { 'category': 'none', 'action': 'none', 'keyword_sets': [] }

    return action_dict


#==========================================================================
