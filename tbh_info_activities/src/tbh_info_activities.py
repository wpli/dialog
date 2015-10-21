## Activities Information

##     * functions:
##           o get_activities( time_range ) --> returns list of activities
##           o get_activities_for_day( day )
##           o find_next_activity_of_type( activity_type, start_day, start_time ) --> returns a single activity

import sys
import gdata.calendar.service
import gdata.service
import atom.service
import gdata.calendar
import atom
import getopt
import sys
import string
import time
import datetime

###Should be taken out eventually###
sys.path.append( "../../tbh_google_login/src" )
from tbh_google_login import *

#######################



sys.path.append( "../../tbh_api/src" )
from tbh_api import *

#=========================================================================

##
# Description: 
# activity object 
# This represents a single activity
@tbh_api_callable_class
class tbh_activity_t( object ):
    ##
    # Description:
    # datetime object with start date and time of this activity
    start_date_time = None

    ##
    # Description:
    # endtime object with end date and time of this activity
    # We will assume length of activity to be the duration reflected
    # in the Google Calendar
    end_date_time = None 
  
    ##
    # Description:
    # Name of activity
    name = None
    
    ##
    # Description:
    # Location of activity
    # Note: We currently do not have the location information;
    # it is not provided by staff
    location = None
           
    ##
    # Description:
    # Creates a new tbh_activity_t object with a given 
    # date_time, name, location, and duration
    @tbh_api_callable_method
    def __init__( self, start_date_time=None, end_date_time=None, name=None, \
                      location=None ):
        self.start_date_time = start_date_time
        self.end_date_time = end_date_time
        self.name = name
        self.location = location

#=========================================================================
##
# Description:
# Gets the activities for a given time period (start time and end time)
# Returns as a list
# Returns an empty list if there are no activities
# Input variables are of type datetime.datetime and datetime.datetime
# class datetime.datetime(year, month, day[, hour[, minute[, second[, \
# microsecond[, tzinfo]]]]])

def get_activities( start_time, end_time ) :
    #Initialize the connection to the Google account
    #Note that we can only specify the intervals to the Google API
    #at midnight boundary times
    #Therefore, we need to specify an additional day 
    #and remove times at the start and the end

    start_time_google_format = start_time.strftime( "%Y-%m-%d" )
    end_time_with_extra_day = end_time + datetime.timedelta( days=1 )
    end_time_google_format = end_time_with_extra_day.strftime( "%Y-%m-%d" )


    activities_list = _get_activities_from_google( \
        start_time_google_format, end_time_google_format )


    #Prune the activities before the specified start_time or 
    #after the specified end_time
    #For pre-period activities, start from the beginning of the list
    #and remove items as needed
    #For post-period activities, start from the end of the list and
    #remove items as needed
    

    try:
        while activities_list[0].start_date_time < start_time:
            del activities_list[0]

        while activities_list[-1].start_date_time > end_time:
            del activities_list[-1]

    except IndexError:
        activities_list = []



    return activities_list

#=========================================================================
##
# Description:
# Gets the activities for a certain day (midnight to midnight)
# Returns as a list
# Input variable is of type datetime.date
# class datetime.date(year, month, day)
def get_activities_for_day( day ):
    #use get_activities() function and convert to a 24 period
    day_start = datetime.datetime.combine( day, datetime.time() )
    day_end = day_start + datetime.timedelta( days=1 )

    return get_activities( day_start, day_end )

#=========================================================================
##
# Description:
# Gets the activities for a given time period (start time and end time)
# Look over a 72 hour period to limit the time of the search in the event
# of no activities
# Returns a single activity object
def get_next_activity():
    next_activity = None
    now = datetime.datetime.now()
    activities_list = get_activities( now, now + \
                                      datetime.timedelta( days=3 ) )

    if len( activities_list ) > 0: 
        next_activity = activities_list[0]
    else:
        pass
                                    

    return next_activity

#=========================================================================
##
# Description:
# Gets activity schedule from Google based on start and end time
# Returns a list of tbh_activity_t objects
    
def _get_activities_from_google( start_date, end_date ):
    calendar_service = connect_to_google_calendar()
    query = gdata.calendar.service.CalendarEventQuery('a8n4snfcpgln28vuc4isda7ae8@group.calendar.google.com','private','full')
    query.start_min = start_date
    query.start_max = end_date
    query.max_results = 1000
    query._SetSingleEvents('true')
    query._SetOrderBy('starttime')
    query._SetSortOrder('ascending')
    #query._SetSingleEvents(True)
    feed = calendar_service.CalendarQuery(query)

    #instantiate a list that will contain activities

    activities_list = []
    count = 0
    for i, an_event in enumerate(feed.entry):
        #instantiate a tbh_activity_t class
        activities_list.append( tbh_activity_t() )

        activities_list[-1].name = an_event.title.text

        raw_start_date_time = an_event.when[0].start_time.split('T')
        raw_end_date_time = an_event.when[0].end_time.split('T')

        activities_list[-1].start_date_time = _parse_date_time( raw_start_date_time )
        activities_list[-1].end_date_time = _parse_date_time( raw_end_date_time ) 
        
    #if there are no activities, return an empty list
    return activities_list

#=========================================================================
##
# Description:
# Converts the date/time string of each activity
# into datetime format


def _parse_date_time( date_time ): 

    #format of date:
    #'yyyy-mm-dd' +'T' +'hh:mm:ss.sss-hh:mm' (last part is time
    #difference from UTC
    if len(date_time) > 1:
        date = date_time[0].split('-')
        year = int( date[0] )
        month = int( date[1] )
        day = int( date[2] )
        timesplit = date_time[1].split(':')
        hour = int( timesplit[0] )
        minute = int( timesplit[1] )

    return datetime.datetime( year, month, day, hour, minute ) 






#=========================================================================
##
# Description: 
# Unit test function
if __name__ == "__main__":
    current_time = datetime.datetime.today()
    print "Current time:", current_time

    now_datetime  = datetime.datetime.today()
    two_days = datetime.timedelta(days=2)
    two_days_activities = get_activities( now_datetime, \
                                              now_datetime + two_days )


    print "\nActivities today:"
    today = datetime.date.today()
    activities_today = get_activities_for_day( today ) 
    for item in activities_today:
        print "%s: %s to %s" % ( item.name, item.start_date_time, \
                                     item.end_date_time )

    print "\nActivities over the next 48 hours:"
    for item in two_days_activities:
        print "%s: %s to %s" % ( item.name, item.start_date_time, \
                                     item.end_date_time )


    print "\nNext activity:"
    next_activity = get_next_activity()
    print "%s: %s to %s" % ( next_activity.name, next_activity.start_date_time, \
                                     next_activity.end_date_time )



