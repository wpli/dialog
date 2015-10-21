##     Skype Interface

##     *
##           o adjust_phone_state 

import sys
# sys.path.append( "../../tbh_api/src" )
# from tbh_api import *
import os
# Import Skype4Py module
import Skype4Py

# Define a new function which is part of the api as:
"""
@tbh_api_callable
def func_foo( arg1, arg2 ):
    ... some code here ...
"""

# Remedy to eliminate segmentation faults, especially with PyGTK
#from Skype4Py.api.posix_x11 import threads_init
# Skype4Py.api.posix_x11.threads_init()


import time


## types library
import types

## threading libraries
import threading
import functools
import gobject

##
# Description:
# Default contacts file
# Can be used as a template for new contacts files
DEFAULT_CONTACTS_FILE = '../../tbh_skype_interface/src/skype_contact_names.txt'

##
# Description:
# Skype interface class
class tbh_skype_interface_t():

    # Constructor that creates instance of Skype4Py.Skype object 
    def __init__( self, contacts_file=None, current_call=None ):

        if contacts_file == None:
            self.contacts = load_skype_contacts( DEFAULT_CONTACTS_FILE )
        else:
            # Note: must pass in a contact dictionary, as defined in
            # load_skype_contacts
            self.contacts = contacts_file


            


        # Member containing Skype4Py.Skype() object
        self.skype = Skype4Py.Skype()

        # Member containing dictionary of contacts
        # We will use our own contact list instead of Skype's internal
        # contacts functions


       # Member containing information about current call
        self.current_call = None
      
        self.skype.OnAttachmentStatus = self.on_skype_attach
        self.skype.OnCallStatus = self.on_call_status

        self.skype_status = None


        ## Handler lists
        self._skype_event_handler_list = []
        self._processed_audio_event_handler_gtk_list = []



    ## Description
    # Connects Skype to the class so that it responds to commands
    # Launches Skype if it is not running
    # This has been separated from the constructor
    def start_skype( self ):

        if not self.skype.Client.IsRunning:
            #print "starting skype..."
            self.skype.Client.Start()

            # Provide some time to allow Skype to start up
            #import time
            #time.sleep(4)

        if Skype4Py.apiAttachAvailable:
            try:
		self.skype.Attach()
            except:
                pass
                  
    ## 
    # Description
    # function to return names                                       
    def get_skype_contact_name( self ):
        try:    
            skype_contact_name = self.contacts[ spoken_name ]['skype_contact_id']     
        except:
            #if there is an error, return None
            skype_contact_name = None

        return skype_contact_name

    ## 
    # Description
    # Function to return an extension
    def get_extension(self, spoken_name):
        try:            
            digits = self.contacts[ spoken_name ]['extension']
            if digits == '':
                extension = None
            else:
                extension = digits
        except:
            extension = None

        return extension

    def get_wait_time( self, spoken_name ):
        try:
            seconds = self.contacts[ spoken_name ]['wait_time']
            if seconds == '':
                wait_time = None
            else:
                wait_time = seconds
        except:
            wait_time = None


        return wait_time



    ##
    # Description:
    # Start a Skype call 
    def make_phone_call( self, contact_id_number ):

        #print self.contacts
        call_target = None
        
        if contact_id_number in self.contacts.keys():
            skype_contact_id = self.contacts[contact_id_number]['skype_contact_id']

            try:
            #if 1:

                self.current_call = self.skype.PlaceCall( skype_contact_id )

                #extension = self.get_extension( name )
                #if extension:
                #    wait_time = self.get_wait_time( name )
                #    self.dial_extension( wait_time, extension )




                call_target = skype_contact_id

            except:
                print "Could not make phone call"
                call_target = None
        
        #print "CURRENT CALL", self.current_call

        return call_target


    ##
    # Description
    # Dial an extension
    # Input: a number string

    def dial_extension(self, wait_time, number_string): 
        time.sleep( float( wait_time ) )
	for digit in number_string:
            self.skype.Client.ButtonPressed(digit)





    def end_phone_call( self ):
        """
        all_calls = self.skype.Calls()
        in_progress_calls = self.determine_in_progress_calls(all_calls)         
        print in_progress_calls
        """
        if self.current_call != None:
            self.current_call.Finish()
            self.current_call = None
        else:
            # No current call
            return None

    ## 
    # Description:
    def hold_call( self ):
        if self.current_call != None:
            #self.current_call.Hold()
            if self.current_call.Status == Skype4Py.clsInProgress:
                self.current_call.Hold()
        else:
            return None

    def resume_call( self ):
        print self.current_call.Status
        if self.current_call != None:

            # We use a string because it doesn't seem that 'LOCALHOLD' was
            # defined in the current Skype4Py version
            if self.current_call.Status == 'LOCALHOLD':                
                self.current_call.Resume()
            else:
                return None
        else:
            return None


    def answer_call( self, call ):
        try:
            call.Answer()
            self.current_call = call
        except:
            return None

        """
        if self.current_call == None:
            # Answer call
            #self.current_call = 
            all_calls = self.skype.Calls()
            #print all_calls
            ringing_calls = filter(lambda x: x.Status == Skype4Py.clsRinging, self.skype.Calls())
        try:
            if ringing_calls[0].Type in \
                    ( Skype4Py.cltIncomingPSTN or Skype4Py.cltIncomingP2P ):
                ringing_calls[0].Answer()
        except:
            pass
        

        else: 
            return None
        """

    def fullscreen_video( self ):
        os.system("wmctrl -a Call")
        os.system("xte 'key f'")

    def unfullscreen_video( self ):
        os.system("wmctrl -a Call")
        os.system("xte 'key f'")



    #def load_contacts()

    ## TBH threading functions
    def execute_action_handler( self, action_code ):
        base_code = action_code[0]
        phone_action = action_code[1][0]

        if phone_action == "make_phone_call":
            pass            
        elif phone_action == "hang_up":
            self.end_phone_call()
        elif phone_action == "answer_phone":
            pass
        elif phone_action == "dial_extension":
            pass
        elif phone_action == "hold_call":
            self.hold_call()
        elif phone_action == "resume_call":
            self.resume_call()
        elif phone_action == "fullscreen_video":
            # press F
            self.fullscreen_video()
        elif phone_action == "unfullscreen_video":
            #press F again
            self.unfullscreen_video()
        elif phone_action == "finished":
            pass
        elif phone_action == "start_over":
            pass
        elif phone_action == "dial_number":
            pass
        elif base_code == "call_contact":
            contact_code = phone_action
            if contact_code in self.contacts.keys():
                desired_contact = contact_code
            else:
                desired_contact = contact_code

            self.make_phone_call( desired_contact )
            
    ######################################################################
    ##
    # EVENT SIGNAL FUNCTIONS: These functions are executed with 
    # certain events in Skype
    ##
    # Description:
    # Triggers when Skype tries to attach
    def on_skype_attach(self, status):
        pass
        #print "API Attachment Status:", self.skype.Convert.AttachmentStatusToText(status)


    ## 
    # Description:
    # Triggers when there is a change in the call state
    def on_call_status(self, call, status):
        # It seems most logical simply to use the status definitions defined by 
        # Skype4Py
        # Skype4Py.clsCancelled, Skype4Py.clsFinished, Skype4Py.clsMissed, 
        # Skype4Py.clsRefused, Skype4Py.clsFailed
        
        # if a call is terminated, change the state of self.current_call to None
        # This occurs regardless of which party terminates the call
        
        #if status in ( Skype4Py.clsInProgress, Skype4Py.clsRouting,Skype4Py.clsOnHold, \
        #                   Skype4Py.clsMissed, Skype4Py.clsRinging, \
        #                   Skype4Py.clsRefused, Skype4Py.clsBusy, Skype4Py.clsCancelled ):

        if status == Skype4Py.clsFinished:
            self.current_call = None          
        elif status == Skype4Py.clsRinging:
            incoming_call = self.determine_if_incoming( call, status )

        # Skype event has just occurredps
        print "calling _skype_event", status
        
        self._skype_event( status ) 


    def determine_if_incoming( self, call, status ):
        incoming_call = False
        if call.Type in ( Skype4Py.cltIncomingP2P, Skype4Py.cltIncomingPSTN ):
            if status == Skype4Py.clsRinging:
                incoming_call = True
            else:
                incoming_call = False
            
        return incoming_call

    def getCallStatus(self):
	try:
            return self.call.Status
	except:
            pass

    def whoIsOnline(self):
        for user in self.skype.Friends:
            self.onlineFriends = []
            if user.OnlineStatus == 'ONLINE':				
                self.onlineFriends.append(user.FullName)
	return self.onlineFriends
	
    def getAliasesDict(self):
        return self.aliases			
		
    def putOnHold(self):
        try:
            self.current_call.Hold()
            
	    #self.skype.SkypeEvents.Mute(True)
	except:
            pass
		
    def resumeCall(self):
	try:
            self.current_call.Resume()
	except:
            pass
		
    def answerCall(self):
		
        all_calls = self.skype.Calls()
        #print all_calls
        ringing_calls = filter(lambda x: x.Status == Skype4Py.clsRinging, self.skype.Calls())
        try:
                ringing_calls[0].Answer()
        except:
                pass



    def determine_in_progress_calls(self, all_calls):
        in_progress_calls = []
        for call in all_calls:
            if call.Status in ( Skype4Py.clsCancelled, Skype4Py.clsFinished, Skype4Py.clsMissed, Skype4Py.clsRefused, Skype4Py.clsFailed):
                pass
            else:
                in_progress_calls.append(call)

        return in_progress_calls

    # ------------ HANDLE EVENTS -------------- #
    ##
    # Description
    # Stuff for managing the speech recognizer events/callbacks
    def _skype_event( self, skype_event ):
        for handler in self._skype_event_handler_list:
            t = threading.Thread( target=functools.partial( handler , skype_event ) )
            t.start()

        #callback for GTK handlers 
        for handler in self._processed_audio_event_handler_gtk_list:
            gobject.idle_add( handler , skype_event)
    ##
    # Description
    # Adds callbacks
    def add_skype_event_handler( self, handler ):
        self._skype_event_handler_list.append( handler )




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
    



if __name__ == "__main__":
    #Instantiate a Skype object

    skype_interface = tbh_skype_interface_t()
    skype_interface.start_skype()
    # skype_interface.load_contacts()

    print skype_interface.contacts
    
    import time
    time.sleep(2)

    skype_interface.make_phone_call( 2 )
    # sleep for five seconds 
    time.sleep( 5 )
    skype_interface.hold_call()
    time.sleep( 5 )
    skype_interface.resume_call()

    time.sleep( 5 )
    skype_interface.end_phone_call()
    time.sleep( 4 )

    # Unit test with call --> hold --> hang up
    skype_interface.make_phone_call( 1 )
    # sleep for 10 seconds to allow time for call to be made
    # 
    time.sleep( 10 )
    skype_interface.hold_call()
    time.sleep( 2 )

    skype_interface.end_phone_call()
    time.sleep( 4 )
    



    #try to make a phone call
    #skype_interface.make_phone_call( 'tech support' )
