import sys, os, random
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from PyQt4 import QtCore, QtGui
import PyQt4


import matplotlib
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure



import threading
import Queue
import sys
import time


import numpy

# import the state 
state_file_name =  '../../dialog_system_tools/bin/20120118/decision_process_files/states.txt'
action_file_name =  '../../dialog_system_tools/bin/20120118/decision_process_files/actions.txt'


# data annotation
LABEL_THRESHOLD = 0.03

# for data annotation - label on plot, or use legend?
LABEL_ON_PLOT = True



# This will be in the same thread as the tbh_output_interface
# The threading functions do not seem necessary right now
'''
class tbh_pomdp_data_viz_thread:
    def __init__( self ):
        """
        Start the GUI and the asynchronous threads. We are in the main
        (original) thread of the application, which will later be used by
        the GUI. We spawn a new thread for the worker.
        """
        # Create the queue
        self.queue = Queue.Queue()

        # Set up the GUI part
        self.state_matplotlib = tbh_pomdp_data_viz_t( self.queue, self.endApplication )
        self.state_matplotlib.show()

        # A timer to periodically call periodicCall :-)
        self.queue_timer = QTimer()

        # Start the timer -- this replaces the initial call 
        # to periodicCall
        self.queue_timer.start(100)
        QObject.connect(self.queue_timer, SIGNAL("timeout()"), \
                                         self.periodicCall)



        # Set up the thread to do asynchronous I/O
        # More can be made if necessary
        self.running = 1
        
    	self.thread = threading.Thread( target=self.worker_thread )
        self.thread.start()

        # Start the periodic call in the GUI to check if the queue contains
        # anything
        self.periodicCall()


    def periodicCall(self):
        """
        Check every 100 ms if there is something new in the queue.
        """       
        self.state_matplotlib.process_incoming()
        #if not self.running:
        #    root.quit()
      
    def endApplication(self):
        self.running = 0

    def worker_thread( self ):

        """
        This is where we handle the asynchronous I/O. 
        """

        # rand = random.Random()
        
        #while self.running:
        #    # To simulate asynchronous I/O, we create a random number at
        #    # random intervals. Replace the following 2 lines with the real
        #    # thing.
        #    time.sleep( rand.random() * 1 )
        #    msg = rand.random()
        #    self.queue.put(msg)


'''

class tbh_pomdp_data_viz_t(QMainWindow):

    def __init__(self, queue, end_command, parent=None, playback_results=False, organized_dialog_entries=None ):

        if playback_results:
            self.dialog_logfile = sys.argv[1]
            self.dialog_type = sys.argv[2]
            self.organized_dialog_entries = organized_dialog_entries

        else:
            self.dialog_logfile = ""


        # Initialize as an empty list
        self.belief_vector = []

        self.state_code_list = get_state_code_list( state_file_name )
        self.action_code_list = get_code_list( action_file_name )


        self.queue = queue
        self.end_command = end_command



        QMainWindow.__init__(self, parent)
        self.setWindowTitle('Dialog POMDP state probabilities')


        self.create_menu()
        self.create_main_frame()
        self.create_status_bar()

        self.textbox.setText('0.01 0.01 0.07 0.01 0.01 0.01 0.01 0.01 0.01 0.03')
        self.on_draw()

    def save_plot(self):
        file_choices = "PNG (*.png)|*.png"
        
        path = unicode(QFileDialog.getSaveFileName(self, 
                        'Save file', '', 
                        file_choices))
        self.slider.setRange(1, 100)
        self.slider.setValue(70)
        self.slider.setTracking(True)
        self.slider.setTickPosition(QSlider.TicksBothSides)
        self.connect(self.slider, SIGNAL('valueChanged(int)'), self.on_draw)
        
        #
        # Layout with box sizers
        # 
        hbox = QHBoxLayout()
        
        #for w in [  self.textbox, self.draw_button, self.grid_cb,
        #            slider_label, self.slider]:
        #    hbox.addWidget(w)
        #    hbox.setAlignment(w, Qt.AlignVCenter)

        for w in [  self.grid_cb, slider_label, self.slider]:
            hbox.addWidget(w)
            hbox.setAlignment(w, Qt.AlignVCenter)

        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)
        vbox.addWidget(self.mpl_toolbar)
        vbox.addLayout(hbox)
        
        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.main_frame)
    
    def on_about(self):
        msg = """ A demo of using PyQt with matplotlib:
        
         * Use the matplotlib navigation bar
         * Add values to the text box and press Enter (or click "Draw")
         * Show or hide the grid
         * Drag the slider to modify the width of the bars
         * Save the plot to a file using the File menu
         * Click on a bar to receive an informative message
        """
        QMessageBox.about(self, "About the demo", msg.strip())
    
    def on_pick(self, event):
        # The event received here is of the type
        # matplotlib.backend_bases.PickEvent
        #
        # It carries lots of information, of which we're using
        # only a small amount here.
        # 
        box_points = event.artist.get_bbox().get_points()
        msg = "You've clicked on a bar with coords:\n %s" % box_points
        
        QMessageBox.information(self, "Click!", msg)





    def on_draw_button( self ):
        self.draw_from_data( None )


    def on_update_button( self ):
        #print "Loading %s" %( self.dialog_logfile )
        #import cPickle
        #f = open( self.dialog_logfile, 'r' )
        #self.simulation_results = cPickle.load( f ) 

        if self.dialog_type == "all_incorrect":
            dialog_number = int( self.dialog_number_textbox.text() )
            turn_number = int( self.turn_number_textbox.text() )
            self.draw_from_data( self.organized_dialog_entries.incorrect_dialog_list[dialog_number]['turn_list'][turn_number]['pomdp_dict']['final_belief'] )
            print_turn_data_information( \
                self.organized_dialog_entries.incorrect_dialog_list, \
                    dialog_number, turn_number, self.action_code_list )

        elif self.dialog_type == "all_correct":
            dialog_number = int( self.dialog_number_textbox.text() )
            turn_number = int( self.turn_number_textbox.text() )
            self.draw_from_data( self.organized_dialog_entries.correct_dialog_list[dialog_number]['turn_list'][turn_number]['pomdp_dict']['final_belief'] )
            print_turn_data_information( \
                self.organized_dialog_entries.correct_dialog_list, \
                    dialog_number, turn_number, self.action_code_list )




        elif self.dialog_type == "four_long":
            dialog_number = int( self.dialog_number_textbox.text() )
            turn_number = int( self.turn_number_textbox.text() )
            self.draw_from_data( self.organized_dialog_entries.four_long_dialog_list[dialog_number]['turn_list'][turn_number]['pomdp_dict']['final_belief'] )
            print_turn_data_information( \
                self.organized_dialog_entries.four_long_dialog_list, \
                    dialog_number, turn_number, self.action_code_list )





    def on_increase_dialog_button( self ):
        current_dialog_number = int( self.dialog_number_textbox.text() )
        new_dialog_number = current_dialog_number + 1
        self.dialog_number_textbox.setText( str(new_dialog_number) )
        self.turn_number_textbox.setText( "0" )

        # Execute the actual belief update
        self.on_update_button()




    def on_decrease_dialog_button( self ):
        current_dialog_number = int( self.dialog_number_textbox.text() )
        new_dialog_number = current_dialog_number - 1
        self.dialog_number_textbox.setText( str(max( 0, new_dialog_number) ) )
        self.turn_number_textbox.setText( "0" )

        # Execute the actual belief update
        self.on_update_button()



    def on_increase_turn_button( self ):
        current_turn_number = int( self.turn_number_textbox.text() )
        new_turn_number = current_turn_number + 1
        self.turn_number_textbox.setText( str( new_turn_number ) )

        self.on_update_button()
    

    def on_decrease_turn_button( self ):
        current_turn_number = int( self.turn_number_textbox.text() )
        new_turn_number = current_turn_number - 1
        self.turn_number_textbox.setText( str( max( 0, new_turn_number ) ) )

        self.on_update_button()






    
    def on_draw(self):
        """ Redraws the figure
        """
        

        
        self.data = self.belief_vector
        
        x = range(len(self.data))


        # clear the axes and redraw the plot anew
        #
        self.axes.clear()        
        self.axes.grid(self.grid_cb.isChecked())
        
        self.axes.bar(
            left=x, 
            height=self.data, 
            width=self.slider.value() / 100.0, 
            align='center', 
            alpha=0.44,
            picker=5)


        self.axes.set_ylabel( 'probability' )
        self.axes.set_xlabel( 'state' )
        self.axes.set_xbound( lower=0, upper=96 )
        self.canvas.draw()



        # clear the axes and redraw the plot anew
        #
        #self.axes.clear()        

        #self.axes.set_ylabel( 'Probability' )
        #self.axes.set_xlabel( 'State' )


        #self.axes.grid(self.grid_cb.isChecked())
        
        #self.axes.bar(
        #    left=x, 
        #    height=self.data, 
        #    width=self.slider.value() / 100.0, 
        #    align='center', 
        #    alpha=0.44,
        #    picker=5)
        
        #self.canvas.draw()


        





        # Comment out the sample code
        #str = unicode(self.textbox.text())
        #self.data = map(float, str.split())
        
        #x = range(len(self.data))

        # clear the axes and redraw the plot anew
        #
        #self.axes.clear()        

        #self.axes.set_ylabel( 'Probability' )
        #self.axes.set_xlabel( 'State' )


        #self.axes.grid(self.grid_cb.isChecked())
        
        #self.axes.bar(
        #    left=x, 
        #    height=self.data, 
        #    width=self.slider.value() / 100.0, 
        #    align='center', 
        #    alpha=0.44,
        #    picker=5)
        
        #self.canvas.draw()

    def draw_from_data( self, data=None ):
        if data==None:
            print "I am drawing from the data"
            str = unicode( '0.01 0.02 0.03 0.04 0.05' )
            self.data = map(float, str.split())

        else:
            self.data = data
        
        x = range(len(self.data))

        # clear the axes and redraw the plot anew
        #
        self.axes.clear()        
        self.axes.grid(self.grid_cb.isChecked())
        
        self.axes.bar(
            left=x, 
            height=self.data, 
            width=self.slider.value() / 100.0, 
            align='center', 
            alpha=0.44,
            picker=5)


        self.axes.set_ylabel( 'probability' )
        self.axes.set_xlabel( 'state' )
        self.axes.set_xbound( lower=-1, upper=62 )
        self.axes.set_ybound( lower=0, upper=1 )

        self.annotate_axes()
        self.canvas.draw()

    def annotate_axes( self ):

        # annotate if the item is greater than a certain threshold
        # also, use a "legend" box to present this data
        annotation_letters = \
            [ 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J' ]

        key_states_list = []
        for index, item in enumerate( self.data ):
            if item > LABEL_THRESHOLD:
                key_states_list.append( ( index, item ) )

        print "KEY STATES", key_states_list
        
        state_legend_list = []

        for index, entry in enumerate( key_states_list ):
            
           annotation_string = annotation_letters[ index ]


           legend_string = "%s: %s (%s)" % ( annotation_string, \
                                            self.state_code_list[ entry[0] ], \
                                                 entry[0] )

           #self.axes.annotate( annotation_string, \
           #                        xy=( entry[0], \
           #                         entry[1] ), \
           #                         xytext=( entry[0], \
           #                                      entry[1] ) )
           #


           self.axes.annotate( legend_string, \
                                   xy=( entry[0], \
                                    entry[1] ), \
                                    xytext=( entry[0], \
                                                 entry[1] ), size='x-small' )
           



           state_legend_list.append( legend_string )

        legend_string = "Legend: " + "; ".join( state_legend_list )

        self.legend.setText( legend_string )


                  
                             
    def create_main_frame(self):
        self.main_frame = QWidget()
        
        # Create the mpl Figure and FigCanvas objects. 
        # 5x4 inches, 100 dots-per-inch
        #
        self.dpi = 100
        self.fig = Figure((5.0, 4.0), dpi=self.dpi )


        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)
        
        # Since we have only one plot, we can use add_axes 
        # instead of add_subplot, but then the subplot
        # configuration tool in the navigatFigureion toolbar wouldn't
        # work.                


        self.axes = self.fig.add_subplot(111)

        
        # Bind the 'pick' event for clicking on one of the bars
        #
        self.canvas.mpl_connect('pick_event', self.on_pick)
        
        # Create the navigation toolbar, tied to the canvas
        #
        self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)
        
        # Other GUI controls
        # 
        self.textbox = QLineEdit()
        self.textbox.setMinimumWidth(200)
        self.connect(self.textbox, SIGNAL('editingFinished ()'), self.on_draw)
        
        self.draw_button = QPushButton("&Draw")
        #self.connect(self.draw_button, SIGNAL('clicked()'), self.on_draw)
        self.connect(self.draw_button, SIGNAL('clicked()'), self.on_draw_button)        
        

        # Other features necessary for the dialog review

        dialog_logfile_label = QLabel('Name of Dialog Logfile: ')

        self.dialog_logfile_textbox = QLineEdit()
        self.dialog_logfile_textbox.setMinimumWidth(200)
        self.dialog_logfile_textbox.setText( self.dialog_logfile )

        self.connect(self.dialog_logfile_textbox, \
                         SIGNAL('editingFinished ()'), self.on_draw)




        dialog_number_label = QLabel('Dialog Number: ')
        self.dialog_number_textbox = QLineEdit()
        self.dialog_number_textbox.setText( "0" )
        self.dialog_number_textbox.setMaximumWidth(30)
        self.connect(self.dialog_number_textbox, \
                         SIGNAL('editingFinished ()'), self.on_draw)

        turn_number_label = QLabel('Turn Number: ')
        self.turn_number_textbox = QLineEdit()
        self.turn_number_textbox.setText( "0" )
        self.turn_number_textbox.setMaximumWidth(30)
        self.connect(self.dialog_number_textbox, \
                         SIGNAL('editingFinished ()'), self.on_draw)

        self.update_button = QPushButton("&Update")
        
        self.connect(self.update_button, SIGNAL('clicked()'), self.on_update_button)     
        self.increase_dialog_button = QPushButton(">")
        self.increase_dialog_button.setMaximumWidth(20)
        self.connect(self.increase_dialog_button, SIGNAL('clicked()'), \
                         self.on_increase_dialog_button)     

        self.decrease_dialog_button = QPushButton("<")
        self.decrease_dialog_button.setMaximumWidth(20)
        self.connect(self.decrease_dialog_button, SIGNAL('clicked()'), \
                         self.on_decrease_dialog_button)     


        self.increase_turn_button = QPushButton(">")
        self.increase_turn_button.setMaximumWidth(20)
        self.connect(self.increase_turn_button, SIGNAL('clicked()'), \
                         self.on_increase_turn_button)     



        self.decrease_turn_button = QPushButton("<")
        self.decrease_turn_button.setMaximumWidth(20)
        self.connect(self.decrease_turn_button, SIGNAL('clicked()'), \
                         self.on_decrease_turn_button)     




        self.grid_cb = QCheckBox("Show &Grid")
        self.grid_cb.setChecked(True)
        self.connect(self.grid_cb, SIGNAL('stateChanged(int)'), self.on_draw)
        
        slider_label = QLabel('Bar width (%):')
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(1, 100)
        self.slider.setValue(70)
        self.slider.setTracking(True)
        self.slider.setTickPosition(QSlider.TicksBothSides)
        self.connect(self.slider, SIGNAL('valueChanged(int)'), self.on_draw)
        


        self.legend = QLabel('Legend: ')

        #
        # Layout with box sizers
        # 
        hbox = QHBoxLayout()
        data_explorer_hbox = QHBoxLayout()
        legend_hbox = QHBoxLayout()


        for w in [  self.textbox, \
                        self.draw_button, \
                        self.grid_cb, slider_label, self.slider]:
            hbox.addWidget(w)
            hbox.setAlignment(w, Qt.AlignVCenter)


        for w in [  self.grid_cb, slider_label, self.slider]:
            hbox.addWidget(w)
            hbox.setAlignment(w, Qt.AlignVCenter)


        for w in [ dialog_logfile_label, self.dialog_logfile_textbox, \
                       self.update_button, \
                       dialog_number_label, \
                       self.decrease_dialog_button, \
                       self.dialog_number_textbox, \
                       self.increase_dialog_button, \
                       turn_number_label, \
                       self.decrease_turn_button, \
                       self.turn_number_textbox, \
                       self.increase_turn_button ]:
            data_explorer_hbox.addWidget(w) 
            data_explorer_hbox.setAlignment( w, Qt.AlignLeft )



        



        legend_hbox.addWidget( self.legend )
       
        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)


        vbox.addLayout(legend_hbox)

        vbox.addWidget(self.mpl_toolbar)

        vbox.addLayout(hbox)
        
        vbox.addLayout( data_explorer_hbox )



        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.main_frame)

    def create_status_bar(self):
        self.status_text = QLabel("TBH Resident Interface")
        self.statusBar().addWidget(self.status_text, 1)
        
    def create_menu(self):        
        self.file_menu = self.menuBar().addMenu("&File")
        
        load_file_action = self.create_action("&Save plot",
            shortcut="Ctrl+S", slot=self.save_plot, 
            tip="Save the plot")
        quit_action = self.create_action("&Quit", slot=self.close, 
            shortcut="Ctrl+Q", tip="Close the application")
        
        self.add_actions(self.file_menu, 
            (load_file_action, None, quit_action))
        
        self.help_menu = self.menuBar().addMenu("&Help")
        about_action = self.create_action("&About", 
            shortcut='F1', slot=self.on_about, 
            tip='About the demo')
        
        self.add_actions(self.help_menu, (about_action,))

    def add_actions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def create_action(  self, text, slot=None, shortcut=None, 
                        icon=None, tip=None, checkable=False, 
                        signal="triggered()"):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action



    def process_incoming(self):
        """
        Handle all the messages currently in the queue (if any).
        """
        while self.queue.qsize():
            try:
                desired_action = self.queue.get(0)
                # Check contents of message and do what it says
                # As a test, we simply print it

                #print desired_action
                #self.unit_test()

                if desired_action['action'] == "change_gui_system_state":
                    desired_state = desired_action['action_predicate']
                    self.gui.system_state.setText( \
                        self.gui_system_state_lookup['text'][desired_state] )
                    self.gui.system_state.setStyleSheet( \
                        "QWidget { background-color: %s }" % \
                            self.gui_system_state_lookup['colors'][desired_state])  

                elif desired_action['action'] == "show_output_string":
                    output_string = desired_action['action_predicate']
                    self.gui.system_message.setText( output_string )

                elif desired_action['action'] == "change_phone_system_state":
                    desired_state = desired_action['action_predicate']

                    self.gui.phone_state.setText( \
                        self.phone_state_lookup['text'][desired_state] )

                    self.gui.phone_state.setStyleSheet( \
                        "QWidget { background-color: %s }" % \
                            self.phone_state_lookup['colors'][desired_state])  
                    

            except Queue.Empty:
                pass


    ####### HANDLERS FOR THREADED PROGRAM ##################



    # Description:
    # Just updates the plot
    def update_plot( self, belief ):
        belief_to_plot = belief
        self.draw_from_data( belief_to_plot )

    # Description:
    # Does whatever actions requested by the DM
    def update_belief_handler( self, param_dict ):
        belief_to_plot = param_dict['action_dict']['pomdp_dict']['belief_for_policy']
        current_belief = param_dict['action_dict']['pomdp_dict']['final_belief']
        reset_belief = param_dict['action_dict']['pomdp_dict']['reset_belief']

        self.belief_vector = belief_to_plot

        #print self.belief_vector.shape


        # Plot the belief vector that comes in
        self.draw_from_data( self.belief_vector )
       
        if reset_belief:
            self.status_text.setText( \
                "Terminal action taken - belief has been re-initialized" )           
        else:
            self.status_text.setText( "Terminal action not yet taken" )
            

    def unit_test_reset_belief( self, param_dict ):
        belief_to_plot = param_dict['action_dict']['pomdp_dict']['belief_for_policy']
        current_belief = param_dict['action_dict']['pomdp_dict']['final_belief']
        reset_belief = param_dict['action_dict']['pomdp_dict']['reset_belief']

        self.belief_vector = belief_to_plot

        #print self.belief_vector.shape


        # Plot the belief vector that comes in
        self.draw_from_data( self.belief_vector )
       
        if reset_belief:
            self.status_text.setText( \
                "Terminal action taken - belief has been re-initialized" )           
        else:
            self.status_text.setText( "Terminal action not yet taken" )

def get_state_code_list( state_file ):
    state_code_list = []
    f = open( state_file )
    for line in f.readlines():
        state_name = line.strip()
        state_code_list.append( state_name )    
    f.close()
    print state_code_list
    return state_code_list
    
def get_code_list( code_text_file ):
    code_list = []
    f = open( code_text_file )
    for line in f.readlines():
        code_name = line.strip()
        code_list.append( code_name )    
    f.close()
    #print state_code_list
    return code_list



def print_turn_data_information( dialog_list, dialog_number, turn_number, action_code_list ):
    dialog = dialog_list[dialog_number]

    print "\nDIALOG %s" % dialog_number
    print "Goal State:", dialog['starting_state']

    turn = dialog['turn_list'][turn_number]

    print "Turn %s" % turn_number
    print "Agent's Selected Observation", \
        turn['turn_dict']['observation_choice_description']
    print "Probability of Selected Observation: %s" % ( turn['turn_dict']['observation_choice_probability'] )


    print "Agent's Utterance: %s, Orthography: %s, Confidence Score: %.5f" % (
        turn['turn_dict']['sample_utterance'], \
        turn['turn_dict']['sample_utterance_info']['reference_concept'], \
        turn['turn_dict']['sample_utterance_info']['confidence_score'] )
        

    print "Machine Action:", turn['pomdp_dict']['new_machine_action'], action_code_list[ turn['pomdp_dict']['new_machine_action'] ]





def main():
    app = QApplication(sys.argv)
    form = tbh_pomdp_data_viz_t( None, None, None, True )
    form.show()
    app.exec_()




if __name__ == "__main__":
    main()
