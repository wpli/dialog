#
# Answers a phone call automatically
# Must make a phone call within 10 seconds
from tbh_skype_interface import *
import Skype4Py

def call_status_change( call, status ):
    skype_interface.answer_call( call )

if __name__ == "__main__":
    #Instantiate a Skype object

    skype_interface = tbh_skype_interface_object()
    skype_interface.start_skype()
    skype_interface.skype.OnCallStatus = call_status_change
  
    
    import time
    time.sleep( 10 )







