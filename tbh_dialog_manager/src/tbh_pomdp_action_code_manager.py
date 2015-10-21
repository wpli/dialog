# This module should be the ONLY interface to action_code_set.txt, DO
# NOT modify the file directly!
action_code_file = "../../tbh_dialog_manager/src/action_code_set_pomdp.txt"

##
# Description:
# Checks if the action code is in the file already
def verify_action_code( action_code ):
    existing_code = False
    action_base = action_code[0]
    action_parameter_list = action_code[1]
    action_parameter_string = ''
    for action_parameter in action_parameter_list:
        action_parameter_string = action_parameter_string + ' ' + action_parameter
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

def get_pomdp_action_code_number_list():
    action_code_list = []

    f = open( action_code_file )
    for line in f.readlines():
        split_line = line.strip().split(' ')
        action_code_list.append( [ split_line[0], split_line[1:] ] )
    
    f.close()

    return action_code_list

def get_number_action_code( action_code_list, action_code ):
    try: 
        return action_code_list.index( action_code )
    except ValueError:
        error_code = 'Could not find this action_code', action_code
        raise Exception( error_code )

if __name__ == '__main__':
    action_code_list = get_pomdp_action_code_number_list()
    print get_number_action_code( action_code_list, [ 'request_confirmation', 'time', 'time' ] )
