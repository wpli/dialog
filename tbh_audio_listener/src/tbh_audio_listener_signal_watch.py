## Audio Listener

##     * listens continuously to an audio port and sends an event when it decides it hears a chunk of audio, stores the audio into the database with a tag
##           o tag = MACaddress+timestamp
##           o Stores the audio data into local database with tag with threshold settings
##           o Also sends data ( and tag ) to remote database for persistent storage and analysis 
##     * event object
##           o tag
##           o threshold settings of the listener 
##     * functions:
##           o add_audio_event_listener( audio_event_listener )
##           o set_power_threshold, get_power_threshold -- does not return until success/failure to set
##           o set_holdover_threshold, get_holdover_threshold
##           o set_minspeech_threshold, get_minspeech_threshold
##           o set_prespeech_threshold, get_prespeech_threshold
##           o get_audio_from_tag( tag ) returns an audio obj which contains tag, thresholds, raw data 
##     * implementation thoughts: audio will be stored to files.
##     * Use Case:
##           o create al = new AudioListener()
##           o Define function, f, to handle the events from audio listener
##           o al.add_audio_listener( f ) 


import sys
sys.path.append( "../../tbh_api/src" )
from tbh_api import *
sys.path.append( "../../tbh_api/src/data_model/" )
sys.path.append( "../../tbh_api/third-party/storm" )
import data_model

import threading
import gobject
import gio
import gst
import datetime
import functools
import pickle



#==========================================================================

##
# Description:
# The default port which connects to the audio listener
DEFAULT_AUDIO_LISTENER_PORT             = 8765

##
# Description:
# The structure name sent by the Speech_activity_Detector filter for
# gstreamer ( SAD ) whenever a chunck of audio has been recognized
# as speech ( at the end )
SAD_SPEECH_DETECTED_STRUCTURE_NAME      = 'end_of_segment'

##
# Description:
# The default throsholds for a Tablet running the audia listner
# These are the thresholds for the Speech-Activity-Detector ( aka SAD )
DEFAULT_TABLET_SAD_POWER_THRESHOLD      = -25
DEFAULT_TABLET_SAD_HOLDOVER_THRESHOLD   = 1000000
DEFAULT_TABLET_SAD_MINSPEECH_THRESHOLD  = 50000
DEFAULT_TABLET_SAD_PRESPEECH_THRESHOLD  = 900000


##
# Description:
# The default names for the gstreamer pipelin source and sink
DEFAULT_GST_SOURCE_NAME                 = 'source'
DEFAULT_GST_SINK_NAME                   = 'sink'


#==========================================================================

##
# Description: 
# listens continuously to an audio device and sends an event when it
# decides it hears a chunk of speech, stores the audio into the
# database with a tag
#
# Handlers can be added to this which will get called whenever a new 
# audio_object ( for hte speech ) has been stored.
#
# \uses_concept audio_listener_handler_concept
@tbh_api_callable_class
class tbh_audio_listener_t(object):

    ##
    # Description:
    # The threshold set for this audio listener
    threshold_set = None

    ##
    # Description:
    # The port this audio listener is running on
    # Note: currently NOT IMPLEMENTED
    audio_port = None


    ##
    # Description:
    # The gstreamer elements we need for listening for audio
    gst_pipeline = None
    _gst_source_name = None
    gst_sink_name = None

    ##
    # Description:
    # The internal event thread for the audio listener
    # _event_thread = None

    ##
    # Description:
    # The set of handlers waiting to be told when audio has been captured
    _audio_listener_handler_list = None

    ## 
    # Description
    # The set of handlers waiting to be told when the gst-Speech Activity
    # Detector (gst-SAD) has fired
    _start_of_audio_handler_list = None


    #------------------------------------------------------------------------
    

    ##
    # Description:
    # Initializes the thresholds to sane values, sets up port
    @tbh_api_callable_method
    def __init__( self ):

        # set port
        self.audio_port = DEFAULT_AUDIO_LISTENER_PORT

        # set thresholds
        self.threshold_set = data_model.audio_listener_setting_t() #tbh_api.data_model.audio_listener_setting_t()
        self.threshold_set.power_threshold = DEFAULT_TABLET_SAD_POWER_THRESHOLD
        self.threshold_set.holdover_threshold = DEFAULT_TABLET_SAD_HOLDOVER_THRESHOLD
        self.threshold_set.minspeech_threshold = DEFAULT_TABLET_SAD_MINSPEECH_THRESHOLD
        self.threshold_set.prespeech_threshold = DEFAULT_TABLET_SAD_PRESPEECH_THRESHOLD

        # set the gst source/sink names
        self._gst_source_name = DEFAULT_GST_SOURCE_NAME
        self.gst_sink_name = DEFAULT_GST_SINK_NAME

        # Initialize, no handlers
        self._audio_listener_handler_list = []

        # Initialize start_of_audio handler list
        self._start_of_audio_handler_list = []

        # GIO output memory stream
        self.gst_gio_output_memory_stream = None

        
        # Loop for audio listener
        self.keep_running = True


    #------------------------------------------------------------------------


    ##
    # Description:
    # Adds an audio listener handler to be called when audio has been captured
    #
    # \param handler - a audio_listener_handler_t object, or a function which
    #                  implements the audio_listener_handler_concept
    @tbh_api_callable_method
    def add_audio_listener_handler( self, handler ):
        self._audio_listener_handler_list.append( handler )

    
    ##
    # Description:
    # Adds an handler to be called when gst-SAD first fires
    #
    # \param handler - a audio_listener_handler_t object, or a function which
    #                  implements the audio_listener_handler_concept
    @tbh_api_callable_method
    def add_start_of_audio_handler( self, handler ):
        self._start_of_audio_handler_list.append( handler )
    


    #------------------------------------------------------------------------

    def make_new_pipeline( self ):
        if 1:


            # setup the audio pipeline
            self.gst_pipeline = self.make_gst_pipeline_for_record( 
                self._gst_source_name, self.gst_sink_name )

            self.gst_sink_object = self.gst_pipeline.get_by_name( self.gst_sink_name )
            # create a new listener thread


            # ok, setup the output buffer for pipeline
            self.reset_memory_output_stream()

            # getthe pipeline bus
            self.pipeline_bus = self.gst_pipeline.get_bus()




            # start the pipeline
            self.gst_pipeline.set_state( gst.STATE_PLAYING )


            # start the pipeline

            
            self.pipeline_bus.add_signal_watch()
            self.pipeline_bus.connect( "message", self.process_message )



    ##
    # Description
    # listens to audio port and send out chunks when it hears something
    @tbh_api_callable_method
    def run( self ):

        self.make_new_pipeline()
        


        # Check that we are not already running
        # if self._event_thread is not None:
        #    raise RuntimeError( 'Cannot start an already running audio_listener' )

        # connect to port
        # TODO: for now do nothing, fix later

        # From subclass
        poll_forever_timeout = -1
        # while self.keep_running:
        
        if 1:
            pass
            """
            # Ok, now we just have to repeatedly poll the pipeline bus
            # for the messages we want, and process the messages

            # pipeline_bus.add_signal_watch()
            # pipeline_bus.connect("message", self.process_message)

            # message = pipeline_bus.pop()
            # message = pipeline_bus.pop( gst.CLOCK_TIME_NONE, gst.MESSAGE_APPLICATION | gst.MESSAGE_EOS | gst.MESSAGE_ERROR | gst.MESSAGE_STATE_CHANGED )

            processed = False
            while not processed:

            

                # print 'starting to poll'
                message = self.pipeline_bus.poll( gst.MESSAGE_APPLICATION | gst.MESSAGE_EOS | gst.MESSAGE_ERROR | gst.MESSAGE_STATE_CHANGED, poll_forever_timeout )

                if message != None:
                    try :
                        processed = self.process_message( message )
                    except:
                        print "exception happened"
                        raise

            # Check whether the code reaches past here
            # when the handlers stop responding, this does not get called

            """
            """
            i = 0
            while i < 100:
                print "HERE!!!"
                i += 1
            """


        # """
        # self._event_thread = \
        #     _audio_listener_event_thread( self._gst_pipeline,
        #                                  self._gst_giostream_sink_name,
        #                                  self,
        #                                  self._internal_process_audio_event )
        #"""
        # start the event thread for internal processing
        # then wait for it to finish
        
        # self._event_thread.start()
        # self._event_thread.join()
        
        # reset event thread so that we can be started again
        # self._event_thread = None


    #------------------------------------------------------------------------

    ##
    # Description:
    # Create a gstreamer pipeline for recording audio
    # The source and sink of the pipeline are named with hte given names
    # so they can be referenced externally using pipeline.get_by_name
    def make_gst_pipeline_for_record( self, gst_source_name, gst_sink_name ):
        
        # Ok, create the beginnig of hte pipeline, which takes input from
        # the source and pushes into queue, then audio converts to the
        # desired format
        source_filter = self.get_gst_filter_string_for_gst_source_record( gst_source_name )
        audio_convert_filter = "queue ! audioconvert ! audioresample"
        
        # Create a resample filter for getting hte right sampling format
        resample_parameter = {  'resample_bitrate'     : 16000, #800,
                                'resample_num_channel' : 1,
                                'resample_bitwidth'    : 16,
                                'resample_bitdepth'    : 16 }
        audio_resample_filter = "audio/x-raw-int, rate=%(resample_bitrate)d, channels=%(resample_num_channel)d, width=%(resample_bitwidth)d, depth=%(resample_bitdepth)d " % resample_parameter

        # create a speech activity detector filter ( SAD )
        speech_activity_detector_parameter = { 'name' : 'sad' }
        
        speech_activity_detector_filter = "SAD name=%(name)s" % speech_activity_detector_parameter

        sink_filter = self.get_gst_filter_string_for_gst_sink_record( gst_sink_name )
        






        # Ok, now link all filters together and make a pipeline
        parse_launch_string = source_filter + " ! " + \
                              audio_convert_filter + " ! " + \
                              audio_resample_filter + " ! " + \
                              speech_activity_detector_filter + " ! " + \
                              sink_filter

        # print parse_launch_string
        gst_pipeline = gst.parse_launch( parse_launch_string )





        # Ok, now set the threholds for the SAD filter
        sad_filter_obj = gst_pipeline.get_by_name( speech_activity_detector_parameter[ 'name' ] )
        sad_filter_obj.set_property( 'enable_noise_est', True )
        sad_filter_obj.set_property( 'threshold', self.threshold_set.power_threshold )
        sad_filter_obj.set_property( 'minspeech' , self.threshold_set.minspeech_threshold )
        sad_filter_obj.set_property( 'holdover', self.threshold_set.holdover_threshold )
        

        # return this new pipeline
        return gst_pipeline


    #------------------------------------------------------------------------


    ##
    # Description:
    # Returns a gst filter string for the source when we want to record
    # sets the filter element the given name
    def get_gst_filter_string_for_gst_source_record( self, name ):
        #return "dsppcmsrc name=%s" % name
        #return 'filesrc location="/home/velezj/media/music/sample.ogg" ! oggdemux ! vorbisdec '
        return 'pulsesrc name=source device=alsa_input.pci-0000_00_1b.0.analog-stereo'



    #------------------------------------------------------------------------

    
    ##
    # Description:
    # Returns the gst filter string for the sink when we want to record
    # Sets the filter element name to that given
    def get_gst_filter_string_for_gst_sink_record( self, name ):
        return "wavenc ! giostreamsink name=%s" % name
        # return "wavenc ! filesink name=%s location=test.wav" % name

        
    #------------------------------------------------------------------------


    ##
    # Description:
    # Handler for the internal event thread.  This is called every time the
    # internal thread has an audio_object_t reacorded from the stream.
    # This handler simply sends the audio_object_t to those handler waiting for
    # it and registered with this audio listener
    def _internal_process_audio_event( self, gst_pipeline, audio_object ):        
        # Ok, spawn a new thread for each handler listening for this audio
        # and calls the handler
        # print "about to call handlers"

        # store count in an external file because we want to resume
        # count from wherever previous count was, even if we restart
        # the program
        try:
            count_file = open( 'count.pkl', 'r' )
            count = pickle.load( count_file )
            count_file.close()
        except:
            count = 0
            count_file = open( 'count.pkl', 'w' )
            pickle.dump( count, count_file )
        current_file_name = str(count) + '.wav'
            
        # save the file
        f = open( str(count) + '.wav', 'w')
        f.write( audio_object )
        f.close()
    
        #Increment the counter
        count = count + 1
        count_file = open( 'count.pkl', 'w' )
        pickle.dump( count, count_file )
        count_file.close()

        for handler in self._audio_listener_handler_list:
            # print "calling handler %s" % str( handler )
            t = threading.Thread( target=functools.partial( handler, current_file_name ) )
            t.start()

    def _start_of_audio_event( self, gst_pipeline ):

        for handler in self._start_of_audio_handler_list:
            print "HANDLER", str( handler )
            t = threading.Thread( target=functools.partial( handler ) )
            t.start()

    ##
    # Description:
    # Process a message from hte gst pipeline bus.
    # In general, we only want to know when an audio chuck has been 
    # processed by gstreamer into the sink so that we can send out
    # and audio_object_t with the data to any listners waiting for it
    def process_message( self, bus, message ):
        # Ok, check the name of the structure in the message
        # We know that the Speech-Activity-Detector sends out a 
        # named event 'end_of_segment' whenever the speech is recognized
        # as such, so just look for it    
        
        #return None
        # print message.type, str(message)
        #if message.structure.get_name() == SAD_SPEECH_DETECTED_STRUCTURE_NAME:
        #    print "SAD has fired!"

        # http://old.nabble.com/Troubles-with-gstreamer,-pygtk-and-ubuntu-karmic-td26377568.html
        #if message.structure is None:
        #    return
        

        print message.structure.keys()

        if message.type == gst.MESSAGE_APPLICATION and message.structure.keys()[0] == 'start_timestamp':
            self._start_of_audio_event( self.gst_pipeline )



        elif message.type == gst.MESSAGE_APPLICATION and message.structure.keys()[0] == 'end_timestamp':

            
            # if message.type == gst.MESSAGE_EOS:
            # self.gst_pipeline.set_state( gst.STATE_NULL )

            # Ok, do some processing to get the audio into an audio object
            audio_object = self.create_new_audio_object_from_memory_output_stream()
            # audio_object = None

            # Reset the output stream to be empty
            # self.reset_memory_output_stream()

            # print "returning True"

            # now async fire the callbacks waiting for this audio object
            self._internal_process_audio_event( self.gst_pipeline, audio_object )
           
            # Note: We are making a new pipeline here
            # self.gst_pipeline = self.make_gst_pipeline_for_record( 
            #     self._gst_source_name, self.gst_sink_name )

            # self.gst_sink_object = self.gst_pipeline.get_by_name( self.gst_sink_name )


            # getthe pipeline bus
            # self.pipeline_bus = self.gst_pipeline.get_bus()

            # print "about to start playing new pipeline"
            
            # self.make_gst_pipeline_for_record( 
            #     self._gst_source_name, self._gst_giostream_sink_name )

            self.gst_pipeline.set_state( gst.STATE_NULL )
            #self.gst_pipeline.set_state( gst.STATE_PLAYING )

            self.make_new_pipeline()


            return True 

            # self.gst_pipeline.set_state( gst.STATE_PLAYING )
            # For other messages we just rpint them out
        else :
            return False





    #------------------------------------------------------------------------


    ##
    # Descripiton:
    # Creates a new audio_object_t from the audio data in the 
    # memory output stream. This will also store this new object
    # into the DB
    def create_new_audio_object_from_memory_output_stream( self ):

        # print "Content size: %d" % self.gst_gio_output_memory_stream.get_data_size()
        #print "CONTENT: %s" % self.gst_gio_output_memory_stream.get_contents()
        #fout = open( "content_text.wav_%s" % str(datetime.datetime.now()) , "w" )
        #fout.write( self.gst_gio_output_memory_stream.get_contents() )
        #fout.close()
        
        # Create a new audio_object_t and set it's data to be the
        # data from the output stream
        # audio_object = tbh_api.model.audio_object_t( datetime.datetime.now(), tbh_api.get_local_host() )
        #audio_object.capture_audio_listener_setting = self.threshold_set
        #audio_object.capture_audio_data = self.gst_gio_output_memory_stream.get_contents()
        audio_object = self.gst_gio_output_memory_stream.get_contents()
        #audio_object = None
        
        # add to DB
        #tbh_api.db.add( audio_object )
        #tbh_api.db.commit()
        
        return audio_object


    #------------------------------------------------------------------------


    ##
    # Description:
    # Resets the memory output stream
    def reset_memory_output_stream( self ) :
        # print "In reset_memory_output_stream"
        # if we have an output stream already. close it
        if self.gst_gio_output_memory_stream is not None:
            
            self.gst_gio_output_memory_stream.close()
            # print "closed file"
        # ok, here we will create a new memry poutput stream and store
        # it.
        self.gst_gio_output_memory_stream = gio.MemoryOutputStream()
        
        # Now we need to set this as the stream to use in the pipeline
        self.gst_sink_object.set_property( 'stream', self.gst_gio_output_memory_stream )
        

#==========================================================================
#==========================================================================
#==========================================================================
#==========================================================================
#==========================================================================

##
# Code for in memory gio stream sink
# gmem = gio.MemoryOutputStream()
# p = gst.parse_launch( 'filesrc location="/home/velezj/media/music/sine.ogg" ! oggdemux ! vorbisdec ! audioconvert ! audioresample ! audio/x-raw-int ! giostreamsink name="sink"' )
# gsink = p.get_by_name( "sink" )
# gsink.set_property( "stream", gmem )
# p.set_state( gst.STATE_PLAYING )
# gmem.get_data_size()
# gmem.get_contest() <-- This is the raw (x-raw-int) data from the file, woot!

#class GTK_Main:
#    pass


#gtk.gdk.threads_init()
#gtk.main()

