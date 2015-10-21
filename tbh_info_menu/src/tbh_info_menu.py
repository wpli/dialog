## Menu Information

##     * functions:
##           o get_all_menus( day ) --> returns all three meals
##           o get_menu( day , meal ) --> returns meal on specified date
##           o get_next_menu( date_time ) --> returns next meal

import sys
import datetime

sys.path.append( "../../tbh_api/src" )
from tbh_api import *

###Should be taken out eventually###
sys.path.append( "../../tbh_google_login/src" )
from tbh_google_login import *
#######################


#=========================================================================
##
# Description
# Time of breakfast
BREAKFAST = datetime.time( 8, 30 )

## 
# Description
# Time of lunch
LUNCH = datetime.time( 12, 0 )

## 
# Description
# Time of dinner
DINNER = datetime.time( 17, 30 )

## Description
# List of menus
MENU_TUPLE = ( 'breakfast', 'breakfast_alt', 'lunch', 'lunch_alt', \
                  'dinner', 'dinner_alt' )
#=========================================================================
##
# Description: 
# Menu object
# This represents the menu for a single meal
@tbh_api_callable_class
class tbh_menu_t( object ):
    ##
    # Description:
    # datetime object with date of meal
    date = None

    ##
    # Description:
    # string that contains one of MENU_TUPLE
    type_of_meal = None
  
    ##
    # Description:
    # List of items for meal
    food_list = None
           
    ##
    # Description:
    # Creates a new tbh_activity_t object with a given 
    # date, type_of_meal, main_meal, and alternative_meal
    @tbh_api_callable_method
    def __init__( self, date=None, type_of_meal=None, food_list=None ):
        self.date = date
        self.type_of_meal = type_of_meal
        self.food_list = food_list


#=========================================================================
##
# Description: 
# Gets all three meals on a certain date
# Returns a tbh_menu_t object
def get_all_menus( date ):

    
    date_google_format = date.strftime( "%Y-%m-%d" )
  


    tbh_menus = _get_menus_from_google( date_google_format )
  


    return tbh_menus
    
#=========================================================================
##
# Description: 
# Gets all three meals from Google for a given date
# Returns a dictionary with three tbh_menu_t objects
def _get_menus_from_google( date ):
    calendar_service = connect_to_google_calendar()
    #since we need a time interval, determine the next day
    target_date_datetime = datetime.datetime.strptime( date, '%Y-%m-%d' )
    next_day_datetime = target_date_datetime + datetime.timedelta( days=1 ) 
    next_day = next_day_datetime.strftime( "%Y-%m-%d" )


    #query Google Calendar to get the menu information
    calendar_code_dict = { "breakfast":
                               "68b5u9s68tnkam1je4n86ito1c@group.calendar.google.com",
                           "lunch": 
                               "18efposk6s9m5rmpt5u6diics8@group.calendar.google.com",
                           "dinner":
                               "ugjvpulg1s41qrgb84r5pgbl80@group.calendar.google.com" }

    meals_dict = {}
    try: 
        for meal, meal_code in calendar_code_dict.items(): 
            # obtain the events from the given day
            # there should be two events: meal and meal + "_alt"
            new_set = {}
            query = gdata.calendar.service.CalendarEventQuery( meal_code, 'private', 'full' )
            query.start_min = date
            query.start_max = next_day
            query.max_results = 500
            query._SetSingleEvents('true')
            query._SetOrderBy('starttime')
            query._SetSortOrder('ascending')
            feed = calendar_service.CalendarQuery(query)
        

    
            for an_event in feed.entry:
                tbh_menu = tbh_menu_t() 
                tbh_menu.date = target_date_datetime.date()
                if 'Alt' in an_event.title.text:
                    e = an_event.title.text.split(':')
                    tbh_menu.type_of_meal = meal + "_alt"
                    tbh_menu.food_list = e[1]

                    meals_dict[meal+"_alt"] = tbh_menu

                else:

                    tbh_menu.type_of_meal = meal
                    tbh_menu.food_list = an_event.title.text
                    meals_dict[meal] = tbh_menu



    except:
        meals_dict = None



    return meals_dict

#=========================================================================
##
# Description: 
# Gets a specific meal on the given date
# Returns tbh_menu_t object with meal
def get_menu( date, meal ):
    tbh_menu = None

    if meal in MENU_TUPLE:       
        all_menus = get_all_menus( date ) 
        if meal in all_menus.keys():            
            return all_menus[meal]
        else:
            return tbh_menu
    else:
        return tbh_menu
    
#=========================================================================
##
# Description: 
# Gets the next meal based on the current time and the start time of the 
# next meal
# Returns list with two tbh_menu_t objects corresponding to main and 
# alternative meals
def get_next_menu( date_time ):
    current_time = date_time.time()
    desired_date_time = date_time
    #determine next meal

    if current_time > BREAKFAST and current_time <= LUNCH:
        next_meal = 'lunch'
    elif current_time > LUNCH and current_time <= DINNER:
        next_meal = 'dinner'
    else:
        next_meal = 'breakfast'
        if date_time.time() >= datetime.time( 0, 0 ):
            pass
        else:
            desired_date_time = date_time + datetime.timedelta( days=1 )

    next_meal_main = get_menu( desired_date_time.date(), next_meal )
    next_meal_alternative = get_menu( desired_date_time.date(), next_meal + "_alt" )
    
    meals = [ next_meal_main, next_meal_alternative ] 

    return meals
                                     



#=========================================================================
##
# Description: 
# Unit test function
if __name__ == '__main__':
    
    #print "Menus on December 26, 2010:"
    dec26_menus = get_all_menus( datetime.date(2011, 03, 23) )
    
    
    for meal, menu in dec26_menus.items():
        print "%s: %s" % ( meal, menu.food_list )


    print "\nAlternative lunch on December 6, 2010:"
    dec6_lunch = get_menu( datetime.date( 2011, 03, 24 ), 'lunch' )
    print dec6_lunch.food_list

    print "\nNext meal:"
    #next_meal = get_next_menu( datetime.datetime.now() )
    next_meal = get_next_menu( datetime.datetime( 2011, 03, 25, 0, 0 ) )
    for item in next_meal:
        if item != None:
            print "%s on %s: %s" % (item.type_of_meal, item.date, item.food_list )
        else:
            print "Menu not available for this date."


            






















