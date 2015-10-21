#!/bin/bash -v 

#gst-launch --gst-plugin-path=. filesrc location=../../testaudio/test.wav ! wavparse ! audioconvert ! audioresample ! audio/x-raw-int, rate=8000, channels=1 ! SAD name=sad sad.activesrc ! wavenc ! filesink location=active.wav

rm noise.wav active.wav

# ver2 double ported
gst-launch --gst-plugin-path=. filesrc location=./test.wav ! wavparse ! audioconvert ! audioresample ! audio/x-raw-int, rate=8000, channels=1 ! SAD threshold=-30 name=sad sad.activesrc ! queue ! wavenc ! filesink location=active.wav sad.noisesrc ! queue ! wavenc ! filesink location=noise.wav

#gst-launch --gst-plugin-path=. filesrc location=../../testaudio/test.wav ! wavparse ! audioconvert ! audioresample ! audio/x-raw-int, rate=8000, channels=1 ! SAD threshold=-30 ! queue ! wavenc ! filesink location=active.wav


