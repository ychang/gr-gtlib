/* -*- c++ -*- */
/* 
 * Copyright 2012 <+YOU OR YOUR COMPANY+>.
 * 
 * This is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3, or (at your option)
 * any later version.
 * 
 * This software is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this software; see the file COPYING.  If not, write to
 * the Free Software Foundation, Inc., 51 Franklin Street,
 * Boston, MA 02110-1301, USA.
 */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gtlib_ofdm_cyclic_prefixer.h>
#include <gr_io_signature.h>
#include <stdio.h>
#include <iostream>

gtlib_ofdm_cyclic_prefixer_sptr
gtlib_make_ofdm_cyclic_prefixer (size_t input_size, size_t output_size)
{
  return gnuradio::get_initial_sptr(new gtlib_ofdm_cyclic_prefixer (input_size,
								      output_size));
}

gtlib_ofdm_cyclic_prefixer::gtlib_ofdm_cyclic_prefixer (size_t input_size,
							    size_t output_size)
  : gr_sync_interpolator ("ofdm_cyclic_prefixer",
			  gr_make_io_signature (1, 1, input_size*sizeof(gr_complex)),
			  gr_make_io_signature (1, 1, sizeof(gr_complex)),
			  output_size), 
    d_input_size(input_size),
    d_output_size(output_size)

{
}

int
gtlib_ofdm_cyclic_prefixer::work (int noutput_items,
				    gr_vector_const_void_star &input_items,
				    gr_vector_void_star &output_items)
{
  gr_complex *in = (gr_complex *) input_items[0];
  gr_complex *out = (gr_complex *) output_items[0];
  size_t cp_size = d_output_size - d_input_size;
  unsigned int i=0, j=0;

  
  
  j = cp_size;
  for(i=0; i < d_input_size; i++,j++) {
    out[j] = in[i];
  }

  j = d_input_size - cp_size;
  for(i=0; i < cp_size; i++, j++) {
    out[i] = in[j];
  }

  //printf("OFDM Cyclic Prefixer:  d_output_size: %d\n", d_output_size);
  return d_output_size;
}
