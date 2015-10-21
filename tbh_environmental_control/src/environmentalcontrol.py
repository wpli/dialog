#functional
#program that waits for Y/N input, then sends it to arduino
#load environmentalcontrol(for arduino) code onto arduino
#Sebastian Nowak @ CSAIL, July 2011
import serial  
import time
import Tkinter
from Tkinter import *


root = Tkinter.Tk()
root.title("GUI based environmental control")
canvas = Tkinter.Canvas(root, width=600, height=350, bg="white")
canvas.create_text(300, 15, text="GUI Based Environmental Control")
canvas.create_text(300, 33, text="Sebastian Nowak at CSAIL, July 2011")

wut=(0) #infinite loop variable

 # connects to arduino
locations=['/dev/ttyACM0','/dev/ttyACM1','/dev/ttyACM2','/dev/ttyACM3','/dev/ttyACM4','/dev/ttyACM5',
           '/dev/ttyACM6','/dev/ttyACM7','/dev/ttyACM8','/dev/ttyACM9','/dev/ttyACM10','/dev/ttyACM11']    
      
for device in locations:  
    try:  
        print "Trying...",device  
        arduino = serial.Serial(device, 9600)  
        break  
    except:  
        print "Failed to connect on",device     



while wut != 1: #actual loop, activataed once connection is established        
    
    def lampOn():
        print"Lamp on"
        arduino.write("1") # This is the on command     
        time.sleep(1.5)
        arduino.write("N") # N is the off command
        # N makes it so the remote is only pressed for a 
        # limited amount of time.
    b = Button(root, text="Lamp On", command=lampOn)
    b.pack()
    b.place(bordermode=OUTSIDE, height=40, width=100)
    b.place(x=130, y=50)
    
    
    def lampOff():
        print"Lamp off"
        arduino.write("2")
        time.sleep(1.5)
        arduino.write("N")    
    b = Button(root, text="Lamp Off", command=lampOff)
    b.pack()
    b.place(bordermode=OUTSIDE, height=40, width=100)   
    b.place(x=140, y=100)
    
    def fanOn():
        print"Fan on"
        arduino.write("3")
        time.sleep(1.5)
        arduino.write("N")    
    b = Button(root, text="Fan On", command=fanOn)
    b.pack()
    b.place(bordermode=OUTSIDE, height=40, width=120)
    b.place(x=240, y=50)
    
    def fanOff():
        print"Fan off"
        arduino.write("4")
        time.sleep(1.5)
        arduino.write("N")    
    b = Button(root, text="Fan Off", command=fanOff)
    b.pack()
    b.place(bordermode=OUTSIDE, height=40, width=100)
    b.place(x=250, y=100)
    
    def radioOn():
        print"Radio on"
        arduino.write("5")
        time.sleep(1.5)
        arduino.write("N")    
    b = Button(root, text="Radio On", command=radioOn)
    b.pack()
    b.place(bordermode=OUTSIDE, height=40, width=100)
    b.place(x=370, y=50)
    
    def radioOff():
        print"Radio off"
        arduino.write("6")
        time.sleep(1.5)
        arduino.write("N")    
    b = Button(root, text="Radio Off", command=radioOff)
    b.pack()
    b.place(bordermode=OUTSIDE, height=40, width=100)
    b.place(x=360, y=100)
    
    canvas.pack()
    root.mainloop()
   
       
  
