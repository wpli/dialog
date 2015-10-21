

##
# Description:
# Just some python code to play around with gst for my own learning


import gst
import gobject



p = gst.parse_launch( 'filesrc location="/home/velezj/media/music/sample.ogg" ! oggdemux ! vorbisdec ! audioconvert ! audioresample ! audio/x-raw-int ! alsasink' )


# callback for messages
def on_message( gst_bus, message, user_data ):
    print message
    return True


# add callback to bus
p.get_bus().add_watch( on_message, None )


# try to play the pipeline
#p.set_state( gst.STATE_PLAYING )


