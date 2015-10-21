import sys

sys.path.append( '../../tbh_skype_interface/src/' )
import tbh_skype_interface

EC_VOCAB_LIST = '../../tbh_compute_text_feature_set/src/tbh_environmental_control_keyword.txt'

def read_contacts_text_file( contacts_text ):
    contacts_dict = tbh_skype_interface.load_skype_contacts( contacts_text )
    return contacts_dict


def create_grammar( skype_contacts_dict ):
    print "#JSGF V1.0;"
    print "grammar call_contact;"
    grammar_string = "public <command> = ( [ computer | chair | wheelchair ] ( (call <contact_name>) | cancel | exit | never_mind | dial_a_number | dial_number | show_phone_list | show_contacts | next_page | maximize_video | minimize_video | good_day | wake_up | full_screen_video | hold_call | resume_call | end_call | put_call_on_hold | hang_up | go_to_sleep | yes | no"
    
    f = open( EC_VOCAB_LIST, 'r' )
    ec_vocab_list = f.readlines()
    for item in ec_vocab_list:
        
        grammar_string = grammar_string + " | " + item.strip()


    grammar_string = grammar_string + " ) );"


    print grammar_string
    vocab_list = []
    for word in [ 'cancel', 'exit', 'never_mind', 'dial_a_number', 'dial_number', 'show_phone_list', 'show_contacts', 'next_page', 'yes', 'no' ]:
        vocab_list.append( word )

    number_list = [ "one", "two", "three", 
                    "four", "five", "six", 
                    "seven", "eight", "nine", 
                    "ten", "eleven", "twelve", 
                    "thirteen", "fourteen", "fifteen", 
                    "sixteen", "seventeen", "eighteen", 
                    "nineteen", "twenty" ]

    for number in number_list:
        vocab_list.append( number )

    vocab_list.append( 'contact' )
    vocab_list.append( 'number' )

    contact_string = "<contact_name> = [contact] [number] "
    contact_string += "( "
    for entry in number_list:
        contact_string += entry + " |\n "

    for contact in skype_contacts_dict:
        contact_string += skype_contacts_dict[contact]['spoken_name'] + " |\n "
        vocab_list.append( skype_contacts_dict[contact]['spoken_name'] )

    contact_string += "cancel );"


    print contact_string 


    f = open( sys.argv[1] + '.vocab', 'w' )
    for item in vocab_list:
        #print item
        f.write( item + '\n' )
    f.close()

    g = open( sys.argv[1] + '.contacts', 'w' )
    for item in number_list:
        g.write( item + '\n' )
    
    for contact in skype_contacts_dict:
        g.write( skype_contacts_dict[contact]['spoken_name'] + '\n' )

    g.close()
        
    #for item in skype_contacts_dict:
    #    print item, skype_contacts_dict[item]['spoken_name']

if __name__ == '__main__':
    contacts_text = sys.argv[1]
    contacts_dict = read_contacts_text_file( contacts_text )

    create_grammar( contacts_dict )
