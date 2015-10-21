## Datetime Information

##     * functions:
##           o get_current_time: returns datetime.time object
##           o get_current_date: returns datetime.date object
##           o get_current_datetime: returns datetime.datetime object


import sys
import datetime

sys.path.append( "../../tbh_api/src" )
from tbh_api import *

#=========================================================================

##
# Description: 
# Weather object 
# This represents the weather on a day
@tbh_api_callable_class
class date_time_t( object ):

    ##
    # Description:
    # Creates a datetime object
    # weather_condition, high, and low
    @tbh_api_callable_method
    def __init__( self, date_time=None ):
        ##
        # Description:
        # datetime object
        self.date_time = date_time

@tbh_api_callable     
def get_current_datetime():
    date_time = date_time_t()
    date_time.date_time = datetime.datetime.now()
    return date_time.date_time

@tbh_api_callable
def get_current_date():
    return get_current_datetime().date()
    
@tbh_api_callable
def get_current_time():
    return get_current_datetime().time()


#=========================================================================

                                         




if __name__ == "__main__":      
    print "datetime: %s" % get_current_datetime()
    print "date: %s" % get_current_date()
    print "time: %s" % get_current_time()

