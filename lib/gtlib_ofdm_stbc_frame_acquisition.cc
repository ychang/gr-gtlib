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

#include <gtlib_ofdm_stbc_frame_acquisition.h>
#include <gr_io_signature.h>
#include <gr_expj.h>
#include <gr_math.h>
#include <cstdio>

#define VERBOSE 1
#define M_TWOPI (2*M_PI)
#define MAX_NUM_SYMBOLS 1000

gtlib_ofdm_stbc_frame_acquisition_sptr
gtlib_make_ofdm_stbc_frame_acquisition (unsigned int occupied_carriers,
				     unsigned int fft_length, 
				     unsigned int cplen,
				     const std::vector<gr_complex> &known_symbol,
				     unsigned int max_fft_shift_len,
				     unsigned int code_type,
				     const std::vector< std::vector<gr_complex> > &training_symbol)
{
  return gnuradio::get_initial_sptr(new gtlib_ofdm_stbc_frame_acquisition (occupied_carriers, fft_length, cplen,
									known_symbol, max_fft_shift_len, code_type,training_symbol));
}

gtlib_ofdm_stbc_frame_acquisition::gtlib_ofdm_stbc_frame_acquisition (unsigned occupied_carriers,
								unsigned int fft_length, 
								unsigned int cplen,
								const std::vector<gr_complex> &known_symbol,
								unsigned int max_fft_shift_len,
								unsigned int code_type,
								const std::vector< std::vector<gr_complex> > &training_symbol)
								
  : gr_block ("ofdm_stbc_frame_acquisition",
	      gr_make_io_signature2 (2, 2, sizeof(gr_complex)*fft_length, sizeof(char)*fft_length),
	      gr_make_io_signature2 (2, 2, sizeof(gr_complex)*occupied_carriers, sizeof(char))),
    d_occupied_carriers(occupied_carriers),
    d_fft_length(fft_length),
    d_cplen(cplen),
    d_freq_shift_len(max_fft_shift_len),
    d_known_symbol(known_symbol),
    d_code_type(code_type),
    d_coarse_freq(0),
    d_phase_count(0),
    d_training_symbol(training_symbol)
{
    unsigned int i = 0, j = 0;

    d_symbol_phase_diff.resize(d_fft_length);
    d_known_phase_diff.resize(d_occupied_carriers);
    
    // Initialize channel buffer
    d_hestimate.resize(4);
    for (i = 0; i < 4; i++)
        d_hestimate[i].resize(d_occupied_carriers);
    

    // Clear Known phase??? 

    std::fill(d_known_phase_diff.begin(), d_known_phase_diff.end(), 0);
    
    for(i = 0; i < d_known_symbol.size()-2; i+=2) {
        d_known_phase_diff[i] = norm(d_known_symbol[i] - d_known_symbol[i+2]);
    }
    
    // Phas e Lookup Table
  
    d_phase_lut = new gr_complex[(2*d_freq_shift_len+1) * MAX_NUM_SYMBOLS];
    
    for(i = 0; i <= 2*d_freq_shift_len; i++) 
    {
    
        for(j = 0; j < MAX_NUM_SYMBOLS; j++)
        {
            d_phase_lut[j + i*MAX_NUM_SYMBOLS] =  gr_expj(-M_TWOPI*d_cplen/d_fft_length*(i-d_freq_shift_len)*j);
        }
    
    }
    
    d_block_size = 2;
    
    stored_symbol[0].resize(occupied_carriers);
    stored_symbol[1].resize(occupied_carriers);
    stored_symbol[2].resize(occupied_carriers);
    stored_symbol[3].resize(occupied_carriers);
    
    printf ( "[OFDM Frame Acquisition] : Lenght of Preamble=%d\n", d_known_symbol.size() );
    printf ( "[OFDM Frame Acquisition] : Lenght of STBC block=%d\n", d_training_symbol.size() );
    
    for (i=0 ; i < d_training_symbol.size(); i++)
    {
        printf ( "                           [%d] : Length = %d\n", i+1, d_training_symbol[i].size() );
    }
    
}

gtlib_ofdm_stbc_frame_acquisition::~gtlib_ofdm_stbc_frame_acquisition(void)
{
    delete [] d_phase_lut;
}

void
gtlib_ofdm_stbc_frame_acquisition::forecast (int noutput_items, gr_vector_int &ninput_items_required)
{
    unsigned ninputs = ninput_items_required.size ();
    for (unsigned i = 0; i < ninputs; i++)
        ninput_items_required[i] = 1;
}

gr_complex
gtlib_ofdm_stbc_frame_acquisition::coarse_freq_comp(int freq_delta, int symbol_count)
{
    //  return gr_complex(cos(-M_TWOPI*freq_delta*d_cplen/d_fft_length*symbol_count),
    //	    sin(-M_TWOPI*freq_delta*d_cplen/d_fft_length*symbol_count));

    return gr_expj(-M_TWOPI*freq_delta*d_cplen/d_fft_length*symbol_count);

    //return d_phase_lut[MAX_NUM_SYMBOLS * (d_freq_shift_len + freq_delta) + symbol_count];
}

void
gtlib_ofdm_stbc_frame_acquisition::correlate(const gr_complex *symbol, int zeros_on_left)
{
    unsigned int i,j;
    
    std::fill(d_symbol_phase_diff.begin(), d_symbol_phase_diff.end(), 0);
    
    for(i = 0; i < d_fft_length-2; i++) {
        d_symbol_phase_diff[i] = norm(symbol[i] - symbol[i+2]);
    }

    // sweep through all possible/allowed frequency offsets and select the best
    int index = 0;
    float max = 0, sum=0;

    for(i =  zeros_on_left - d_freq_shift_len; i < zeros_on_left + d_freq_shift_len; i++) {

        sum = 0;
    
        for(j = 0; j < d_occupied_carriers; j++) {
            sum += (d_known_phase_diff[j] * d_symbol_phase_diff[i+j]);
        }

        if(sum > max) {
            max = sum;
            index = i;
        }

    }
  
    // set the coarse frequency offset relative to the edge of the occupied tones
    d_coarse_freq = index - zeros_on_left;
}

/*
void
gtlib_ofdm_stbc_frame_acquisition::calculate_equalizer(const gr_complex *symbol, int zeros_on_left)
{
    unsigned int i=0;

    // Set first tap of equalizer
    d_hestimate[0] = d_known_symbol[0] / 
        (coarse_freq_comp(d_coarse_freq,1)*symbol[zeros_on_left+d_coarse_freq]);

    // set every even tap based on known symbol
    // linearly interpolate between set carriers to set zero-filled carriers
    // FIXME: is this the best way to set this?
    for(i = 2; i < d_occupied_carriers; i+=2) {
        d_hestimate[i] = d_known_symbol[i] / 
            (coarse_freq_comp(d_coarse_freq,1)*(symbol[i+zeros_on_left+d_coarse_freq]));
        d_hestimate[i-1] = (d_hestimate[i] + d_hestimate[i-2]) / gr_complex(2.0, 0.0);    
    }

    // with even number of carriers; last equalizer tap is wrong
    if(!(d_occupied_carriers & 1)) {
        d_hestimate[d_occupied_carriers-1] = d_hestimate[d_occupied_carriers-2];
    }

    if(VERBOSE) {
        
        fprintf(stderr, "Equalizer setting:\n");
        
        for(i = 0; i < d_occupied_carriers; i++) {
            gr_complex sym = coarse_freq_comp(d_coarse_freq,1)*symbol[i+zeros_on_left+d_coarse_freq];
            gr_complex output = sym * d_hestimate[i];
            fprintf(stderr, "sym: %+.4f + j%+.4f  ks: %+.4f + j%+.4f  eq: %+.4f + j%+.4f  ==>  %+.4f + j%+.4f\n", 
                sym .real(), sym.imag(),
            d_known_symbol[i].real(), d_known_symbol[i].imag(),
            d_hestimate[i].real(), d_hestimate[i].imag(),
            output.real(), output.imag());
        }

        fprintf(stderr, "\n");

    }
}
*/
/*
void
gtlib_ofdm_stbc_frame_acquisition::calculate_equalizer(const gr_complex *symbol, int zeros_on_left, int channel)
{
    unsigned int i=0;

    // Set first tap of equalizer
    d_hestimate[channel][0] = d_training_symbol[channel][0] / 
        (coarse_freq_comp(d_coarse_freq,1)*symbol[zeros_on_left+d_coarse_freq]);

    // set every even tap based on known symbol
    // linearly interpolate between set carriers to set zero-filled carriers
    // FIXME: is this the best way to set this?
    for(i = 2; i < d_occupied_carriers; i+=2) {
        d_hestimate[channel][i] = d_training_symbol[channel][i] / 
            (coarse_freq_comp(d_coarse_freq,1)*(symbol[i+zeros_on_left+d_coarse_freq]));
        d_hestimate[channel][i-1] = (d_hestimate[channel][i] + d_hestimate[channel][i-2]) / gr_complex(2.0, 0.0);    
    }

    // with even number of carriers; last equalizer tap is wrong
    if(!(d_occupied_carriers & 1)) {
        d_hestimate[channel][d_occupied_carriers-1] = d_hestimate[channel][d_occupied_carriers-2];
    }

    if(VERBOSE) {
        
        fprintf(stderr, "Equalizer setting:\n");
        
        for(i = 0; i < d_occupied_carriers; i++) {
            gr_complex sym = coarse_freq_comp(d_coarse_freq,1)*symbol[i+zeros_on_left+d_coarse_freq];
            gr_complex output = sym * d_hestimate[channel][i];
            fprintf(stderr, "sym: %+.4f + j%+.4f  ks: %+.4f + j%+.4f  eq: %+.4f + j%+.4f  ==>  %+.4f + j%+.4f\n", 
                sym .real(), sym.imag(),
            d_training_symbol[channel][i].real(), d_training_symbol[channel][i].imag(),
            d_hestimate[channel][i].real(), d_hestimate[channel][i].imag(),
            output.real(), output.imag());
        }

        fprintf(stderr, "\n");

    }
}
*/
void
gtlib_ofdm_stbc_frame_acquisition::calculate_equalizer(const gr_complex *symbol, int zeros_on_left, int channel)
{
    unsigned int i=0;

    // Set first tap of equalizer
    d_hestimate[channel][0] = (coarse_freq_comp(d_coarse_freq,1)*symbol[zeros_on_left+d_coarse_freq]) 
                            / d_training_symbol[channel][0];
        ;

    // set every even tap based on known symbol
    // linearly interpolate between set carriers to set zero-filled carriers
    // FIXME: is this the best way to set this?
    for(i = 2; i < d_occupied_carriers; i+=2) {
        d_hestimate[channel][i] = (coarse_freq_comp(d_coarse_freq,1)*(symbol[i+zeros_on_left+d_coarse_freq])) 
                            / d_training_symbol[channel][i];
            ;
        d_hestimate[channel][i-1] = (d_hestimate[channel][i] + d_hestimate[channel][i-2]) / gr_complex(2.0, 0.0);    
    }

    // with even number of carriers; last equalizer tap is wrong
    if(!(d_occupied_carriers & 1)) {
        d_hestimate[channel][d_occupied_carriers-1] = d_hestimate[channel][d_occupied_carriers-2];
    }

    if(VERBOSE) {
        
        fprintf(stderr, "Equalizer setting:\n");
        
        for(i = 0; i < d_occupied_carriers; i++) {
            gr_complex sym = coarse_freq_comp(d_coarse_freq,1)*symbol[i+zeros_on_left+d_coarse_freq];
            gr_complex output = sym * d_hestimate[channel][i];
            fprintf(stderr, "sym: %+.4f + j%+.4f  ks: %+.4f + j%+.4f  eq: %+.4f + j%+.4f  ==>  %+.4f + j%+.4f\n", 
                sym .real(), sym.imag(),
            d_training_symbol[channel][i].real(), d_training_symbol[channel][i].imag(),
            d_hestimate[channel][i].real(), d_hestimate[channel][i].imag(),
            output.real(), output.imag());
        }

        fprintf(stderr, "\n");

    }
}

int
gtlib_ofdm_stbc_frame_acquisition::general_work(int noutput_items,
					     gr_vector_int &ninput_items,
					     gr_vector_const_void_star &input_items,
					     gr_vector_void_star &output_items)
{
    const gr_complex *symbol = (const gr_complex *)input_items[0];
    const char *signal_in = (const char *)input_items[1];
    
    gr_complex *out = (gr_complex *) output_items[0];
    char *signal_out = (char *) output_items[1];
    
    int unoccupied_carriers = d_fft_length - d_occupied_carriers;
    int zeros_on_left = (int)ceil(unoccupied_carriers/2.0);
    int ii;


    //printf("OFDM Frame Acquisition: noutput_items=%d\n",noutput_items);
    
    // Check the existence of Preamble Symbol ( Single symbol )
    if(signal_in[0]) {
            
        printf("[OFDM Frame Acquisition] : Signal In\n");
        d_phase_count = 1;

        // Find the coarse frequency offset by correlating with the known sequence
        // d_coarse_freq

        correlate(symbol, zeros_on_left);

        // Decorrelation of the preamble and calculate the 
        //calculate_equalizer(symbol, zeros_on_left,0 );
        signal_out[0] = 1;
        d_symbol_idx = 0;
 
        d_symbol_idx++;
        d_phase_count++;

        consume_each(1);
        return 1;
    }
    else
    {
        signal_out[0] = 0;
        
        if ( (d_symbol_idx-1) < d_block_size)
        {
            //printf("[OFDM Frame Acquisition] : Training Sequence %d\n",d_symbol_idx-1);
            
            calculate_equalizer(symbol, zeros_on_left, d_symbol_idx-1);
            
            d_symbol_idx++;
            d_phase_count++;

            if(d_phase_count == MAX_NUM_SYMBOLS) {
                d_phase_count = 1;
            }
            
        }
        else
        {
            if (d_symbol_idx < MAX_SYMBOL)
            {
                for(unsigned int i = 0; i < d_occupied_carriers; i++) 
                {
                    stored_symbol[ (d_symbol_idx-d_block_size-1)%d_block_size ][i] = coarse_freq_comp(d_coarse_freq,d_phase_count)
                        *symbol[i+zeros_on_left+d_coarse_freq];
                }
                consume_each(1);
                
                d_symbol_idx++;
                d_phase_count++;

                if(d_phase_count == MAX_NUM_SYMBOLS) {
                    d_phase_count = 1;
                }
                
                if ( ((d_symbol_idx-d_block_size-1)%d_block_size) == 0 )
                {
                    switch(d_code_type)
                    {
                        case 0: 

                            //printf("OFDM Frame Acquisition: Odd Frame\n");
                            for(unsigned int i = 0; i < d_occupied_carriers; i++) 
                            {
                                out[i] = conj(d_hestimate[0][i])*stored_symbol[0][i] + d_hestimate[1][i]*conj(stored_symbol[1][i]);
                            }
        
                            //printf("OFDM Frame Acquisition: Even Frame\n");
                            for(unsigned int i = 0; i < d_occupied_carriers; i++) 
                            {
                                out[d_occupied_carriers + i] = conj(d_hestimate[1][i])*stored_symbol[0][i] - d_hestimate[0][i]*conj(stored_symbol[1][i]);
                            }
                            
                            break;

                        default:
                            break;
                    }
                    
                    return d_block_size;                
                }
                else
                {
                    return 0;
                }
            }
        }
        consume_each(1);
    }
    
    
}
