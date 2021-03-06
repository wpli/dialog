# This module should be the ONLY interface to action_code_set.txt, DO
# NOT modify the file directly!
action_code_file = "../../dialog_system_tools/bin/20120118/decision_process_files/observations.txt"

##
# Description:
# Checks if the action code is in the file already
def verify_action_code( action_code ):
    existing_code = False

    action_base = action_code[0]
    action_parameter_list = action_code[1]
    action_parameter_string = ''
    for action_parameter in action_parameter_list:
        action_parameter_string = str( action_parameter_string ) + \
        ' ' + str( action_parameter )
    action_parameter_string = action_parameter_string[1:]
    f = open( action_code_file )
    for line in f.readlines():
        split_line = line.split(' ')
        if ( action_base == split_line[0].strip() ) and ( action_parameter_string == split_line[1].strip() ):
            existing_code = True
    f.close()
    return existing_code

##
# Description:
# Adds action code to the file
def add_action_code( action_code ):
    action_base = action_code[0]
    action_parameter_list = action_code[1]
    if ' ' in action_base:
        raise NameError("Don't use spaces in action base")
    for action_parameter in action_parameter_list:
        if ' ' in action_parameter:
            raise NameError("Don't use spaces in action parameter")
    
    # actually add
    print 'Added New Code' , action_base , action_parameter_list
    f = open( action_code_file , 'a' )
    f.write( action_base ) 
    for action_parameter in action_parameter_list:
        f.write( ' ' + action_parameter )
    f.write( '\n' )
    f.close()

def get_action_code_number_list():
    action_code_list = []
    f = open( action_code_file )
    for line in f.readlines():
        split_line = line.strip().split(' ')
        action_code_list.append( split_line )    
    f.close()
    return action_code_list

def get_number_action_code( action_code_list, action_code ):
    #print action_code

    return action_code_list.index( action_code )
    """
    try:
        return action_code_list.index( action_code )
    except:
        error_code = "Could not find this observation code", action_code
        raise Exception( error_code )
    """

    '''
    flattened_list = []

    for item in action_code:
        if hasattr( item, '__iter__' ):
            for subitem in item:
                flattened_list.append( subitem )
        else:
            flattened_list.append( item )

    try: 
        return action_code_list.index( flattened_list )
    except ValueError:
        raise Exception('Could not find this action code')
    '''

if __name__ == '__main__':
    action_code_list = get_action_code_number_list()
    print get_number_action_code( action_code_list, [ 'null', 'yes_record' ] )
    print get_number_action_code( action_code_list, [ 'confirmatory', 'yes' ] )
