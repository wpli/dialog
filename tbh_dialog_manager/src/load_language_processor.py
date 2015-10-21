'''
Created on Oct 14, 2010

@author: william
'''

import csv
import sys

    
def load_action_file( file_name ):
    action_file = csv.reader( open( file_name, 'rb' ), delimiter='\t', quotechar='"' )
    
    action_list = []
        
    for row in action_file:    
        #add a new list to the action_list
        if row[0] != '':
            action_list.append( [] )
            for item in row:
                if item != '':
                    action_list[-1].append( item )

    
    
    return action_list 

















if __name__ == '__main__':
    file_name = sys.argv[1]
    print "Loading", file_name
    action_list = load_action_file( file_name )
    
    #for row in action_file:
        #print "; ".join(row)
        

    for row in action_list:
        print row
        
    
    
    
