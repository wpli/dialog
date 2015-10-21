## Datetime Information

##     * functions:
##           o get_current_time: returns datetime.time object
##           o get_current_date: returns datetime.date object
##           o get_current_datetime: returns datetime.datetime object

##                 + 
##                       # weatherobject has: 'date', 'enumerated_weather_forecast' 'friendly_weather_string' <<- this is text spew 
##           o get_weather( day )
          

import sys
import datetime
from urllib import quote
import urllib2, re
from xml.dom import minidom

sys.path.append( "../../tbh_api/src" )
from tbh_api import *

#=========================================================================

##
# Description:
# TBH zipcode
TBH_ZIPCODE = '02110'

##
# Description
# Google URL to look up weather by zipcode and language
# First string is zipcode
# Second string is language ID (set to empty string for English default
GOOGLE_WEATHER_URL = 'http://www.google.com/ig/api?weather=%s&hl=%s'

#=========================================================================

##
# Description: 
# Weather object 
# This represents the weather on a day
@tbh_api_callable_class
class daily_weather_forecast_t( object ):
    
    ##
    # Description:
    # Date object with date of this forecast
    date = None
    
    ##
    # Description:
    # Qualitative weather condition for entire day
    # This is not the current weather condition    
    weather_condition = None
    
    ##
    # Description:
    # High temperature and low temperature in Fahrenheit    
    high = None
    low = None

    ##
    # Description:
    # Creates a new daily weather forecast object with a given date, 
    # weather_condition, high, and low
    @tbh_api_callable_method
    def __init__( self, date=None, weather_condition=None, high=None, low=None ):
        self.date = date
        self.weather_condition = weather_condition
        self.high = high
        self.low = low


#=========================================================================

##
# Description: 
# Current weather object 
# This represents the weather at a point in time
@tbh_api_callable_class
class current_weather_forecast_t( object ):
    
    ##
    # Description:
    # Datetime object with date and time of this forecast
    date_time = None
    
    ##
    # Description:
    # Qualitative weather condition at a point in time    
    weather_condition = None
    
    ##
    # Description:
    # Current temperature in Fahrenheit    
    temperature = None

    ##
    # Description:
    # Percent humidity    
    humidity = None

    ##
    # Description:
    # Creates a new current weather forecast object with a given datetime, 
    # weather_condition, temperature, humidity
    @tbh_api_callable_method
    def __init__( self, date_time=None, weather_condition=None, 
                  temperature=None, humidity=None ):
        self.date_time = date_time
        self.weather_condition = weather_condition
        self.temperature = temperature
        self.humidity = humidity

#=========================================================================

##
# Description:
# Returns the weather at current time for specific location (zip code)
@tbh_api_callable
def get_current_weather():
    
    # Grab data from Google
    weather_data = _grab_google_weather_info( TBH_ZIPCODE )
    # Extract weather info from google spew
    current_weather_object = _extract_google_current_weather( weather_data )
    
    return current_weather_object
     

#=========================================================================

##
# Description:
# Returns the weather forecast for given date for specific location 
# (zip code) 
# \note: Will only return within three days of today
@tbh_api_callable
def get_daily_weather( date ):
    
    # Grab data from Google
    weather_data = _grab_google_weather_info( TBH_ZIPCODE )
    
    # Extract weather info from google spew
    weather_object = _extract_google_daily_weather( weather_data, date )
    
    return weather_object
     
#=========================================================================

##
# Description:
# Scrapes weather data from Google for a given zipcode
def _grab_google_weather_info( zipcode ):
    weather_data = None

    # URL encode the string representation of zipcode
    # and fill URL pattern    
    zipcode = str( zipcode ) 
    url = GOOGLE_WEATHER_URL % (zipcode, '')
    
    # read URL into XML string
    try:
       handler = urllib2.urlopen(url)

       content_type = handler.info().dict['content-type']
       charset = re.search('charset\=(.*)',content_type).group(1)
       if not charset:
          charset = 'utf-8'
       if charset.lower() != 'utf-8':
          xml_response = handler.read().decode(charset).encode('utf-8')
       else:
          xml_response = handler.read()
       handler.close()
     
    # return None if there is a web access issue      
    except:
        return weather_data
    
    # parse XML data into recursive dictionary structure        
    try:
        dom = minidom.parseString(xml_response)    
    
        weather_data = {}
        weather_dom = dom.getElementsByTagName('weather')[0]
    
        data_structure = { 
            'forecast_information': ('city', 'postal_code', 'latitude_e6', 'longitude_e6', 'forecast_date', 'current_date_time', 'unit_system'),
            'current_conditions': ('condition','temp_f', 'temp_c', 'humidity', 'wind_condition', 'icon')
        }           
        for (tag, list_of_tags2) in data_structure.items():
            tmp_conditions = {}
            for tag2 in list_of_tags2:
                try: 
                    tmp_conditions[tag2] =  weather_dom.getElementsByTagName(tag)[0].getElementsByTagName(tag2)[0].getAttribute('data')
                except IndexError:
                    pass
            weather_data[tag] = tmp_conditions
    
        forecast_conditions = ('day_of_week', 'low', 'high', 'icon', 'condition')
        forecasts = []
        
        for forecast in dom.getElementsByTagName('forecast_conditions'):
            tmp_forecast = {}
            for tag in forecast_conditions:
                tmp_forecast[tag] = forecast.getElementsByTagName(tag)[0].getAttribute('data')
            forecasts.append(tmp_forecast)
    
        weather_data['forecasts'] = forecasts
        dom.unlink()
    except UnboundLocalError:
        weather_data = None

 
    #print weather_data
    return weather_data
    
#=========================================================================

##
# Description:
# Gets the current weather conditions from a recursive dictionary structure
def _extract_google_current_weather( weather_data ):
    current_weather = None
    
    if weather_data != None:
        # instantiate a current_weather_forecast_t class
        current_weather = current_weather_forecast_t()
        
        # assign current date and time for weather
        # currently, this is expressed in UTC
        # Example output: 2009-05-29 13:36:46 +0000
        # We need to split this into the correct parts
        current_date_time_string = weather_data['forecast_information']['current_date_time']    
        current_date = current_date_time_string.split()[0]
        current_time = current_date_time_string.split()[1]   
        
        current_weather.date_time = datetime.datetime( int( current_date.split( '-' )[0] ), 
                                      int ( current_date.split( '-' )[1] ), 
                                      int( current_date.split( '-' )[2] ), 
                                      int( current_time.split( ':' )[0] ), 
                                      int( current_time.split( ':' )[1] ), 
                                      int( current_time.split( ':' )[2] ) )
        
        # assign current weather condition
        # this is a short (1-2 word) text description    
        current_weather.weather_condition = weather_data['current_conditions']['condition']
          
        # temperature in Fahrenheit 
        current_weather.temperature = int( weather_data['current_conditions']['temp_f'] )
        
        # humidity in percentage
        # data is presented in a string as follows: "Humidity: 98%" 
        humidity_string = weather_data['current_conditions']['humidity']
        humidity_percentage = humidity_string.split()[1]
        humidity_percentage_value = int( humidity_percentage.split( '%' )[0] )
        current_weather.humidity = humidity_percentage_value
    
    return current_weather
    
#=========================================================================
##
# Description:
# Gets the weather forecast for a 
# Returns None if the date is invalid (not today or three days in advance)
def _extract_google_daily_weather( weather_data, date ):
    daily_weather_forecast = None
    
    if weather_data != None:
        # instantiate a current_weather_forecast_t class
        daily_weather_forecast = daily_weather_forecast_t()
        
        # assign current date and time for weather
        # currently, this is expressed in UTC
        # Example output: 2009-05-29 13:36:46 +0000
        # We need to split this into the correct parts
        current_date_time_string = weather_data['forecast_information']['forecast_date']    
        current_date = current_date_time_string.split()[0]
           
        
        current_date_object = datetime.date( int( current_date.split( '-' )[0] ), 
                                      int ( current_date.split( '-' )[1] ), 
                                      int( current_date.split( '-' )[2] ) )
    
    # check whether the query date is within the forecast range
    if date in ( current_date_object, current_date_object + datetime.timedelta(1), current_date_object + datetime.timedelta(2),
                current_date_object + datetime.timedelta(3) ):
        day_difference_timedelta = date - current_date_object
        day_difference = day_difference_timedelta.days
        daily_weather_forecast.date = date
        daily_weather_forecast.weather_condition = weather_data['forecasts'][day_difference]['condition']
        daily_weather_forecast.high = int( weather_data['forecasts'][day_difference]['high'] )
        daily_weather_forecast.low = int( weather_data['forecasts'][day_difference]['low'] )
    
    else:
        
        return None
    
    #daily_weather_forecast
    return daily_weather_forecast
    
        
                                      





if __name__ == "__main__":      
    current_weather_info = get_current_weather()

    print "Current weather (time, humidity, condition, and temperature)"

    print current_weather_info.date_time
    print current_weather_info.humidity
    print current_weather_info.weather_condition
    print current_weather_info.temperature
    
    print "Today's weather (date, weather condition, hugh, and low)"
    daily_weather_info = get_daily_weather( datetime.date.today() )
    print daily_weather_info.date
    print daily_weather_info.weather_condition
    print daily_weather_info.high
    print daily_weather_info.low
