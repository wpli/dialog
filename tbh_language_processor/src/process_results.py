'''
Created on Oct 14, 2010

@author: william
'''

#import csv
import sys
from load_language_processor import load_action_file
import re


def find_action( statement, action_list ):  
    candidate_action_codes = []
 
    for possible_action in action_list:
        #"keywords" is a list of at least length 1        
        keywords = possible_action[3:]
        for possible_keyword in keywords:
            if ',' in possible_keyword:
                possible_keyword_list = possible_keyword.split(', ')
                for keyword in possible_keyword_list:
                    possible_keywords_found = True
                    if string_find( statement, keyword ):
                        pass
                    else:
                        possible_keywords_found = False
                        break

                if possible_keywords_found:
                    candidate_action_codes.append( [ possible_action[0], possible_keyword ] )

                        
            else:
                if string_find( statement, possible_keyword ):
                    candidate_action_codes.append( [ possible_action[0], possible_keyword ] )


    #pick the action code for which the most keywords matches
    if len( candidate_action_codes ) == 0:
        action_code = 0
    elif len( candidate_action_codes ) == 1:
        action_code = int( candidate_action_codes[0][0] )
    else:
        most_keywords_matched = 0
        for entry in candidate_action_codes:
            keywords_matched = len( entry[1].split( ', ' ) )
            if keywords_matched > most_keywords_matched:
                most_keywords_matched = keywords_matched
                action_code = int( entry[0] )
            
    

    return action_code


def string_find( statement, query_string ): 
     

    
    string_found = False

    temp_statement = repr( statement )
    raw_statement_string = temp_statement[1:-1]

    temp_query_string = repr( query_string )
    raw_query_string = temp_query_string[1:-1]

    

    if re.search(r'\b' + raw_query_string + r'\b', raw_statement_string):
        string_found = True  

        
    return string_found



            


if __name__ == '__main__':
    action_file_name = sys.argv[1]
    print "Loading", action_file_name
    action_list = load_action_file( action_file_name )
    print action_list          

    transcript_file_name = sys.argv[2]
    transcript_file = open( transcript_file_name, 'rb' )
    transcript_list = transcript_file.readlines()
    transcript_file.close()
    
    for index, item in enumerate( transcript_list ):
        if item == '\n':
            del transcript_list[index]
        else:
            transcript_list[index] = item.split( '\n' )[0]

    #Now, the transcript_list only contains the transcripts
    #Create a corresponding list of items containing the code


    transcript_codes = []

    for item in transcript_list:
        action_code = find_action ( item, action_list )
        transcript_codes.append( action_code )

    code_file = open( transcript_file_name + '.code', 'wb' )
    
    for item in transcript_codes:
        code_file.write( str( item ) + '\n' )
    
    code_file.close()


    









 

    
    
