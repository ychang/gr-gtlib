/* -*- c++ -*- */
/*
 * Copyright 2004 Free Software Foundation, Inc.
 * 
 * This file is part of GNU Radio
 * 
 * GNU Radio is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3, or (at your option)
 * any later version.
 * 
 * GNU Radio is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with GNU Radio; see the file COPYING.  If not, write to
 * the Free Software Foundation, Inc., 51 Franklin Street,
 * Boston, MA 02110-1301, USA.
 */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#define VERBOSE 0

#include <stdio.h>
#include <gtlib_bfsk_modulator_fc.h>
#include <gr_io_signature.h>
#include <gr_sincos.h>
#include <math.h>


gtlib_bfsk_modulator_fc_sptr gtlib_make_bfsk_modulator_fc (double sensitivity_a,double sensitivity_b)
{
  return gtlib_bfsk_modulator_fc_sptr (new gtlib_bfsk_modulator_fc (sensitivity_a,sensitivity_b));
}

gtlib_bfsk_modulator_fc::gtlib_bfsk_modulator_fc (double sensitivity_a,double sensitivity_b)
  : gr_sync_block ("bfsk_modulator_fc",
		   gr_make_io_signature (1, 1, sizeof (float)),
		   gr_make_io_signature (1, 1, sizeof (gr_complex))),
    d_sensitivity_a (sensitivity_a), d_sensitivity_b (sensitivity_b), d_phase (0)
{
}
void
gtlib_bfsk_modulator_fc::set_sensitivity(double sensitivity_a,double sensitivity_b)
{
    d_phase = 0;
    d_sensitivity_a = sensitivity_a;
    d_sensitivity_b = sensitivity_b;
}
int
gtlib_bfsk_modulator_fc::work (int noutput_items,
				 gr_vector_const_void_star &input_items,
				 gr_vector_void_star &output_items)
{
  const float *in = (const float *) input_items[0];
  gr_complex *out = (gr_complex *) output_items[0];
  float amp_correct;

    if (VERBOSE)
        fprintf(stderr,">>> [BFSK Modulator] noutput_items=%ld\n",noutput_items);
       

  for (int i = 0; i < noutput_items; i++){
    if(in[i] >= 0)
        d_phase = d_phase + d_sensitivity_a * in[i];
    else
        d_phase = d_phase + d_sensitivity_b * in[i];

    float oi, oq;
    gr_sincosf (d_phase, &oq, &oi);
    out[i] = gr_complex (oi, oq);
  }

  // Limit the phase accumulator to [-16*pi,16*pi]
  // to avoid loss of precision in the addition above.

  if (fabs (d_phase) > 16 * M_PI){
    double ii = trunc (d_phase / (2 * M_PI));
    d_phase = d_phase - (ii * 2 * M_PI);
  }

  return noutput_items;
}
