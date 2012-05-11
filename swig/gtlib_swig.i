/* -*- c++ -*- */

#define GTLIB_API

%include "gnuradio.i"			// the common stuff

//load generated python docstrings
%include "gtlib_swig_doc.i"


%{
#include "gtlib_bfsk_modulator_fc.h"
#include "gtlib_ncbfsk_freq_diversity.h"
#include "gtlib_framer_sink_2.h"
%}


GR_SWIG_BLOCK_MAGIC(gtlib,bfsk_modulator_fc);
%include "gtlib_bfsk_modulator_fc.h"
GR_SWIG_BLOCK_MAGIC(gtlib,ncbfsk_freq_diversity);
%include "gtlib_ncbfsk_freq_diversity.h"

GR_SWIG_BLOCK_MAGIC(gtlib,framer_sink_2);
%include "gtlib_framer_sink_2.h"
