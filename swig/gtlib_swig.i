/* -*- c++ -*- */

#define GTLIB_API

%include "gnuradio.i"			// the common stuff

//load generated python docstrings
%include "gtlib_swig_doc.i"


%{
#include "gtlib_bfsk_modulator_fc.h"
%}


GR_SWIG_BLOCK_MAGIC(gtlib,bfsk_modulator_fc);
%include "gtlib_bfsk_modulator_fc.h"
