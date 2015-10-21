##
# Description:
# Accepts a csv file and returns a dictionary 
# with contact names, phone numbers, and extensions
def load_skype_contacts( contacts_file=DEFAULT_CONTACTS_FILE ):

    datafile = open( contacts_file, 'r' )
        
    contact_names_dict = dict()
    

    for line in datafile.readlines():

        items = line.split(',')
        if items[0] != '\n':
            code = int( items[0] )
            spoken_name = items[1]
            skype_contact_name = items[2]
            if items[2] != '':
                extension = items[3]
            else:
                extension = None

            wait_time = items[3].strip()
            if items[3] != '':
                #Do not modify the wait_time variable
                pass
            else:
                wait_time = None

            skype_contact_name = skype_contact_name.rsplit('\n')[0]
            # skype_contact_id is either a Skype username or a ten-digit
            # number (with a '+' prefix)
            contact_names_dict[ code ] = { 'spoken_name': spoken_name,
                                           'skype_contact_id': 
                                                       skype_contact_name,
                                                       'extension': 
                                                       extension,
                                                       'wait_time':
                                                       wait_time
                                                       }
    
    return contact_names_dict
