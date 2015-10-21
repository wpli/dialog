## Action Manager


##     Given a certain action code from the dialog manager, decides
##     what arguments to send to the appropriate information function
##     This function does not instantiate any of the other classes
##     Instead, it acts as the glue between the action codes and the 
##     rest of the system
##     * functions
##           o self.get_action( action_code ): returns a dictionary
##             containing 'desired_class' (string) and 'arguments' (list) 

import sys
import csv
import re
import datetime
#sys.path.append( '../../tbh_api/src' )
#from tbh_api import *

#==========================================================================
## Append the relevant paths and scripts 
sys.path.append( '../../tbh_info_weather/src/' )
import tbh_info_weather

sys.path.append( '../../tbh_info_activities/src/' )
import tbh_info_activities

sys.path.append( '../../tbh_info_menu/src/' )
import tbh_info_menu

sys.path.append( '../../tbh_info_datetime/src/' )
import tbh_info_datetime

sys.path.append( '../../tbh_skype_interface/src/' )
import tbh_skype_interface


#==========================================================================

import pickle

## 
# Description:
# Dictionary that maps function to the relevant classes
CLASSES_DICT = { 'time' : 'tbh_info_datetime', 
                 'date' : 'tbh_info_datetime',
                 'weather' : 'tbh_info_weather',
                 'activities' : 'tbh_info_activities', 
                 'confirmatory': None,
                 'system' : None,
                 'phone_call' : 'tbh_skype_interface',
                 'voice_synthesizer' : 'tbh_voice_synthesizer',
                 'miscellaneous' : None,
                 'none' : None,
                 'digits' : 'tbh_skype_interface',
                 'menus' : 'tbh_info_menu'
                 }

MEALS_DICT = { 'breakfast': 'Breakfast',
               'breakfast_alt': 'Breakfast Alternative',
               'lunch': 'Lunch',
               'lunch_alt': 'Lunch Alternative',
               'dinner': 'Dinner',
               'dinner_alt': 'Dinner Alternative' 
               }

def get_answer_text( action_code, skype_contacts_dict=None ):
    base_code = action_code[0]
    parameter = action_code[1]
    desired_text = None

    # call function to return a information string
    # this string may be spoken or displayed on teh GUI
    ## 
    # Description:
    # Confirmations
    if parameter[0] == 'request_confirmation':
        desired_text = "I think you requested: %s. Am I correct?" % ( parameter[1:] )




    elif base_code in ( 'time', 'activities', 'menus', \
                  'breakfast', 'lunch', 'dinner', 'weather' ):
        desired_text = get_info_text( action_code )
    elif base_code == 'system':
        desired_text = get_system_text( action_code )
    elif base_code == 'phone':
        desired_text = get_phone_call_text( action_code )



    return desired_text
           
#==========================================================================

def get_call_contact_text( action_code, skype_contacts_dict ):
    base_code = action_code[0]
    parameter = action_code[1][0]
    contacts = tbh_skype_interface.load_skype_contacts()
    output_string = ""
    if base_code == 'call_contact':
        if parameter == 'unknown':
            output_string = "Sorry, I don't know who that is. Exiting phone call mode."
        else:
            output_string = "Now trying to call " + \
                skype_contacts_dict[int(parameter)]['spoken_name'].replace('_', ' ').title() + " (" + \
                skype_contacts_dict[int(parameter)]['skype_contact_id'] + ")."

    return output_string


def get_info_text( action_code ): 
    base_code = action_code[0]
    parameter = action_code[1][0]

    

    ## 
    # Description:
    # Time requests
    if base_code == 'time':
        if parameter == 'time':
            desired_item = tbh_info_datetime.get_current_time()
            output_string = "The current time is %s." \
                % ( desired_item.strftime( "%I:%M %p" ) )
        elif parameter == 'date':
            desired_item = tbh_info_datetime.get_current_date()
            output_string = "Today is %s." \
                % desired_item.strftime( "%A, %B %d, %Y" )              

    ## 
    # Description:
    # Activities requests
    elif base_code == 'activities':
        if base_code == 'activities':
            desired_date = datetime.date.today()
            if parameter == 'today':
                desired_date = datetime.date.today()
            elif parameter == 'tomorrow':
                desired_date = desired_date + datetime.timedelta( days=1 )
            else:
                desired_date = determine_date_from_day_of_week( \
                    parameter )

            desired_item = tbh_info_activities.get_activities_for_day( desired_date )
            if desired_item != None:
                output_string = "Activities for %s:\n" \
                    % ( desired_date.strftime( "%A, %B %d" ) )
                for activity in desired_item:
                    output_string = output_string + "%s: %s.\n" \
                        % ( activity.start_date_time.strftime( "%I:%M" ), \
                            activity.name )
            else:
                output_string = "Activities not available for this date."



        # Other arguments for next activity and activities for other dates
        # should be written here

    ## 
    # Description:
    # Weather requests
    elif base_code == 'weather':

        desired_date = determine_date( parameter )

        if parameter == 'today':
            # return dictionary containing current conditions and
            # today's weather forecast
            desired_item = {}
            desired_item['current_weather'] = tbh_info_weather.get_current_weather()

            desired_item['forecast'] = tbh_info_weather.get_daily_weather( desired_date )
            if desired_item['current_weather'] == None:
                output_string = "Weather information currently not available."
            else:                                           
                output_string = "Currently %s and %s.\nHumidity: %s percent.\nToday's high is %s and today's low is %s.\n" \
                 % ( desired_item['current_weather'].temperature, \
                      desired_item['current_weather'].weather_condition.lower(), \
                      desired_item['current_weather'].humidity, \
                      desired_item['forecast'].high, \
                      desired_item['forecast'].low )


        elif parameter =='tomorrow':
            desired_date = datetime.date.today() + datetime.timedelta( days=1 )

            desired_item = tbh_info_weather.get_daily_weather( desired_date )


            if desired_item != None:
                output_string = "Weather for tomorrow (%s):\n%s\nHigh %s and low %s" % ( \
                    desired_date.strftime( "%A, %B %d" ), \
                    desired_item.weather_condition, \
                    desired_item.high, \
                    desired_item.low )

                            #desired_item.high, \
                            #desired_item.low )

            else:
                output_string = "Weather information not available for tomorrow."

        # Request for one of the days of the week
        elif parameter in ( 'monday', 'tuesday', 'wednesday', 'thursday', \
                                     'friday', 'saturday', 'sunday' ):
            desired_date = determine_date_from_day_of_week( parameter )
            desired_item = tbh_info_weather.get_daily_weather( desired_date )

            if desired_item != None:
                output_string = "Weather for %s:\n%s.\nHigh %s and low %s." % ( \
                    desired_date.strftime( "%A, %B %d" ), \
                    desired_item.weather_condition, \
                    desired_item.high, \
                    desired_item.low )

            else:
                output_string = "Weather information not yet available for %s." % \
                    desired_date.strftime( "%A, %B %d" )


        elif parameter == 'three_day':
            # Get the three-day forecast
            # Returns a list of four current_weather_forecast_t objects
            desired_date = datetime.date.today()

            output_string = "Weather forecast:\n"

            desired_item = []
            for i in range(0,4):
                date = desired_date + datetime.timedelta( days=i )               
                weather_forecast_item = tbh_info_weather.get_daily_weather( date ) 
                print weather_forecast_item.weather_condition, weather_forecast_item.high, weather_forecast_item.low
                desired_item.append( weather_forecast_item )
                output_string = output_string + \
                    "%s: %s. High %s and low %s\n" % ( \
                    date.strftime( "%A, %B %d" ), \
                    weather_forecast_item.weather_condition.lower().capitalize(), \
                    weather_forecast_item.high, \
                    weather_forecast_item.low )




    ## 
    # Description:
    # Menu requests
    elif base_code in ( 'menus', 'breakfast', 'lunch', 'dinner' ):
        if base_code == 'menus':

            desired_date = determine_date( parameter )

            desired_item = tbh_info_menu.get_all_menus( desired_date )


            output_meal_dict = {}

            output_string = "Menu for %s\n" % \
                desired_date.strftime( "%A, %B, %d" )

            for meal in ( 'breakfast', 'breakfast_alt', 'lunch', 'lunch_alt', 
                          'dinner', 'dinner_alt' ):
                if meal in desired_item.keys():
                    output_meal_dict[meal] = desired_item[meal].food_list
                else:
                    output_meal_dict[meal] = "Information not available."

                output_string = output_string + MEALS_DICT[meal] + ": " + \
                    output_meal_dict[meal] + "\n"                 

        elif base_code in ( 'breakfast', 'lunch', 'dinner' ):
            desired_meal = base_code
            desired_date = determine_date( parameter )
            output_meal_dict = {}
            main_meal = tbh_info_menu.get_menu( desired_date, desired_meal ) 
            alternative_meal = tbh_info_menu.get_menu( desired_date, desired_meal + \
                                             '_alt' )
            output_meal_dict[desired_meal] = main_meal
            output_meal_dict[desired_meal + '_alt'] = alternative_meal

            output_string = "%s for %s:\n%s\nAlternative: %s" % \
                ( MEALS_DICT[desired_meal], \
                      desired_date.strftime( "%A, %B %d" ), \
                      main_meal.food_list, \
                      alternative_meal.food_list
                  )





    return output_string
        
#=================================================================================
##
# Description:
# Get answer text for system functions
def get_system_text( action_code ):
    parameter = action_code[1][0]

    if parameter == 'wake_up':
        output_string = "Ready to answer questions."
    elif parameter == 'go_to_sleep':
        output_string = "Sleeping."
    elif parameter == 'enter_attentive_mode':
        output_string = "Entering attentive mode: No keyword needed."
    elif parameter == 'exit_attentive_mode':
        output_string = "Exiting attentive mode. " + \
            "Please use a keyword before speaking." 
    else:
        output_string = None

    return output_string
        
#=================================================================================
##
# Description:
# Get answer text for phone_call functions
def get_phone_call_text( action_code, skype_contacts_dict=None ):
    parameter = action_code[1][0]

    if parameter == 'make_phone_call':
        output_string = "Whom do you wish to call?"
    elif parameter == 'show_contacts':
        contacts = skype_contacts_dict

        output_string = ""
        list_of_just_names = []
        contacts_by_skype_contact_id_dict = {}

        for index, entry in contacts.items():
            # eliminate aliasing of names (in case some numbers have
            # more than one entry because it is possible to call the
            # same number with a different contact name)
            contacts_by_skype_contact_id_dict[ entry['spoken_name'] ] = entry['skype_contact_id']              
            list_of_just_names.append( entry['spoken_name'] )

            list_of_just_names.sort()

        output_list = []
        for contact_name in list_of_just_names:
            readable_contact_id = contacts_by_skype_contact_id_dict[contact_name]
            if readable_contact_id[0] == '+':
                readable_contact_id_list = list( readable_contact_id ) 
                readable_contact_id_list.insert( 2 , '-' )
                readable_contact_id_list.insert( 6 , '-' )
                readable_contact_id_list.insert( 10 , '-' )
                readable_contact_id = "".join( readable_contact_id_list )
            else:
                pass

            output_list.append( contact_name.title() + ": " + readable_contact_id + "\n" )

            if len( output_list ) > 6:
                current_output_list = output_list[0:6]
                future_output_list = output_list[6:]
                f = open( 'phone_list.pkl', 'w' )
                pickle.dump( future_output_list, f )
                f.close()
        for entry in current_output_list:
            output_string = output_string + entry

        
        # The title() command seems to capitalize after apostrophes,
        # which is undesirable
        output_string = output_string.replace( "'S", "'s" )
        output_string = output_string.replace( "_", " " )


    elif parameter == 'next_page':
        try:
            f = open( 'phone_list.pkl', 'r' )
            output_list = pickle.load( f )
            f.close()
        except:
            output_list = []

        current_output_list = output_list[0:6]
        future_output_list = output_list[6:]

        output_string = ""
        for entry in current_output_list:
            output_string = output_string + entry
        
        # The title() command seems to capitalize after apostrophes,
        # which is undesirable
        output_string = output_string.replace( "'S", "'s" )
        output_string = output_string.replace( "_", " " )
        
        if len(future_output_list) == 0:
            output_string = output_string + "End of Contacts\n"
        else:
            pass

        f = open( 'phone_list.pkl', 'w' )
        pickle.dump( future_output_list, f )
        f.close()


    elif parameter == 'answer_phone':
        output_string = "Answering phone call."

    elif parameter == 'hang_up':
        output_string = "Ending phone call."

    elif parameter == "hold_call":
        output_string = "Phone call on hold."

    elif parameter == "resume_call":
        output_string = "Phone call resumed."

    elif parameter == "execute_phone_call":
        output_string = "Now calling."

    elif parameter == "enter_voice_dial":
        output_string = "Say the phone number you wish to dial\n" + \
        "You can also say 'start over', 'finished', or 'back'."

    else:
        output_string = None 

    return output_string


      


def determine_date( date_word ):
    if date_word == 'today':
        desired_date = datetime.date.today()
    elif date_word == 'tomorrow':
        desired_date = datetime.date.today() + datetime.timedelta( days=1 )
    else:
        # Other possibilities should be a day of the week
        # If not, use today's date
        try: 
            desired_date = determine_date_from_day_of_week( date_word )
        except:
            desired_date = datetime.datetime.today()

    return desired_date



## Description
# Determines the next date (today or in the future) for a given day of week
def determine_date_from_day_of_week( day_of_week ):
    day_order = ['monday', 'tuesday', 'wednesday', 'thursday', 
                 'friday', 'saturday', 'sunday']
    
    # 0 is Monday, 6 is Sunday
    today_code = datetime.date.today().weekday()
    desired_day_code = day_order.index( day_of_week )

    if desired_day_code >= today_code:
        days_to_add = desired_day_code - today_code
    else:
        days_to_add = 7 + desired_day_code - today_code

    timedelta_days = datetime.timedelta( days=days_to_add )     

    return datetime.date.today() + timedelta_days

if __name__ == "__main__":
    answer_manager = tbh_answer_text_manager_t()
    #for item in range(1,90):
    #    print "Code:", item
    #    print answer_manager.get_answer_text(item)







