import sys

sys.path.append( '../../tbh_dialog_manager/src' )

import tbh_experiment_controller

import cPickle

if __name__ == '__main__':
    f = open( 'pickles.txt', 'r' )
    x = f.readlines()

    short_files = []
    for i in x:
        print i.strip()
        pkl = cPickle.load( open( i.strip(), 'r' ) )
        print len( pkl )
        if len( pkl ) < 39:
            short_files.append( i.split('/')[1] )


    print " ".join( short_files )



                           
