## Audio Listener
##     * listens continuously to an audio port and sends an event when
##       it decides it hears a chunk of audio

import threading
import gobject
import gio
import gst
import datetime
import functools
import time
import subprocess

#==========================================================================

##
# Description:
# The default port which connects to the audio listener
DEFAULT_AUDIO_LISTENER_PORT             = 8765

##
# Description:
# The default throsholds for a Tablet running the audia listner
# These are the thresholds for the Speech-Activity-Detector ( aka SAD )
DEFAULT_TABLET_SAD_POWER_THRESHOLD      = -30
DEFAULT_TABLET_SAD_HOLDOVER_THRESHOLD   = 1000000
DEFAULT_TABLET_SAD_MINSPEECH_THRESHOLD  = 50000
DEFAULT_TABLET_SAD_PRESPEECH_THRESHOLD  = 200000 
DEFAULT_TABLET_SAD_FRAME_LENGTH  = 31744

## 
# Description:
# Default sampling rate for audio
# This is set at 16kHz for optimal speech recognizer performance
DEFAULT_AUDIO_SAMPLING_RATE             = 16000


##
# Description:
# The default names for the gstreamer pipelin source and sink
DEFAULT_GST_SOURCE_NAME                 = 'source'
DEFAULT_GST_SINK_NAME                   = 'sink'

##
# Description:
# Microphone device name dictionary 
MICROPHONE_DICTIONARY                   = { 'stereo': 'alsa_input.pci-0000_00_1b.0.analog-stereo',  
                                            'logitech_wireless': \
                                                'alsa_input.usb-Logitech_Logitech_Wireless_Headset_H760-00-H760.analog-mono',
                                            'shure_x2u': \
                                                'alsa_output.usb-Shure_Incorporated_Shure_Digital-00-default.analog-stereo.monitor',
                                            'icicle': \
                                                'alsa_input.usb-BLUE_MICROPHONE_Blue_Icicle_201010-00-default.analog-stereo',
                                            'logitech': \
                                            'alsa_input.usb-AKM_AK5370-00-default.analog-mono'
                                            }


#==========================================================================

##
# Description: 
# listens continuously to an audio device and sends an event when it
# decides it hears a chunk of speech, stores the audio into the
# database with a tag
#
# Handlers can be added to this which will get called whenever a new 
# audio_object ( for hte speech ) has been stored.
class tbh_audio_listener_t(object):

    ##
    # Description:
    # Initializes the thresholds to sane values, sets up port
    def __init__( self, microphone_name, temp_audio_storage_path  ):

        # set port
        self.audio_port = DEFAULT_AUDIO_LISTENER_PORT

        # set path for temporarily storing audio files
        # this is not the final data storage location (see tbh_data_storage module)
        self.temp_audio_storage_path = temp_audio_storage_path

        # set microphone name
        if microphone_name in MICROPHONE_DICTIONARY:
            self.microphone_name = MICROPHONE_DICTIONARY[ microphone_name ]
        else:
            self.microphone_name = microphone_name



        # set thresholds
        self.threshold_set = {}
        self.threshold_set[ 'power_threshold' ] = DEFAULT_TABLET_SAD_POWER_THRESHOLD
        self.threshold_set[ 'holdover_threshold' ] = DEFAULT_TABLET_SAD_HOLDOVER_THRESHOLD
        self.threshold_set[ 'minspeech_threshold' ] = DEFAULT_TABLET_SAD_MINSPEECH_THRESHOLD
        self.threshold_set[ 'prespeech_threshold' ] = DEFAULT_TABLET_SAD_PRESPEECH_THRESHOLD
        self.threshold_set[ 'framelength'] = DEFAULT_TABLET_SAD_FRAME_LENGTH
        
        # set the gst source/sink names
        self.gst_source_name = DEFAULT_GST_SOURCE_NAME
        self.gst_sink_name = DEFAULT_GST_SINK_NAME

        # Initialize, no handlers
        self._start_of_audio_handler_list = []
        self._start_of_audio_handler_gtk_list = []
        self._end_of_audio_handler_list = []
        self._end_of_audio_handler_gtk_list = []
        self._poll_audio_handler_list = []
        self._poll_audio_handler_gtk_list = []

        # GIO output memory stream
        self.gst_gio_output_memory_stream = None

        
        # Loop for audio listener
        self.keep_running = True

    # --------- ADDING HANDLERS/CALLBACKS --------- #
    ##
    # Description:
    # Adds an audio listener handler to be called when audio has been
    # captured; handler is a function to be called when event fires
    def add_end_of_audio_handler( self, handler ):
        self._end_of_audio_handler_list.append( handler )

    ##
    # Description: For GTK callbacks 
    # Adds an audio listener handler to be called when audio has been
    # captured; handler is a function to be called when event fires
    def add_end_of_audio_gtk_handler( self, handler ):
        self._end_of_audio_handler_gtk_list.append( handler )

    ##
    # Description:
    # Adds an handler to be called when gst-SAD first fires
    def add_start_of_audio_handler( self, handler ):
        self._start_of_audio_handler_list.append( handler )

    ##
    # Description:
    # Adds a GTK handler to be called when gst-SAD first fires
    def add_start_of_audio_gtk_handler( self, handler ):
        self._start_of_audio_handler_gtk_list.append( handler )

    ##
    # Description:
    # Adds an handler to be called when gst-SAD first fires
    def add_poll_audio_handler( self, handler ):
        self._poll_audio_handler_list.append( handler )

    ##
    # Description:
    # Adds a GTK handler to be called when gst-SAD first fires
    def add_poll_audio_gtk_handler( self, handler ):
        self._poll_audio_handler_gtk_list.append( handler )
    
    ##
    # Description
    # Processes the dialog manager suggesting new settings
    def process_action_handler( self , param_dict ):
        if param_dict[ 'action_dict' ][ 'audio_listener_power_threshold' ] is not None:        
            self.threshold_set[ 'power_threshold' ] = param_dict[ 'action_dict' ][ 'audio_listener_power_threshold' ]
        if param_dict[ 'action_dict' ][ 'audio_listener_holdover_threshold' ] is not None:        
            self.threshold_set[ 'holdover_threshold' ] = param_dict[ 'action_dict' ][ 'audio_listener_holdover_threshold' ]
        if param_dict[ 'action_dict' ][ 'audio_listener_minspeech_threshold' ] is not None:        
            self.threshold_set[ 'minspeech_threshold' ] = param_dict[ 'action_dict' ][ 'audio_listener_minspeech_threshold' ]
        if param_dict[ 'action_dict' ][ 'audio_listener_prespeech_threshold' ] is not None:        
            self.threshold_set[ 'prespeech_threshold' ] = param_dict[ 'action_dict' ][ 'audio_listener_prespeech_threshold' ]

    # --------- SETTING UP, RUNNING THE GST PIPELINE --------- #
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
        resample_parameter = {  'resample_bitrate'     : DEFAULT_AUDIO_SAMPLING_RATE, 
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
        sad_filter_obj.set_property( 'threshold', self.threshold_set[ 'power_threshold' ] )
        sad_filter_obj.set_property( 'minspeech' , self.threshold_set[ 'minspeech_threshold' ] )
        sad_filter_obj.set_property( 'holdover', self.threshold_set[ 'holdover_threshold' ] )
        sad_filter_obj.set_property( 'prespeech', self.threshold_set[ 'prespeech_threshold' ] )
        sad_filter_obj.set_property( 'framelength', self.threshold_set[ 'framelength' ] )
        # sad_filter_obj.set_property( 'output-features', True )

        # return this new pipeline
        return gst_pipeline
 
    ##
    # Description:    
    # take the gst pipeline and make it ready to use (set up watches, etc.)
    def make_new_pipeline( self ):
        self.gst_pipeline = self.make_gst_pipeline_for_record( 
            self.gst_source_name, self.gst_sink_name )
        self.gst_sink_object = self.gst_pipeline.get_by_name( self.gst_sink_name )
                    
        # get the pipeline bus
        self.pipeline_bus = self.gst_pipeline.get_bus()

        # start the pipeline
        self.gst_pipeline.set_state( gst.STATE_PLAYING )
        
        # start the pipeline
        self.pipeline_bus.add_signal_watch()
        self.pipeline_bus.connect( "message", self.process_message )

    # Description
    # listens to audio port and send out chunks when it hears something
    def run( self ):
        self.make_new_pipeline()
                
    # ----------- PROCESSING AUDIO EVENTS ------------ #
    ##
    # Description:
    # Handler for whenever the start of an audio stream is detected
    def _start_of_audio_event( self ):
        for handler in self._start_of_audio_handler_list:
            t = threading.Thread( target=functools.partial( handler ) )
            t.start()
        #GTK handlers - do not spawn threads 
        for handler in self._start_of_audio_handler_gtk_list:
            gobject.idle_add( handler )
    
    ##
    # Description:
    # Handler for whenever the start of an audio stream is detected
    def _poll_audio_event( self , audio_power ):
        tag = str( time.time() )
        param_dict = { 'audio_power' : audio_power , 'time' : tag , 
                           'threshold_set' : self.threshold_set }

        for handler in self._poll_audio_handler_list:
            t = threading.Thread( target=functools.partial( handler , param_dict ) )
            t.start()
        #GTK handlers - do not spawn threads 
        for handler in self._poll_audio_handler_gtk_list:
            gobject.idle_add( handler , param_dict )

    ##
    # Description:
    # Handler for the internal event thread.  This is called every time the
    # internal thread has an audio_object_t reacorded from the stream.
    # This handler simply sends the audio_object_t to those handler waiting for
    # it and registered with this audio listener
    def _end_of_audio_event( self, gst_pipeline, audio_object=None ):        

        # save the file  
        tag = str( int( time.time() ) )
        current_file_name = self.temp_audio_storage_path + '/' + \
            tag + '.wav'
        subprocess.call( "sox" + " test.wav " + current_file_name, shell=True )
        param_dict = { 'filename' : current_file_name , 'time' : tag , 
                           'threshold_set' : self.threshold_set }
        
        # Ok, spawn a new thread for each handler listening for this audio
        # and calls the handler
        for handler in self._end_of_audio_handler_list:
            t = threading.Thread( target=functools.partial( handler, param_dict ) )
            t.start()
            
        # Gtk handler called 
        # These do not spawn seperate threads 
        for handler in self._end_of_audio_handler_gtk_list:
            gobject.idle_add(handler, param_dict)

    ##
    # Description:
    # Process a message from hte gst pipeline bus.
    # In general, we only want to know when an audio chuck has been 
    # processed by gstreamer into the sink so that we can send out
    # and audio_object_t with the data to any listners waiting for it
    def process_message( self, bus, message ):

        if message.type == gst.MESSAGE_APPLICATION and message.structure.keys()[0] == 'start_timestamp':
            self._start_of_audio_event()
        elif message.type == gst.MESSAGE_APPLICATION and message.structure.keys()[0] == 'end_timestamp':
            audio_object = None
            self._end_of_audio_event( self.gst_pipeline, audio_object )
            self.gst_pipeline.set_state( gst.STATE_NULL )
            self.gst_pipeline = None
            self.make_new_pipeline()
            return True 
        elif message.type == gst.MESSAGE_APPLICATION and message.structure.keys()[0] == 'output_feature':
            # print "output_feature", message.structure['output_feature']
            self._poll_audio_event( message.structure['output_feature'] ) 
        else :
            return False

    # ------------- UTILS ---------- #
    ##
    # Description:
    # Returns a gst filter string for the source when we want to record
    # sets the filter element the given name
    def get_gst_filter_string_for_gst_source_record( self, name ):
        #return "dsppcmsrc name=%s" % name
        #return 'filesrc location="/home/velezj/media/music/sample.ogg" ! oggdemux ! vorbisdec '
        return 'pulsesrc name=source device=' + self.microphone_name

    ##
    # Description:
    # Returns the gst filter string for the sink when we want to record
    # Sets the filter element name to that given
    def get_gst_filter_string_for_gst_sink_record( self, name ):
        # return "wavenc ! giostreamsink name=%s" % name
        #return "wavenc ! filesink name=%s location=test.wav" 
        return "wavenc ! filesink name=%s location=test.wav" 

    ##
    # Descripiton:
    # Creates a new audio_object_t from the audio data in the 
    # memory output stream. This will also store this new object
    # into the DB
    def create_new_audio_object_from_memory_output_stream( self ):
        audio_object = self.gst_gio_output_memory_stream.get_contents()
        return audio_object

    ##
    # Description:
    # Resets the memory output stream
    def reset_memory_output_stream( self ) :
        # print "In reset_memory_output_stream"
        # if we have an output stream already. close it
        if self.gst_gio_output_memory_stream is not None:
            self.gst_gio_output_memory_stream.close()

        # ok, here we will create a new memry poutput stream and store it.
        self.gst_gio_output_memory_stream = gio.MemoryOutputStream()
        
        # Now we need to set this as the stream to use in the pipeline
        self.gst_sink_object.set_property( 'stream', self.gst_gio_output_memory_stream )
        

