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

#include <gr_io_signature.h>
#include <gtlib_ofdm_stbc_decoder.h>


gtlib_ofdm_stbc_decoder_sptr
gtlib_make_ofdm_stbc_decoder (unsigned int fft_length)
{
	return gtlib_ofdm_stbc_decoder_sptr (new gtlib_ofdm_stbc_decoder (fft_length));
}


gtlib_ofdm_stbc_decoder::gtlib_ofdm_stbc_decoder (unsigned int fft_length)
	: gr_block ("ofdm_stbc_decoder",
		gr_make_io_signature2 (1, 2, sizeof(gr_complex)*fft_length, sizeof(char)),
		gr_make_io_signature (1, 1, sizeof(gr_complex)*fft_length)),
		d_fft_length(fft_length)
{
}


gtlib_ofdm_stbc_decoder::~gtlib_ofdm_stbc_decoder ()
{
}


int
gtlib_ofdm_stbc_decoder::general_work (int noutput_items,
			       gr_vector_int &ninput_items,
			       gr_vector_const_void_star &input_items,
			       gr_vector_void_star &output_items)
{
  const float *in = (const float *) input_items[0];
  float *out = (float *) output_items[0];

  // Tell runtime system how many input items we consumed on
  // each input stream.
  consume_each (noutput_items);

  // Tell runtime system how many output items we produced.
  return noutput_items;
}

