

from tbh_audio_listener import *

import gobject
import threading
import pygtk, gtk
import pickle

def handler( audio_object ):
    try:
        count_file = open( 'count.pkl', 'r' )
        count = pickle.load( count_file )
        count_file.close()
    except:
        count = 0
        count_file = open( 'count.pkl', 'w' )
        pickle.dump( count, count_file )
        

        

    f = open( str(count) + '.wav', 'w')
    f.write( audio_object )
    f.close()
    
    #Increment the counter
    count = count + 1
    count_file = open( 'count.pkl', 'w' )
    pickle.dump( count, count_file )
    count_file.close()


al = tbh_audio_listener_t()
al.add_audio_listener_handler( handler )


al_thread = threading.Thread( target=al.run )
al_thread.start()


gtk.gdk.threads_init()
gtk.main()


#al.run()


#loop = gobject.MainLoop()
#loop.run()

