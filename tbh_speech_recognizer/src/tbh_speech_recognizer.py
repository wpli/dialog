## Speech Recognizer
##     * runs when called, possibly threaded 

# imports
import os
import threading
import functools
import xmlrpclib
import wave
from array import array
import gobject

# for Skype4Py constants
import Skype4Py

##
# Description:
# Default format of audio files
DEFAULT_FORMAT = 'LIN16'

##
# Description
# Default chunk size for audio files
DEFAULT_CHUNK_SIZE = 8192

##
# Description
# Default port for audio files
# DEFAULT_PORT = 3000

## 
# Description
# List of grammar files
DEFAULT_GRAMMAR_LIST = [ 'full', 'weather', 'activities', 'basic', 'menus', 'phone_call', 'system', 'sleeping', 'skype', 'call_contact' ]

DEFAULT_SYSTEM_STATE_TO_GRAMMAR_DICT = { 'full': 'full', 
                 'weather': 'weather', 
                 'activities': 'activities', 
                 'basic':'basic', 
                 'menus': 'menus',
                 'phone_call': 'phone_call',
                 'system': 'system',
                 'sleeping': 'full',
                 'awake': 'full',
                 'skype': 'skype',
                 'call_contact': 'call_contact'
                                      
                 }


##
# Description:
# Class that contains all elements of the speech recognizer
class tbh_speech_recognizer_t:
    
    ##   
    # Description
    # Initializes recognizer with certain knob settings
    def __init__( self, starting_grammar, default_grammar, grammar_list = DEFAULT_GRAMMAR_LIST, system_state_to_grammar_dict = DEFAULT_SYSTEM_STATE_TO_GRAMMAR_DICT ):

        ## 
        # Description:
        # Shows available FFST files
        # Currently this is a list - we cannot create grammar files on the
        # fly yet
        self.grammar_list = grammar_list
        
        # Mapping between grammar_list (which contains the names of
        # files) and the desired grammar_states from the dialog
        # manager

        self.system_state_to_grammar_dict = system_state_to_grammar_dict

        ##
        # Set a default grammar to "back off" to
        self.default_grammar = default_grammar

        ## 
        # Description:
        # Set the initial grammar
        self.current_grammar = starting_grammar

        ## 
        # Description:
        # State variable to determine whether in phone call
        self.in_phone_call = False

        ##
        # Description:
        # Has handlers for processed audio
        self._processed_audio_event_handler_list = []

        ##
        # Description:
        # Has GTK handlers for processed audio 
        self._processed_audio_event_handler_gtk_list = []
        
    ##
    # Description
    # Runs the recognizer on an audio input, returns n-best list
    # Note: may take some time to run (~1 second)
    def recognize_audio_sync( self , audio , grammar ):
        format = DEFAULT_FORMAT
        chunk = DEFAULT_CHUNK_SIZE        

        summit = xmlrpclib.ServerProxy('http://localhost:3000/RPC2')    

        # The SUMMIT Library has a grammar compile function for JSGFs
        # This does not seem to work on local versions of SUMMIT
        gid = grammar
        lsb = True

        # read file
        wavfile = wave.open(audio, 'rb')
        if lsb:
            w = wavfile.getfp().read()
        else:
            print "byte swapping"
            #print wavfile.getfp().read()
            a = array('h')
            a.fromstring(wavfile.getfp().read())
            a.byteswap()
            w = a.tostring()
        wavfile.close()

        # process with the grammar given
        if grammar in self.grammar_list:
            # Attempts to accept the grammar file
            # If the grammar file does not exist, then the 
            uid = summit.utterance.open( gid, 'LIN16', True, 16000 )
        else:
            gid = ''
            uid = summit.utterance.open( gid, 'LIN16', True, 16000 )

        # break the data into chunks and pass to recognizer
        # the details of this are handled by SUMMIT
        try:

            i = 0
            while (i < len(w)):
                chunk = 1024;
                data = w[i:(i+chunk)]
                i += chunk
                n = summit.utterance.write(uid, xmlrpclib.Binary(data))

            print "GRAMMAR", gid
            nbest = summit.utterance.close(uid)
        except:
            print "Unsuccessful recognition attempt"
            nbest = None 



        return nbest

    # ------------ CALLBACKS -------------- #
    ##
    # Description
    # Processes the audio and passes around the nbest list
    def process_raw_audio_handler( self , param_dict ):
        # pass file to the speech recognizer to get nbest list
        # example nbest_list: [ { 'text: "what time is it', 'score: 5.61' }, ... ]
        current_file_name = param_dict[ 'filename' ]
        #Test to see if errors in xmlrpc recognizer were file-specific
        # this was a file that failed
        # the error did not seem to be reproducible
        #current_file_name = '../../tbh_top_level/audio_files/1305858652.wav'
        print current_file_name
        nbest_list = self.recognize_audio_sync( current_file_name, self.current_grammar )
        
        # continue if there is proper nbest list returned
        if nbest_list is not None:
            print "SPEECH RECOGNITION RESULTS:"
            for item in nbest_list:
                print "%s, Score: %s" % ( item['text'], item['score'] )

            # call whoever wants the nbest list
            param_dict[ 'nbest_list' ] = nbest_list
            self._processed_audio_event( param_dict )
        
    ##
    # Description
    # Processes the dialog manager suggesting new grammar
    def process_action_handler( self , param_dict ):
        new_grammar_state = param_dict[ 'action_dict' ][ 'speech_recognizer_grammar' ]

        # Logic is as follows: change if not None
        if new_grammar_state is not None and self.in_phone_call == False:
            if self.system_state_to_grammar_dict[ new_grammar_state ] in self.grammar_list:
                self.current_grammar = self.system_state_to_grammar_dict[ new_grammar_state ]

            # To guard against nonsensical desired grammars, set to
            # "full" grammar if the desired grammar was not found
            else:
                print "GRAMMAR NOT FOUND: %s" % new_grammar_state
                self.current_grammar = 'full'

        print "CURRENT GRAMMAR:", self.current_grammar

        # If we have to re-execute the speech recognition, do so
        if param_dict[ 'action_dict' ][ 'speech_recognizer_recompute_nbest' ]:
            self.process_raw_audio_handler( param_dict )

    ##
    # Description:
    # Changes the grammar depending on the state of the phone
    def process_skype_event_handler( self, skype_event ):
        event_string = str(skype_event)
        if event_string == "INPROGRESS":
            self.current_grammar = 'call_contact'
            self.in_phone_call = True
        elif event_string in ( "FINISHED", "REFUSED", "FAILED" ):
            self.current_grammar = 'full'
            self.in_phone_call = False
        





    # ------------ HANDLE EVENTS -------------- #
    ##
    # Description
    # Stuff for managing the speech recognizer events/callbacks
    def _processed_audio_event( self, param_dict ):
        for handler in self._processed_audio_event_handler_list:
            t = threading.Thread( target=functools.partial( handler , param_dict ) )
            t.start()

        #callback for GTK handlers 
        for handler in self._processed_audio_event_handler_gtk_list:
            gobject.idle_add( handler , param_dict)
    ##
    # Description
    # Adds callbacks
    def add_processed_audio_event_handler( self, handler ):
        self._processed_audio_event_handler_list.append( handler )

    ##
    # Description
    # Adds GTK callbacks
    def add_processed_audio_event_gtk_handler( self, handler ):
        self._processed_audio_event_handler_gtk_list.append( handler )


if __name__ == "__main__":
    recognizer = tbh_speech_recognizer_t( 'full', 'full' )
    nbest = recognizer.recognize_audio_sync( 'test.wav', 'full' )
    for index, item in enumerate( nbest ):
        print "%s, Hypothesis: %s, Score: %.2f" % ( index, item['text'], item['score'] )
