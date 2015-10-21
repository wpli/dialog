##
# tbh_speech_output contains speech synthesizer
# need to have pyfestival installed
# checkout from:
# svn checkout http://pyfestival.googlecode.com/svn/trunk/ pyfestival-read-only 
# >> sudo python setup.py install

##    * functions
##          o output_as_speech( text )

import festival

class speech_synthesizer:
    def __init__( self ):
        self.synthesizer = festival.Festival()

    def output_as_speech( self, text ):
        #speech_synthesizer = festival.Festival()
        # Speech synthesizer speaks the text provided to it
        self.synthesizer = festival.Festival()
        self.synthesizer.say( text )

    def interrupt_synthesizer( self ):
        self.synthesizer.close()


if __name__ == "__main__":
    x = speech_synthesizer()

    x.output_as_speech( "hello" )

    

    
   
