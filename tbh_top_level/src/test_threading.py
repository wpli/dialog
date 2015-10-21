import pygtk
pygtk.require('2.0')

import gtk
import gtk.gdk as gdk
import pango

from threading import Thread, Lock

from random import Random, randint, sample
from time import sleep, time

import os
import sys

pname = sys.argv[0].split(os.sep)[-1]
demo_id = pname.split('.')[0].replace("demo" , '')

def Connect(obj, signal, handler, *args):

  def wrap(handler):
    def wrapper(obj, *args):
      gdk.threads_leave()
      handler(obj, *args)
      gdk.threads_enter()
    #end wrapper
    return wrapper
  #end wrap

  obj.connect(signal, wrap(handler), *args)
#end Connect

class Counting (Thread):

  def __init__(self, Id):
    self.Id = Id
    self.ctrl = True
    self.Running = False
    self.ShowMode = 0
    self.Time = 0
    self.Value = 250
    self.lock = Lock()
    self.lock.acquire()
    self.PRG = Random()
    Thread.__init__(self)
  #end __init__


  def run(self):

    def limit(x, sub, sup):
      if x < sub:
        return sub
      elif x > sup:
        return sup
      else:
        return x
      #end if
    #end limit

    while 1:
      if not self.Running:
        self.lock.acquire()
      #end if
      if not self.ctrl:
        return
      #end if
      OldTime = self.Time
      self.Time = OldTime +  self.PRG.randint(1,20)
      while OldTime < self.Time:
        OldTime += 1
      #end while
      self.Value = limit(self.Value + self.PRG.randint(-5,5) , 0 , 500)
      canvas.Adjust(self.Id, self.Time , self.Value)
    #end while
  #end run

  def Start_Stop(self,ignore):
    if self.Running:
      self.Running = False
    else:
      self.Running = True
      self.lock.release()
    #end if
  #end Start_Stop


  def Quit(self):
    self.ctrl = False
    if not self.Running:
      self.Running = True
      self.lock.release()
    #end if
  #end Quit
#end Counting


Worker = [ Counting(i) for i in xrange(7) ]

for W in sample(Worker,7):
  W.start()
#end for


RowHght = 25

def index2rgb(ix, ColorScale = 3 * 65535 / 5):

  return (ColorScale * (ix & 4) >> 2,
          ColorScale * (ix & 2) >> 1,
          ColorScale * (ix & 1) >> 0)
#end index2rgb


class Canvas(gtk.DrawingArea):

  def __init__(self):

    def On_Expose(canvas, evt):
      gc = canvas.window.new_gc()
      lb = canvas.window.new_gc()
      cm = gc.get_colormap()

      gdk.threads_enter()
      for i in xrange(7):
        color = cm.alloc_color(*index2rgb(i))
        gc.set_foreground(color)
        canvas.window.draw_rectangle(gc, True , 75,  (2 * i + 1) * RowHght , canvas.ThrdInfo[i][1] , RowHght )
        canvas.layout.set_text("%8d" % (canvas.ThrdInfo[i][0],))
        canvas.window.draw_layout(lb, 5 , (2 * i + 1) * RowHght + canvas.TxtPad , canvas.layout)
      #end for
      gdk.threads_leave()
    #end On_Expose

    gtk.DrawingArea.__init__(self)
    self.add_events(gdk.BUTTON_PRESS_MASK)
    self.set_size_request(600, 15 * RowHght)
    self.layout = self.create_pango_layout("")
    desc = self.layout.get_context().get_font_description()
    desc.set_family("Monospace")
    self.TxtPad = desc.get_size() / (2 * pango.SCALE)
    self.ThrdInfo = [ [0 , 250 ][:] for x in range(7) ]
    self.layout.set_font_description(desc)
    Connect(self, "expose_event" , On_Expose)
    Connect(self, "button_press_event" , self.On_Click)
  #end __init__

  def On_Click(self, evnt, info):
    for W in sample(Worker,7):
      W.Start_Stop(None)
    #end for
  #end On_Click

  def Adjust(self, ThrdIx, Time, Value):
    gdk.threads_enter()
    gc = self.window.new_gc()
    lb = self.window.new_gc()
    cm = gc.get_colormap()

    OldValue = self.ThrdInfo[ThrdIx][1]
    if OldValue < Value:
      color = cm.alloc_color(*index2rgb(ThrdIx))
      base = 75 + OldValue
    else:
      color = self.style.bg[0]
      base = 75 + Value
    #end if
    gc.set_foreground(color)
    self.window.draw_rectangle(gc, True , base , (2 * ThrdIx + 1) * RowHght , abs(Value - OldValue)  , RowHght)
    self.layout.set_text("%8d" % (Time,))
    self.window.begin_paint_rect((0, (2 * ThrdIx + 1) * RowHght, 75 , RowHght))
    self.window.draw_layout(lb, 5 , (2 * ThrdIx + 1) * RowHght + self.TxtPad , self.layout)
    self.window.end_paint()
    gdk.flush()
    gdk.threads_leave()
    self.ThrdInfo[ThrdIx] = [Time, Value]
  #end Adjust
#end Canvas

class Frame(gtk.Window):

  def __init__(self,canvas):
    gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
    self.set_title("Thread %s Demonstration" % demo_id)
    Connect(self, "delete_event" , self.On_Delete)
    self.add(canvas)
    canvas.show()
    self.show()
  #end __init__

  def On_Delete(self, widget, evt, data=None):
    for W in sample(Worker,7):
      W.Quit()
    #end for
    for W in sample(Worker,7):
      W.join()
    #end for
    gtk.main_quit()
    return False
  #end On_Delete
#end Frame

gtk.threads_init()
canvas=Canvas()
Win=Frame(canvas)
gtk.threads_enter()
gtk.main()
gtk.threads_leave()
