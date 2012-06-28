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
#include <gtlib_ofdm_stbc_encoder.h>
#include <stdio.h>
#include <iostream>

gtlib_ofdm_stbc_encoder_sptr
gtlib_make_ofdm_stbc_encoder (unsigned int fft_length,unsigned int code_type)
{
	return gtlib_ofdm_stbc_encoder_sptr (new gtlib_ofdm_stbc_encoder (fft_length,code_type));
}


gtlib_ofdm_stbc_encoder::gtlib_ofdm_stbc_encoder (unsigned int fft_length, unsigned int code_type)
	: gr_block ("ofdm_stbc_encoder",
		gr_make_io_signature2 (1, 2, sizeof(gr_complex)*fft_length, sizeof(char)),
		gr_make_io_signature (1, 1, sizeof(gr_complex)*fft_length)),
		d_fft_length(fft_length),
		d_code_type(code_type),
		d_encoding_idx(0)

{

    switch(code_type)
    {
        case 0:
            d_block_size = 2;
            break;
        default:
            d_block_size = 1;
            break;
    }
}


gtlib_ofdm_stbc_encoder::~gtlib_ofdm_stbc_encoder ()
{
}
/*
void
gtlib_ofdm_stbc_encoder::forecast(int noutput_items, gr_vector_int &ninput_items_required)
{
  unsigned ninputs = ninput_items_required.size();
  for (unsigned i=0; i < ninputs; i++)
    ninput_items_required[i] =
      (int) ceil((noutput_items * 2));
}
*/

int
gtlib_ofdm_stbc_encoder::general_work (int noutput_items,
			       gr_vector_int &ninput_items,
			       gr_vector_const_void_star &input_items,
			       gr_vector_void_star &output_items)
{
    const gr_complex *in = (const gr_complex *) input_items[0];
    const char *in_flag = 0;    
    gr_complex *out = (gr_complex *) output_items[0];

    //printf("[OFDM STBC Encoder] noutput_items=%d\r\n",noutput_items);

    int ii=0,jj=0;
    
    
    if (noutput_items < d_block_size)
        return 0;
    
    
    if(input_items.size() == 2)
        in_flag = (char *) input_items[1];

    for (ii=0 ;ii < noutput_items - (noutput_items%d_block_size) ;ii+=d_block_size)
    {
        if (in_flag && in_flag[ii])
            d_encoding_idx = 0;
        
        switch(d_code_type)
        {
            case 0:
            
                for (jj = 0;jj < d_fft_length; jj++)
                {
                    out[ii*d_fft_length + jj] = in[ii*d_fft_length + jj];
                    out[(ii+1)*d_fft_length + jj] = in[(ii+1)*d_fft_length + jj];
                }

                break;
                
            default:
                for (jj = 0;jj < d_fft_length; jj++)
                {
                    out[ii*d_fft_length + jj] = in[ii*d_fft_length + jj];
                }
                break;            
         }
    }


    // Tell runtime system how many input items we consumed on
    // each input stream.
    consume_each (ii);

    // Tell runtime system how many output items we produced.
    return ii;
}

