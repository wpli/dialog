# plugindir is set in configure

##############################################################################
# change libgstplugin.la to something more suitable, e.g. libmysomething.la  #
##############################################################################
plugin_LTLIBRARIES = libSAD.la

##############################################################################
# for the next set of variables, rename the prefix if you renamed the .la,   #
#  e.g. libgstplugin_la_SOURCES => libmysomething_la_SOURCES                 #
#       libgstplugin_la_CFLAGS  => libmysomething_la_CFLAGS                  #
#       libgstplugin_la_LIBADD  => libmysomething_la_LIBADD                  #
#       libgstplugin_la_LDFLAGS => libmysomething_la_LDFLAGS                 #
##############################################################################

# sources used to compile this plug-in
libSAD_la_SOURCES = gstSAD.c

# flags used to compile this plugin
# add other _CFLAGS and _LIBS as needed
libSAD_la_CFLAGS = $(GST_CFLAGS) $(GSTCTRL_CFLAGS) $(GSL_CFLAGS)
libSAD_la_LIBADD = $(GST_LIBS) $(GSTCTRL_LIBS) $(GSL_LIBS)
libSAD_la_LDFLAGS = $(GST_PLUGIN_LDFLAGS) $(GSTCTRL_LDFLAGS) $(GSL_LDFLAGS)
libSAD_la_LIBTOOLFLAGS = --tag=disable-static

# headers we need but don't want installed
noinst_HEADERS = gstSAD.h

EXTRA_DIST = testSAD.sh test.wav
