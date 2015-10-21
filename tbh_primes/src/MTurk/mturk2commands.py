#!/usr/bin/python

import cPickle
import csv
import re
if __name__ == '__main__':
    csvread = csv.reader(open('mturk_results.csv', 'rb'), delimiter=',', quotechar='"')

    csvlist = []

    # read CSV file into a list
    for row in csvread:
        csvlist.append( row )

    sentence_dict = {}
    for index, item in enumerate( csvlist[0] ):
        sentence_dict[ item ] = []
        for turker in csvlist[1:]:
            line = re.sub('[?.<>!]', '', turker[index])   
            # print line.lower()
            sentence_dict[ item ].append( line.lower() )

    f = open( 'commands.p', 'r' )
    existing_commands_dict = cPickle.load( f )



    # create new dict file
    new_commands_dict = {}
    for key in existing_commands_dict.keys():
        new_commands_dict[ key ] = []


    # now we need to load up the sentences
    for key in sentence_dict.keys():        
        if key in ( "Answer.activities1", "Answer.activities2", "Answer.activities3", "Answer.activities4", "Answer.activities5", "Answer.activities6" ):
            for sentence in sentence_dict[key]:
                if len( sentence ) > 0:
                    new_commands_dict[ 'activities today' ].append( sentence )

        elif "Answer.activitiestom" in key:
            for sentence in sentence_dict[key]:
                if len( sentence ) > 0:
                    new_commands_dict[ 'activities tomorrow' ].append( sentence )
            

        elif "Answer.activitieswed" in key:
            for sentence in sentence_dict[key]:
                if len( sentence ) > 0:
                    new_commands_dict[ 'activities wednesday' ].append( sentence )
                    new_commands_dict[ 'activities monday' ].append( sentence.replace( "wednesday", "monday" ) )
                    new_commands_dict[ 'activities tuesday' ].append( sentence.replace( "wednesday", "tuesday" ) )
                    new_commands_dict[ 'activities thursday' ].append( sentence.replace( "wednesday", "thursday" ) )
                    new_commands_dict[ 'activities friday' ].append( sentence.replace( "wednesday", "friday" ) )
                    new_commands_dict[ 'activities saturday' ].append( sentence.replace( "wednesday", "saturday" ) )
                    new_commands_dict[ 'activities sunday' ].append( sentence.replace( "wednesday", "sunday" ) )

        elif "Answer.breakfast" in key:
            for sentence in sentence_dict[key]:
                if len( sentence ) > 0:
                    new_commands_dict['breakfast today'].append( sentence )

        elif "Answer.date" in key:
            for sentence in sentence_dict[key]:
                if len( sentence ) > 0:
                    new_commands_dict['time date'].append( sentence )

        elif key in ( "Answer.dinner1", "Answer.dinner2", "Answer.dinner3" ):
            for sentence in sentence_dict[key]:
                if len( sentence ) > 0:
                    new_commands_dict['dinner today'].append( sentence )
                
        elif "Answer.dinnertom" in key:
            for sentence in sentence_dict[key]:
                if len( sentence ) > 0:
                    new_commands_dict['dinner tomorrow'].append( sentence )

        elif "Answer.dinnerwed" in key:
            for sentence in sentence_dict[key]:
                if len( sentence ) > 0:
                    new_commands_dict['dinner wednesday'].append( sentence )
                    new_commands_dict[ 'dinner monday' ].append( sentence.replace( "wednesday", "monday" ) )
                    new_commands_dict[ 'dinner tuesday' ].append( sentence.replace( "wednesday", "tuesday" ) )
                    new_commands_dict[ 'dinner thursday' ].append( sentence.replace( "wednesday", "thursday" ) )
                    new_commands_dict[ 'dinner friday' ].append( sentence.replace( "wednesday", "friday" ) )
                    new_commands_dict[ 'dinner saturday' ].append( sentence.replace( "wednesday", "saturday" ) )
                    new_commands_dict[ 'dinner sunday' ].append( sentence.replace( "wednesday", "sunday" ) )

        elif "Answer.hangup" in key:
            for sentence in sentence_dict[key]:
                if len( sentence ) > 0:
                    new_commands_dict['phone hang_up'].append( sentence )
                
        elif key in ( "Answer.lunch1", "Answer.lunch2", "Answer.lunch3" ):
            for sentence in sentence_dict[key]:
                if len( sentence ) > 0:
                    new_commands_dict['lunch today'].append( sentence )

                
        elif "Answer.lunchtom" in key:
            for sentence in sentence_dict[key]:
                if len( sentence ) > 0:
                    new_commands_dict['lunch tomorrow'].append( sentence )

        elif "Answer.lunchtues" in key:
            for sentence in sentence_dict[key]:
                if len( sentence ) > 0:
                    new_commands_dict['lunch tuesday'].append( sentence )
                    new_commands_dict[ 'lunch monday' ].append( sentence.replace( "tuesday", "monday" ) )
                    new_commands_dict[ 'lunch wednesday' ].append( sentence.replace( "tuesday", "tuesday" ) )
                    new_commands_dict[ 'lunch thursday' ].append( sentence.replace( "tuesday", "thursday" ) )
                    new_commands_dict[ 'lunch friday' ].append( sentence.replace( "tuesday", "friday" ) )
                    new_commands_dict[ 'lunch saturday' ].append( sentence.replace( "tuesday", "saturday" ) )
                    new_commands_dict[ 'lunch sunday' ].append( sentence.replace( "tuesday", "sunday" ) )

        elif "Answer.phone" in key:
            for sentence in sentence_dict[key]:
                if len( sentence ) > 0:
                    new_commands_dict['phone make_phone_call'].append( sentence )

        elif "Answer.time" in key:
            for sentence in sentence_dict[key]:
                if len( sentence ) > 0:
                    new_commands_dict['time time'].append( sentence )


        elif key in ( "Answer.weather1", "Answer.weather2", "Answer.weather3", "Answer.weather4", "Answer.weather5", "Answer.weather6" ):
            for sentence in sentence_dict[key]:
                if len( sentence ) > 0:
                    new_commands_dict['weather today'].append( sentence )

                
        elif "Answer.weathertom" in key:
            for sentence in sentence_dict[key]:
                if len( sentence ) > 0:
                    new_commands_dict['weather tomorrow'].append( sentence )

        elif "Answer.lunchthurs" in key:
            for sentence in sentence_dict[key]:
                if len( sentence ) > 0:
                    new_commands_dict['lunch thursday'].append( sentence )
                    new_commands_dict[ 'lunch monday' ].append( sentence.replace( "thursday", "monday" ) )
                    new_commands_dict[ 'lunch wednesday' ].append( sentence.replace( "thursday", "wednesday" ) )
                    new_commands_dict[ 'lunch tuesday' ].append( sentence.replace( "thursday", "tuesday" ) )
                    new_commands_dict[ 'lunch friday' ].append( sentence.replace( "thursday", "friday" ) )
                    new_commands_dict[ 'lunch saturday' ].append( sentence.replace( "thursday", "saturday" ) )
                    new_commands_dict[ 'lunch sunday' ].append( sentence.replace( "thursday", "sunday" ) )


    total = 0
    for key in new_commands_dict.keys():
        total += len (new_commands_dict[key] )
        print total
    print total
    


    g = open( 'turkCommands.p', 'w' )
    cPickle.dump( new_commands_dict, g )
    g.close()



    




