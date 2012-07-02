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
gtlib_make_ofdm_stbc_encoder (unsigned int fft_length,const std::vector < std::vector <int> > &code_matrix, float code_rate)
{
	return gtlib_ofdm_stbc_encoder_sptr (new gtlib_ofdm_stbc_encoder (fft_length,code_matrix,code_rate));
}


gtlib_ofdm_stbc_encoder::gtlib_ofdm_stbc_encoder (unsigned int fft_length, const std::vector < std::vector <int> > &code_matrix, float code_rate)
	: gr_block ("ofdm_stbc_encoder",
		gr_make_io_signature2 (1, 2, sizeof(gr_complex)*fft_length, sizeof(char)),
		gr_make_io_signature (1, -1, sizeof(gr_complex)*fft_length)),
		d_fft_length(fft_length),
		d_code_matrix(code_matrix),
		d_encoding_idx(0)

{
    d_nsymbols = d_code_matrix[0].size()/2;
    d_ntimeslots = (unsigned int)(float(d_nsymbols) / code_rate);
    d_nantennas = d_code_matrix.size() / d_ntimeslots;
    
    // Initialize a symbol buffer    
    d_stored_symbol.resize(d_nsymbols);

    for (int ii=0;ii<d_nsymbols;ii++)
        d_stored_symbol[ii].resize(d_fft_length);

    printf ("[OFDM STBC Encoder] # of Required Symbols = %d\n",d_nsymbols);
    printf ("[OFDM STBC Encoder] # of Time Slots = %d\n",d_ntimeslots);
    printf ("[OFDM STBC Encoder] # of Antennas = %d\n",d_nantennas);
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
    gr_complex *out;
    const char *in_flag = 0;    

    // printf("[OFDM STBC Encoder] noutput_items=%d\r\n",noutput_items);

    int ii,jj,kk,ll;
    int selected_symbol;
    bool conjugated;
    float negative;
    
    // Process a single symbol at a time
    
    /*
    if (noutput_items < d_ntimeslots)
        return 0;
    */
    
    if(input_items.size() == 2)
    {
        in_flag = (char *)input_items[1];
        if (in_flag[0])
            d_encoding_idx = 0;
    }
    
    //printf ( "[OFDM STBC Encoder] Size of the stored symbol=%d\n", d_stored_symbol[d_encoding_idx].size());
    
    std::copy ( in, in+d_fft_length, d_stored_symbol[d_encoding_idx].begin());

    consume_each (1);
    
    if (d_encoding_idx < (d_nsymbols-1))
    {
        d_encoding_idx++;

        return 0;
    }
    else
    {
        d_encoding_idx=0;

        for (ii = 0; ii < d_ntimeslots; ii++)
        {
            for (jj = 0;jj < d_nantennas; jj++)
            {
                if (jj < output_items.size())
                {
                    // Choose the antenna to transmit
                    out = (gr_complex *) output_items[jj];
                

                    for (kk = 0; kk < 2*d_nsymbols; kk++)
                    {
                        // Find the non-zero element in the code matrix
                        if ( d_code_matrix[ii*(d_nantennas) + jj][kk] != 0)
                        {
                            selected_symbol = kk % d_nsymbols;
                            conjugated = ( kk >= d_nsymbols );
                            negative = ( d_code_matrix[ii*(d_nantennas) + jj][kk] > 0) ? 1.0 : -1.0;
                            
                            //printf ("[OFDM STBC Encoder] ii=%d,jj=%d,kk=%d,selected_symbol=%d,conjugated=%d,negative=%f\n",
                            //        ii,jj,kk,selected_symbol,(int)conjugated,negative);
                            
                            if (!conjugated)
                            {
                                for (ll = 0; ll < d_fft_length; ll++)
                                {
                                    out[ii*d_fft_length + ll] = negative*d_stored_symbol[selected_symbol][ll];    
                                }
                            }
                            else
                            {
                                for (ll = 0; ll < d_fft_length; ll++)
                                {
                                    out[ii*d_fft_length + ll] = negative*conj(d_stored_symbol[selected_symbol][ll]);    
                                }
                            }
                            
                        }
                    }    
                }                    
            }
        }

        return d_ntimeslots;        
    }
    
}

