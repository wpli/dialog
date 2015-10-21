/*
 * GStreamer
 * Copyright (C) 2005 Thomas Vander Stichele <thomas@apestaart.org>
 * Copyright (C) 2005 Ronald S. Bultje <rbultje@ronald.bitfreak.net>
 * Copyright (C) 2009 administrator User <<user@hostname.org>>
 * 
 * Permission is hereby granted, free of charge, to any person obtaining a
 * copy of this software and associated documentation files (the "Software"),
 * to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense,
 * and/or sell copies of the Software, and to permit persons to whom the
 * Software is furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
 * DEALINGS IN THE SOFTWARE.
 *
 * Alternatively, the contents of this file may be used under the
 * GNU Lesser General Public License Version 2.1 (the "LGPL"), in
 * which case the following provisions apply instead of the ones
 * mentioned above:
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Library General Public
 * License as published by the Free Software Foundation; either
 * version 2 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Library General Public License for more details.
 *
 * You should have received a copy of the GNU Library General Public
 * License along with this library; if not, write to the
 * Free Software Foundation, Inc., 59 Temple Place - Suite 330,
 * Boston, MA 02111-1307, USA.
 */

/**
 * SECTION:element-SAD
 *
 * Speech Activity Detector (SAD)
 *        - filters incoming audio - zeroing out any
 *          sections considered non-speech.
 *
 * <refsect2>
 * <title>Example launch line</title>
 * |[
 * gst-launch -v -m filesrc location=test.wav ! wavparse ! audioconvert ! audioresample ! audio/x-raw-int, rate=8000, channels=1 ! SAD threshold=-30 name=sad sad.activesrc ! queue ! wavenc ! filesink location=active.wav sad.noisesrc ! queue ! wavenc ! filesink location=noise.wav
 * ]|
 * </refsect2>
 */

#ifdef HAVE_CONFIG_H
#  include <config.h>
#endif

#include <gst/gst.h>

#include <gsl/gsl_errno.h>
#include <gsl/gsl_fft_real.h>

#include <string.h>
#include <math.h>

#include "gstSAD.h"

//#define X_SIGN(x) ((x) >= 0 ? 1 : -1)

#define TAU 40

GST_DEBUG_CATEGORY_STATIC (gst_sad_debug);
#define GST_CAT_DEFAULT gst_sad_debug

/* Filter signals and args */
enum
{
  /* FILL ME */
  LAST_SIGNAL
};

enum
{
  PROP_0,
  PROP_SILENT,
  PROP_FRAMELENGTH,
  PROP_PRESPEECH,
  PROP_MINSPEECH,
  PROP_HOLDOVER,
  PROP_ETHRESHOLD,
  PROP_ENABLENOISEEST,
  PROP_OUTPUTFEATURES
};

#define DEFAULT_SILENT          FALSE
#define DEFAULT_FRAMELENGTH     31744
#define DEFAULT_PRESPEECH      250000
#define DEFAULT_MINSPEECH      100000
#define DEFAULT_HOLDOVER       250000 
#define DEFAULT_ETHRESHOLD      -26.0
#define DEFAULT_ENABLENOISEEST   TRUE
#define DEFAULT_OUTPUTFEATURES   TRUE

/* the capabilities of the inputs and outputs.
 *
 * describe the real formats here.
 */
static GstStaticPadTemplate 
sink_factory = GST_STATIC_PAD_TEMPLATE("sink",
                                       GST_PAD_SINK,
                                       GST_PAD_ALWAYS,
                                       GST_STATIC_CAPS(
                                           "audio/x-raw-int, "
                                             "width = (int) 16, "
                                             "depth = (int) 16, "
                                             "endianness = (int) BYTE_ORDER, "
                                             "channels = (int) 1, "
					     "rate = (int) [8000,48000]")); 

static GstStaticPadTemplate 
src_factory = GST_STATIC_PAD_TEMPLATE("src",
                                      GST_PAD_SRC,
                                      GST_PAD_ALWAYS,
                                      GST_STATIC_CAPS(
                                           "audio/x-raw-int, "
                                             "width = (int) 16, "
                                             "depth = (int) 16, "
                                             "endianness = (int) BYTE_ORDER, "
                                             "channels = (int) 1, "
					     "rate = (int) [8000,48000]"));


GST_BOILERPLATE(GstSAD, gst_sad, GstElement, GST_TYPE_ELEMENT);

static void gst_sad_set_property(GObject *object, guint prop_id,
                                 const GValue *value, GParamSpec *pspec);
static void gst_sad_get_property(GObject *object, guint prop_id,
                                 GValue *value, GParamSpec *pspec);

static gboolean gst_sad_set_caps(GstPad *pad, GstCaps *caps);
static GstFlowReturn gst_sad_chain(GstPad *pad, GstBuffer *buf);

static GstFlowReturn gst_sad_process_data(GstSAD *filter, GstBuffer *buf);
static void gst_sad_stop_processing(GstSAD *filter);

static gboolean gst_sad_sink_event(GstPad *pad, GstEvent *event);

static void gst_sad_update_noise_estimate(GstSAD *filter, GstBuffer *buf);
static void gst_sad_send_noise_update_event(GstSAD *filter, GstClockTime timestamp);

static gboolean gst_sad_frame_based_classify(GstSAD *filter, GstBuffer *buf);

/* Event Handler */
static gboolean
gst_sad_sink_event(GstPad *pad, GstEvent *event)
{
  GstSAD *filter = GST_SAD(GST_OBJECT_PARENT(pad));

  gboolean bRetCode = TRUE;

//DEBUG
//g_print(__FUNCTION__);
//fflush(stdout);

  switch (GST_EVENT_TYPE(event)) {
    case GST_EVENT_EOS:
      // end-of-stream, we should close down all stream leftovers here
      gst_sad_stop_processing(filter);
      break;

    default:
      break;
  }
  
  if (gst_pad_is_linked(filter->activesrcpad)) {
    gst_event_ref(event);
    bRetCode &= gst_pad_push_event(filter->activesrcpad, event);
  }

  if (gst_pad_is_linked(filter->noisesrcpad)) {
    gst_event_ref(event);
    bRetCode &= gst_pad_push_event(filter->noisesrcpad, event);
  }
  
  gst_event_unref(event);

  return bRetCode;
}

/* GObject vmethod implementations */

static void
gst_sad_base_init (gpointer gclass)
{
  GstElementClass *element_class = GST_ELEMENT_CLASS(gclass);
  GstElementDetails element_details = GST_ELEMENT_DETAILS("SAD", "filter", "Speech Activity Detector", "Michael Mason <m.mason@qut.edu.au>");

//DEBUG
//g_print(__FUNCTION__);
//fflush(stdout);

  gst_element_class_set_details(element_class,
                                &element_details);

  gst_element_class_add_pad_template(element_class,
      gst_static_pad_template_get(&src_factory));
  gst_element_class_add_pad_template (element_class,
      gst_static_pad_template_get(&sink_factory));
}

/* initialize the sad's class */
static void
gst_sad_class_init (GstSADClass * klass)
{
  GObjectClass *gobject_class;
  GstElementClass *gstelement_class;

//DEBUG
//g_print(__FUNCTION__);
//fflush(stdout);

  gobject_class = (GObjectClass *) klass;
  gstelement_class = (GstElementClass *) klass;

  gobject_class->set_property = gst_sad_set_property;
  gobject_class->get_property = gst_sad_get_property;

  g_object_class_install_property(gobject_class, PROP_SILENT,
      g_param_spec_boolean("silent", "Silent", 
                           "Produce verbose output ?",
                           FALSE, G_PARAM_READWRITE));

  g_object_class_install_property(gobject_class, PROP_FRAMELENGTH,
      g_param_spec_int("framelength", "FrameLength", 
                       "The duration of a single frame (us)",
		       0, G_MAXINT, DEFAULT_FRAMELENGTH, G_PARAM_READWRITE));

  g_object_class_install_property(gobject_class, PROP_MINSPEECH,
      g_param_spec_int("minspeech", "MinSpeech", 
                       "The minimum duration of activity required to be considered speech (us)",
		       0, G_MAXINT, DEFAULT_MINSPEECH , G_PARAM_READWRITE));

  g_object_class_install_property(gobject_class, PROP_PRESPEECH,
      g_param_spec_int("prespeech", "PreSpeech", 
                       "The duration of signal retained before the first active frame (us)",
		       0, G_MAXINT, DEFAULT_PRESPEECH, G_PARAM_READWRITE));

  g_object_class_install_property(gobject_class, PROP_HOLDOVER,
      g_param_spec_int("holdover", "Holdover", 
                       "The duration of signal retained after the last active frame (us)",
		       0, G_MAXINT, DEFAULT_HOLDOVER, G_PARAM_READWRITE));

  g_object_class_install_property(gobject_class, PROP_ETHRESHOLD,
      g_param_spec_double("threshold", "Threshold",
                          "The minimum energy required for a segment to be considered active (dBov(sine))",
		          -96.0, 0.0, DEFAULT_ETHRESHOLD, G_PARAM_READWRITE));

  g_object_class_install_property(gobject_class, PROP_ENABLENOISEEST,
      g_param_spec_boolean("enable_noise_est", "EnableNoiseEst", 
                           "Use non-active frames to estimate the average noise spectrum",
                           DEFAULT_ENABLENOISEEST, G_PARAM_READWRITE));

  g_object_class_install_property(gobject_class, PROP_OUTPUTFEATURES,
      g_param_spec_boolean("output_features", "OutputFeatures", 
                           "Output frame by frame features and decisions -- development",
                           DEFAULT_OUTPUTFEATURES, G_PARAM_READWRITE));

}

/* initialize the new element
 * instantiate pads and add them to element
 * set pad calback functions
 * initialize instance structure
 */
static void
gst_sad_init(GstSAD *filter,
             GstSADClass *gclass)
{
//DEBUG
//g_print(__FUNCTION__);
//fflush(stdout);

  // Create the sink pad member
  filter->sinkpad = gst_pad_new_from_static_template(&sink_factory, "sink");
  gst_pad_set_setcaps_function(filter->sinkpad,
                               GST_DEBUG_FUNCPTR(gst_sad_set_caps));
  gst_pad_set_getcaps_function(filter->sinkpad,
                                GST_DEBUG_FUNCPTR(gst_pad_proxy_getcaps));
  gst_pad_set_chain_function(filter->sinkpad,
                             GST_DEBUG_FUNCPTR(gst_sad_chain));
  // link events
  gst_pad_set_event_function(filter->sinkpad, gst_sad_sink_event);

  // Create the src pad memeber
  filter->activesrcpad = gst_pad_new_from_static_template (&src_factory, "activesrc");
  gst_pad_set_getcaps_function(filter->activesrcpad,
                               GST_DEBUG_FUNCPTR(gst_pad_proxy_getcaps));

  // Create the src pad memeber
  filter->noisesrcpad = gst_pad_new_from_static_template (&src_factory, "noisesrc");
  gst_pad_set_getcaps_function(filter->noisesrcpad,
                               GST_DEBUG_FUNCPTR(gst_pad_proxy_getcaps));

  // attach the pads to the element
  gst_element_add_pad(GST_ELEMENT(filter), filter->sinkpad);
  gst_element_add_pad(GST_ELEMENT(filter), filter->noisesrcpad);
  gst_element_add_pad(GST_ELEMENT(filter), filter->activesrcpad);
  
  // Set default property values
  filter->silent = DEFAULT_SILENT;
  filter->framelength = DEFAULT_FRAMELENGTH;
  filter->minspeech = DEFAULT_MINSPEECH;
  filter->holdover = DEFAULT_HOLDOVER;
  filter->prespeech = DEFAULT_PRESPEECH;
  filter->threshold = pow(10,(((DEFAULT_ETHRESHOLD - 3.01)/10)))*filter->framelength;
  filter->enable_noise_est = DEFAULT_ENABLENOISEEST;
  filter->output_features = DEFAULT_OUTPUTFEATURES;

  // Initialise custom members

  filter->nState = -1; // -1 represents brand brand new some initilisation needs to occur still

  filter->bufAccumulator = NULL;
  filter->bufLeftOver = NULL;
  filter->bufHistory = NULL;

  filter->nSampleSize = 0;
  filter->nSampleRate = 0;
  filter->nSamplePeriod = 0;
  filter->nFrameLength = 0;

  filter->nHoldoverDuration = 0;

  filter->nNoiseFrameCount = 0;
  filter->bufNoiseBuffer = NULL;

  filter->vecNoiseFrame = NULL;
  filter->vecInputSpec = NULL;
  filter->vecCurrentSpecEst = NULL;

  filter->vecFrame = NULL;
                       
}

static void
gst_sad_set_property(GObject *object, guint prop_id,
                     const GValue *value, GParamSpec *pspec)
{
  GstSAD *filter = GST_SAD(object);

//DEBUG
//g_print(__FUNCTION__);
//fflush(stdout);

  switch (prop_id) {
    case PROP_SILENT:
      filter->silent = g_value_get_boolean(value);
      break;
    case PROP_FRAMELENGTH:
      filter->framelength = g_value_get_int(value);
      break;
    case PROP_PRESPEECH:
      filter->prespeech = g_value_get_int(value);
      break;
    case PROP_MINSPEECH:
      filter->minspeech = g_value_get_int(value);
      break;
    case PROP_HOLDOVER:
      filter->holdover = g_value_get_int(value);
      break;
    case PROP_ETHRESHOLD:
      filter->threshold = pow(10,(((g_value_get_double(value)-3.01)/10)))*filter->framelength;
      break;
    case PROP_ENABLENOISEEST:
      filter->enable_noise_est = g_value_get_boolean(value);
      break;
    case PROP_OUTPUTFEATURES:
      filter->output_features = g_value_get_boolean(value);
      break;
    default:
      G_OBJECT_WARN_INVALID_PROPERTY_ID(object, prop_id, pspec);
      break;
  }
}

static void
gst_sad_get_property(GObject *object, guint prop_id,
                     GValue *value, GParamSpec *pspec)
{
  GstSAD *filter = GST_SAD(object);

//DEBUG
//g_print(__FUNCTION__);
//fflush(stdout);

  switch (prop_id) {
    case PROP_SILENT:
      g_value_set_boolean(value, filter->silent);
      break;
    case PROP_FRAMELENGTH:
      g_value_set_int(value, filter->framelength);
      break;
    case PROP_PRESPEECH:
      g_value_set_int(value, filter->prespeech);
      break;
    case PROP_MINSPEECH:
      g_value_set_int(value, filter->minspeech);
      break;
    case PROP_HOLDOVER:
      g_value_set_int(value, filter->holdover);
      break;
    case PROP_ETHRESHOLD:
      g_value_set_double(value, 10*log10(filter->threshold/filter->framelength) + 3.01);
      break;
    case PROP_ENABLENOISEEST:
      g_value_set_boolean(value, filter->enable_noise_est);
      break;
    case PROP_OUTPUTFEATURES:
      g_value_set_boolean(value, filter->output_features);
      break;
    default:
      G_OBJECT_WARN_INVALID_PROPERTY_ID (object, prop_id, pspec);
      break;
  }
}

/* GstElement vmethod implementations */

/* this function handles the link with other elements */
static gboolean
gst_sad_set_caps(GstPad *pad, GstCaps *caps)
{
  GstSAD *filter;

  gboolean bRetCode = TRUE;

//DEBUG
//g_print(__FUNCTION__);
//fflush(stdout);

  // find the owner of the current pad and try to set
  // all the other pads to the same caps
   
  filter = GST_SAD(gst_pad_get_parent(pad));

  if (pad == filter->activesrcpad) {
    bRetCode &= gst_pad_set_caps(filter->noisesrcpad, caps);
    bRetCode &= gst_pad_set_caps(filter->sinkpad, caps);
  }

  if (pad == filter->noisesrcpad) {
    bRetCode &= gst_pad_set_caps(filter->sinkpad, caps);
    bRetCode &= gst_pad_set_caps(filter->activesrcpad, caps);
  }  

  if (pad == filter->sinkpad) {
    bRetCode &= gst_pad_set_caps(filter->activesrcpad, caps);
    bRetCode &= gst_pad_set_caps(filter->noisesrcpad, caps);
  }

  gst_object_unref(filter);

  return bRetCode;
}

/* chain function
 * this function does the actual processing
 */
static GstFlowReturn
gst_sad_chain(GstPad *pad, GstBuffer *buf)
{
  GstFlowReturn eRetCode = GST_FLOW_OK;
  GstSAD *filter;

//DEBUG
//g_print(__FUNCTION__);
//fflush(stdout);

  filter = GST_SAD(GST_OBJECT_PARENT(pad));
 
  if (filter->silent == FALSE) {

    if (buf->size > 0) {
      eRetCode = gst_sad_process_data(filter, buf);
      //eRetCode = gst_pad_push(filter->activesrcpad, buf);
    }
    else {
      g_print("Zero size buffer - discarding");
      gst_buffer_unref(buf);
    }

    if (eRetCode != GST_FLOW_OK) {
      // something went wrong - signal an error
      GST_ELEMENT_ERROR(GST_ELEMENT (filter), STREAM, FAILED, (NULL), (NULL));
    }
  }
  else {
    eRetCode = gst_pad_push(filter->activesrcpad, buf);
  }

  return eRetCode;
}


/* entry point to initialize the plug-in
 * initialize the plug-in itself
 * register the element factories and other features
 */
static gboolean
sad_init(GstPlugin *sad)
{
//DEBUG
//g_print(__FUNCTION__);
//fflush(stdout);

  // debug category for fltering log messages
  GST_DEBUG_CATEGORY_INIT(gst_sad_debug, "SAD", 0, "Speech Activity Detector");

  return gst_element_register(sad, "SAD", GST_RANK_NONE, GST_TYPE_SAD);
}

/* gstreamer looks for this structure to register SADs
 */
GST_PLUGIN_DEFINE (
    GST_VERSION_MAJOR,
    GST_VERSION_MINOR,
    "SAD",
    "Speech Activity Detector",
    sad_init,
    VERSION,
    "LGPL",
    "GStreamer",
    "http://gstreamer.net/"
)

/* The actual meat of the SAD algorithm */
static GstFlowReturn
gst_sad_process_data(GstSAD *filter, GstBuffer *buf)
{
  gint16 i = 0;
  gint16 nElements;
  gint16 nFrames;

  GstFlowReturn eRetCode = GST_FLOW_OK;
  
  GstBuffer *bufFrame = NULL;
  GstBuffer *tempbuf = NULL;
  GstBuffer *noisebuf = NULL;
  GstBuffer *outbuf = NULL;

//DEBUG
//g_print(__FUNCTION__);
//fflush(stdout);

  // Initialise empty buffers needed for the first time
  if (filter->nState < 0) {
    // Create LeftOver buffer to carry data unused in one call to the next call
    filter->bufLeftOver = gst_buffer_new();
    gst_buffer_copy_metadata(filter->bufLeftOver, buf, 
                             GST_BUFFER_COPY_FLAGS | GST_BUFFER_COPY_CAPS );
    filter->bufLeftOver->timestamp = 0;
    filter->bufLeftOver->duration = 0;

    // Create History buffer to store frames which have not been decided on yet
    filter->bufHistory = gst_buffer_new();
    gst_buffer_copy_metadata(filter->bufHistory, buf, 
                             GST_BUFFER_COPY_FLAGS | GST_BUFFER_COPY_CAPS );
    filter->bufHistory->timestamp = 0;
    filter->bufHistory->duration = 0;
 
    // Initialise memeber variables based on run time buffer caps
    { 
      GstStructure *poCap = NULL;
      gint tmp;

      poCap = gst_caps_get_structure(GST_BUFFER_CAPS(filter->bufLeftOver),0);
      
      gst_structure_get_int(poCap, "rate", &tmp);
      filter->nSampleRate = (gint16) tmp;
      gst_structure_get_int(poCap, "width", &tmp);
      filter->nSampleSize = (gint16) tmp;
      filter->nSampleSize /= 8;
      filter->nSamplePeriod = (gdouble)(1000000)/(filter->nSampleRate);
      filter->nFrameLength = filter->framelength / filter->nSamplePeriod;

      fprintf(stderr,"nSampleRate %u, nFrame length %f nSamplePeriod %d\n", filter->nSampleRate, filter->nFrameLength, filter->nSamplePeriod );

      // fprintf(stderr,"nSampleRate %u, nFrame length %f nSamplePeriod %d\n", filter->nSampleRate, filter->nSamplePeriod, filter->nFrameLength );
      // fprintf(stderr, "Hello world\n");
      filter->vecFrame = (gdouble *) g_malloc0(filter->nFrameLength * sizeof(gdouble));
    }
    
    filter->nState = 0;
  }

  // Append the new buffer with the leftovers
  filter->bufAccumulator = gst_buffer_merge(filter->bufLeftOver, buf);
  gst_buffer_copy_metadata(filter->bufAccumulator, filter->bufLeftOver,
                           GST_BUFFER_COPY_FLAGS | GST_BUFFER_COPY_CAPS );
  gst_buffer_unref(filter->bufLeftOver);
  gst_buffer_unref(buf);

  
  // Create a new output buffer
  outbuf = gst_buffer_new();
  gst_buffer_copy_metadata(outbuf, filter->bufAccumulator, 
                           GST_BUFFER_COPY_FLAGS | GST_BUFFER_COPY_CAPS );
  outbuf->timestamp = filter->bufAccumulator->timestamp;
  outbuf->duration = 0;

  // Process each waiting in the accumulator
  nElements = GST_BUFFER_SIZE(filter->bufAccumulator) / filter->nSampleSize;
  nFrames = nElements / filter->nFrameLength;
  for (i = 0; i < nFrames; i++) {
    bufFrame = gst_buffer_create_sub(filter->bufAccumulator, 
                                     i * filter->nSampleSize * filter->nFrameLength, 
                                     filter->nFrameLength * filter->nSampleSize);
    gst_buffer_copy_metadata(bufFrame, filter->bufAccumulator,
                             GST_BUFFER_COPY_FLAGS | GST_BUFFER_COPY_CAPS );
    bufFrame->timestamp = filter->bufAccumulator->timestamp + i*filter->nFrameLength*filter->nSamplePeriod;
    bufFrame->duration = filter->nFrameLength * filter->nSamplePeriod;

    {// state machine for activity detector

      gboolean bActiveFrame = FALSE;

      bActiveFrame = gst_sad_frame_based_classify(filter, bufFrame);

      // Smooth the decisions

      switch (filter->nState) {
      case 0:
        // Listening state
        //g_print("(0) listening\n");
        tempbuf = gst_buffer_merge(filter->bufHistory, bufFrame);
        gst_buffer_copy_metadata(tempbuf, filter->bufHistory,
                                 GST_BUFFER_COPY_FLAGS | GST_BUFFER_COPY_CAPS );
        gst_buffer_unref(filter->bufHistory);
        gst_buffer_unref(bufFrame);
        filter->bufHistory = tempbuf;

        if (bActiveFrame) {
          filter->nState = 1;
	}
	else {
          if (filter->bufHistory->duration > filter->prespeech) {

	    if ((filter->enable_noise_est) || (gst_pad_is_linked(filter->noisesrcpad)) )  {
              // Provided the non-active frames to the noise estimator
	      noisebuf = gst_buffer_create_sub(filter->bufHistory, 0,
                                               GST_BUFFER_SIZE(filter->bufHistory)-filter->prespeech/filter->nSamplePeriod*filter->nSampleSize);
	      gst_buffer_copy_metadata(noisebuf, filter->bufHistory,
                                       GST_BUFFER_COPY_FLAGS | GST_BUFFER_COPY_CAPS );
	      noisebuf->duration = filter->bufHistory->duration - filter->prespeech;

	      if (filter->enable_noise_est) {
                gst_sad_update_noise_estimate(filter, noisebuf);
	      }

	      if (gst_pad_is_linked(filter->noisesrcpad)) {
		gst_buffer_ref(noisebuf);
		gst_pad_push(filter->noisesrcpad, noisebuf);
	      }

	      gst_buffer_unref(noisebuf);
	    }

	    tempbuf = gst_buffer_create_sub(filter->bufHistory,
                          GST_BUFFER_SIZE(filter->bufHistory)-filter->prespeech/filter->nSamplePeriod*filter->nSampleSize,
			  filter->prespeech/filter->nSamplePeriod*filter->nSampleSize);
            gst_buffer_copy_metadata(tempbuf, filter->bufHistory,
                                     GST_BUFFER_COPY_FLAGS | GST_BUFFER_COPY_CAPS );
            tempbuf->duration = filter->prespeech;
            tempbuf->timestamp = filter->bufHistory->timestamp + filter->bufHistory->duration - filter->prespeech;
            gst_buffer_unref(filter->bufHistory);
	    filter->bufHistory = tempbuf;
	  }
	}
        break;
      case 1:
        // Speech Onset possibility
	// g_print("(1) speech onset\n");
        tempbuf = gst_buffer_merge(filter->bufHistory, bufFrame);
        gst_buffer_copy_metadata(tempbuf, filter->bufHistory,
                                 GST_BUFFER_COPY_FLAGS | GST_BUFFER_COPY_CAPS );
        gst_buffer_unref(filter->bufHistory);
        gst_buffer_unref(bufFrame);
        filter->bufHistory = tempbuf;

        if (bActiveFrame) {
          if (filter->bufHistory->duration > filter->prespeech + filter->minspeech) {
            tempbuf = gst_buffer_merge(outbuf, filter->bufHistory);
            gst_buffer_copy_metadata(tempbuf, outbuf,
                                     GST_BUFFER_COPY_FLAGS | GST_BUFFER_COPY_CAPS );
            gst_buffer_unref(outbuf);
            gst_buffer_unref(filter->bufHistory);
            outbuf = tempbuf;
            filter->nState = 2;

            if (filter->enable_noise_est) {
              gst_sad_send_noise_update_event(filter, filter->bufHistory->timestamp);
	    }
	  }
	}
	else {
          // dropped out again (NB: does not trim the length of the history)
	  filter->nState = 0;
	}
	break;
      case 2:
        // Active Speech 
        // g_print("(2) active speech\n");
        tempbuf = gst_buffer_merge(outbuf, bufFrame);
        gst_buffer_copy_metadata(tempbuf, outbuf,
                                 GST_BUFFER_COPY_FLAGS | GST_BUFFER_COPY_CAPS );
        gst_buffer_unref(outbuf);
        gst_buffer_unref(bufFrame);
        outbuf = tempbuf;

        if (!bActiveFrame) {
          filter->nHoldoverDuration = filter->framelength;
	  filter->nState = 3;
	}        
        break;
      case 3:
        // Holdover State
        // g_print("(3) holdover\n");
        tempbuf = gst_buffer_merge(outbuf, bufFrame);
        gst_buffer_copy_metadata(tempbuf, outbuf,
                                 GST_BUFFER_COPY_FLAGS | GST_BUFFER_COPY_CAPS );
        gst_buffer_unref(outbuf);
        gst_buffer_unref(bufFrame);
        outbuf = tempbuf;

        if (!bActiveFrame) {
          filter->nHoldoverDuration += filter->framelength;
	}
	else {
          filter->nHoldoverDuration = 0;
          filter->nState = 2;
	}

	if (filter->nHoldoverDuration > filter->holdover) {
          filter->bufHistory = gst_buffer_new();
          gst_buffer_copy_metadata(filter->bufHistory, outbuf, 
                                   GST_BUFFER_COPY_FLAGS | GST_BUFFER_COPY_CAPS );
          filter->bufHistory->timestamp = outbuf->timestamp + outbuf->duration;
	  filter->bufHistory->duration = 0;
	  filter->nState = 0;

          // Also SIGNAL downstream that the current active segment was completed ...
          // using a custon signal "slice" which the summitsink element knows
          g_print("End of Active Speech detected\n");


	  g_print("Posting application message\n");
	  gst_element_post_message(GST_ELEMENT_CAST(filter),
            gst_message_new_application(GST_OBJECT_CAST(filter),
              gst_structure_new("end_of_segment",
				"end_timestamp", G_TYPE_UINT64, (guint64) filter->bufHistory->timestamp, 
                                  NULL)));
	  
	  g_print("Action: Pushing downstream event to trigger recognition\n");
          gst_pad_push_event(filter->activesrcpad,
		             gst_event_new_custom(GST_EVENT_CUSTOM_DOWNSTREAM,
					          gst_structure_empty_new("slice")));

	}
        break;
      default:
        g_assert(FALSE);
      }
    } // state machine context
  }  // frame loop

  // Store unprocessed data in the LeftOver buffer
  filter->bufLeftOver = gst_buffer_create_sub(filter->bufAccumulator, 
                                              i*filter->nSampleSize*filter->nFrameLength,
                                              GST_BUFFER_SIZE(filter->bufAccumulator) - i*filter->nSampleSize*filter->nFrameLength);
  filter->bufLeftOver->timestamp = filter->bufAccumulator->timestamp + i*filter->nFrameLength*filter->nSamplePeriod;
  filter->bufLeftOver->duration = GST_BUFFER_SIZE(filter->bufLeftOver) * filter->nSamplePeriod / filter->nSampleSize;


  /*
  //DEBUG
  filter->bufLeftOver = gst_buffer_new();
  gst_buffer_copy_metadata(filter->bufLeftOver, filter->bufAccumulator,
                           GST_BUFFER_COPY_FLAGS | GST_BUFFER_COPY_CAPS);

  filter->bufLeftOver->timestamp = 0;
  filter->bufLeftOver->duration = 0;
  */

  gst_buffer_unref(filter->bufAccumulator);

  
  outbuf->timestamp = GST_CLOCK_TIME_NONE;
  outbuf->duration = -1;
 
  if (gst_pad_is_linked(filter->activesrcpad)) {
    eRetCode += gst_pad_push (filter->activesrcpad, outbuf);
  }

  return eRetCode;
}

static void 
gst_sad_stop_processing(GstSAD *filter)
{
  if (filter->nState < 2) {
    gst_pad_push(filter->activesrcpad, filter->bufLeftOver);
    
    gst_buffer_unref(filter->bufHistory);
  }
  else {
    gst_buffer_unref(filter->bufLeftOver);
  }
  
  filter->nState = -1;
}


static void
gst_sad_update_noise_estimate(GstSAD *filter, GstBuffer *buf)
{
  gint i, j;
  gint nElements = 0, nFrames = 0;

  GstBuffer *bufTemp = NULL;
  GstBuffer *bufFrame = NULL;

//DEBUG
//g_print(__FUNCTION__);
//fflush(stdout);


  if (filter->bufNoiseBuffer == NULL) {
    filter->bufNoiseBuffer = gst_buffer_new();
    gst_buffer_copy_metadata(filter->bufNoiseBuffer, buf, 
                             GST_BUFFER_COPY_FLAGS | GST_BUFFER_COPY_CAPS );
    filter->bufNoiseBuffer->timestamp = buf->timestamp;
    filter->bufNoiseBuffer->duration = 0;

    filter->vecNoiseFrame = g_malloc0(filter->nFrameLength * sizeof(gdouble));
    filter->vecInputSpec = g_malloc0(((filter->nFrameLength >> 1) + 1) * sizeof(gdouble));
    filter->vecCurrentSpecEst = g_malloc0(((filter->nFrameLength >> 1) + 1) * sizeof(gdouble));
  }

  // Append the new buffer with the leftovers
  bufTemp = gst_buffer_merge(filter->bufNoiseBuffer, buf);
  gst_buffer_copy_metadata(bufTemp, filter->bufNoiseBuffer,
                           GST_BUFFER_COPY_FLAGS | GST_BUFFER_COPY_CAPS );
  gst_buffer_unref(filter->bufNoiseBuffer);

  filter->bufNoiseBuffer = bufTemp;
  bufTemp = NULL;

  // Process each waiting in the accumulator
  nElements = GST_BUFFER_SIZE(filter->bufNoiseBuffer) / filter->nSampleSize;
  nFrames = nElements / filter->nFrameLength;
  for (i = 0; i < nFrames; i++) {
    bufFrame = gst_buffer_create_sub(filter->bufNoiseBuffer, 
                                     i * filter->nSampleSize * filter->nFrameLength, 
                                     filter->nFrameLength * filter->nSampleSize);
    gst_buffer_copy_metadata(bufFrame, filter->bufNoiseBuffer,
                             GST_BUFFER_COPY_FLAGS | GST_BUFFER_COPY_CAPS );
    bufFrame->timestamp = filter->bufNoiseBuffer->timestamp + i*filter->nFrameLength*filter->nSamplePeriod;
    bufFrame->duration = filter->nFrameLength * filter->nSamplePeriod;

    for (j = 0; j < filter->nFrameLength; j++) {
      filter->vecNoiseFrame[j] = ((gdouble) (*(((gint16 *) GST_BUFFER_DATA(bufFrame)) + j))) / G_MAXINT16; 
    }
    gst_buffer_unref(bufFrame);

    // PROCESS FRAME HERE

    //fprintf(stderr,"I am about to be called\n");
    //fprintf(stderr,"vecNoiseFrame=%d nFrameLength=%d\n", filter->vecNoiseFrame, filter->nFrameLength);


    gsl_fft_real_radix2_transform(filter->vecNoiseFrame, 1, filter->nFrameLength);
    
    //fprintf(stderr,"Done\n");
    // Convert to Magnitude
    filter->vecInputSpec[0] = filter->vecNoiseFrame[0] * filter->vecNoiseFrame[0];

    for (j = 1; j < (filter->nFrameLength >> 1); j++) {
      filter->vecInputSpec[j] = filter->vecNoiseFrame[j] * filter->vecNoiseFrame[j] +
	filter->vecNoiseFrame[filter->nFrameLength - j] * filter->vecNoiseFrame[filter->nFrameLength - j];
    }

    filter->vecInputSpec[(filter->nFrameLength >> 1)] = filter->vecNoiseFrame[(filter->nFrameLength >> 1)] 
      * filter->vecNoiseFrame[(filter->nFrameLength >> 1)];

    filter->nNoiseFrameCount++;
    if (filter->nNoiseFrameCount > TAU) {
      for (j = 0; j < (filter->nFrameLength >> 1) + 1; j++) {
        filter->vecCurrentSpecEst[j] = filter->vecCurrentSpecEst[j] * (1-1.0/TAU) + filter->vecInputSpec[j] * (1.0/TAU);
      }
    }
    else if (filter->nNoiseFrameCount == TAU) {
      for (j = 0; j < (filter->nFrameLength >> 1) + 1; j++) {
        filter->vecCurrentSpecEst[j] = (filter->vecCurrentSpecEst[j] + filter->vecInputSpec[j]) * (1.0/TAU);
      }
    }
    else {
      for (j = 0; j < (filter->nFrameLength >> 1) + 1; j++) {
        filter->vecCurrentSpecEst[j] = (filter->vecCurrentSpecEst[j] + filter->vecInputSpec[j]);
      }
    } 

  }

  // Store unprocessed data in the LeftOver buffer
  bufTemp = gst_buffer_create_sub(filter->bufNoiseBuffer, 
                                  i*filter->nSampleSize*filter->nFrameLength,
                                  GST_BUFFER_SIZE(filter->bufNoiseBuffer) - i*filter->nSampleSize*filter->nFrameLength);
  bufTemp->timestamp = filter->bufNoiseBuffer->timestamp + i*filter->nFrameLength*filter->nSamplePeriod;
  bufTemp->duration = GST_BUFFER_SIZE(bufTemp) * filter->nSamplePeriod / filter->nSampleSize;
  gst_buffer_copy_metadata(bufTemp, filter->bufNoiseBuffer,
                           GST_BUFFER_COPY_FLAGS | GST_BUFFER_COPY_CAPS);
  gst_buffer_unref(filter->bufNoiseBuffer);
  filter->bufNoiseBuffer = bufTemp;
  bufTemp = NULL;

}

static void
gst_sad_send_noise_update_event(GstSAD *filter, GstClockTime timestamp)
{
  GstStructure *s;
  GValue v = {0, };
  GValue *a = NULL;
  gint i;
  GstEvent *e;

  //DEBUG
  g_print("Pushing noise spectrum update event downstream - <%"G_GUINT64_FORMAT">\n", timestamp);

  gst_element_post_message(GST_ELEMENT_CAST(filter),
            gst_message_new_application(GST_OBJECT_CAST(filter),
              gst_structure_new("start_of_segment",
				"start_timestamp", G_TYPE_UINT64, (guint64) timestamp, 			
				NULL)));

  if (filter->bufNoiseBuffer == NULL) {
    filter->bufNoiseBuffer = gst_buffer_new();
    gst_buffer_copy_metadata(filter->bufNoiseBuffer, filter->bufLeftOver, 
                             GST_BUFFER_COPY_FLAGS | GST_BUFFER_COPY_CAPS );
    filter->bufNoiseBuffer->timestamp = filter->bufLeftOver->timestamp;
    filter->bufNoiseBuffer->duration = 0;

    filter->vecNoiseFrame = g_malloc0(filter->nFrameLength * sizeof(gdouble));
    filter->vecInputSpec = g_malloc0(((filter->nFrameLength >> 1) + 1) * sizeof(gdouble));
    filter->vecCurrentSpecEst = g_malloc0(((filter->nFrameLength >> 1) + 1) * sizeof(gdouble));
  }

  s = gst_structure_new("noise_spectrum",
			  "timestamp", G_TYPE_UINT64, (guint64) timestamp,
			  "lines", G_TYPE_INT, (gint) (filter->nFrameLength >> 1) + 1,
			  "nyquist", G_TYPE_INT, (gint) filter->nSampleRate/2,
			  NULL);

  g_value_init(&v, GST_TYPE_ARRAY);
  gst_structure_set_value(s, "magnitude", &v);

  g_value_unset(&v);
  g_value_init(&v, G_TYPE_DOUBLE);

  a = (GValue *) gst_structure_get_value(s, "magnitude");
 
  for (i = 0; i < (filter->nFrameLength >> 1) + 1; i++) {
    g_value_set_double(&v, filter->vecCurrentSpecEst[i]);
    gst_value_array_append_value(a, &v);
  }
  g_value_unset(&v);

  e = gst_event_new_custom(GST_EVENT_CUSTOM_DOWNSTREAM, s);
  
  gst_pad_push_event(filter->activesrcpad, e);

}


static gboolean
gst_sad_frame_based_classify(GstSAD *filter, GstBuffer *buf)
{
  gint i;
  gdouble rNRG = 0.0;
  gint nZCC = 0;
  gdouble rZCR = 0.0;
  gboolean bDecision = FALSE;

  gdouble *frame = filter->vecFrame;  //local reference for convenience.

  gint16 *pnData = (gint16 *) GST_BUFFER_DATA(buf);

//DEBUG
//g_print(__FUNCTION__);
//fflush(stdout);

  for (i = 0; i < filter->nFrameLength; i++) {
    frame[i] = ((gdouble) pnData[i])/G_MAXINT16;
  }  

  // Calculate decision features

  // Energy
  for (i = 0; i < filter->nFrameLength; i++) {
    rNRG += frame[i] * frame[i] * (filter->nSamplePeriod);
  }

  // ZCR
  for (i = 1; i < filter->nFrameLength; i++) {
    if (GSL_SIGN(frame[i]) != GSL_SIGN(frame[i-1])) {
      nZCC++;
    }
  }
  rZCR = nZCC / ((gdouble) filter->framelength * 1e-6);
 
  // Classifier
  bDecision = ( ((gdouble) rNRG) > filter->threshold );

  if (filter->output_features) {

    // finale! commented out the pring statement!
    
    //g_print("printing <%"G_GUINT64_FORMAT">\t%lf, %lf\t%d\n", buf->timestamp , 10*log10(rNRG/filter->framelength) + 3.01, rZCR, (gint) bDecision);
   
    // finale! added send a message here!
    gst_element_post_message(GST_ELEMENT_CAST(filter),
            gst_message_new_application(GST_OBJECT_CAST(filter),
              gst_structure_new("start_of_segment",
				"output_feature" , G_TYPE_DOUBLE, (gdouble) rNRG  , NULL)));
  
  }



  return bDecision;
}
