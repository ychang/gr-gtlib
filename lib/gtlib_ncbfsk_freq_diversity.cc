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

#include <stdio.h>
#include <string.h>
#include <gr_io_signature.h>
#include <gtlib_ncbfsk_freq_diversity.h>
#include <gri_mmse_fir_interpolator.h>
#include <gr_count_bits.h>
#include <stdexcept>

//#define d_spade_length 10
#define min_value(a,b) ((a) < (b)) ? a : b

//const int d_spade_index[]={10,14,17,18,21,30,38,39,40,50};

// Public constructor

gtlib_ncbfsk_freq_diversity_sptr 
gtlib_make_ncbfsk_freq_diversity(int sps,float gamma,const std::string &msequence_code, int threshold)
{
  return gtlib_ncbfsk_freq_diversity_sptr (new gtlib_ncbfsk_freq_diversity (sps,gamma,msequence_code, threshold));
}

gtlib_ncbfsk_freq_diversity::gtlib_ncbfsk_freq_diversity (int sps,float gamma,const std::string &msequence_code, int threshold)
  : gr_block ("ncbfsk_freq_diversity",
	      gr_make_io_signature (1, 1, sizeof (float)),
	      gr_make_io_signature (1, 1, sizeof (unsigned long))),
    d_sps (sps),d_gamma(gamma),
    d_data_reg(0), d_flag_reg(0), d_flag_bit(0), d_mask(0), d_timestamp(0), d_threshold(threshold)
{
    d_sps = (int)sps;
    d_gamma = (float)gamma;
    d_locked = 0;
    d_status = 0;
    d_max_value = 0;
    d_unlock_value = 0;
    d_fractional_control_factor = 0;
    d_seq_stack_idx=0;
    d_spade_length = 0;
    d_timestamp_gap = 1;
    
    // Make sure that noutput_items are multiple of 16 even though realtime scheduling is selected (Yong)
    set_output_multiple(16);

    if (!set_msequence_code(msequence_code)){
        //fprintf(stderr, "gr_correlate_msequence_code_bb: msequence_code is > 64 bits\n");
        throw std::out_of_range ("msequence_code is > 64 bits");
    }

}

gtlib_ncbfsk_freq_diversity::~gtlib_ncbfsk_freq_diversity ()
{
}

void
gtlib_ncbfsk_freq_diversity::forecast(int noutput_items, gr_vector_int &ninput_items_required)
{
  unsigned ninputs = ninput_items_required.size();
  for (unsigned i=0; i < ninputs; i++)
    ninput_items_required[i] =
      (int) ceil((noutput_items * d_sps));
}

inline int
slice(float x)
{
  return x < 0 ? 0 : 1;
}

inline int
sign(float x)
{
  return x < 0 ? -1 : x ==  0 ? 0 : 1;
}

inline unsigned int
find_peak(float *data,int len)
{
    float max_value=0;
    unsigned int max_index=0;
    
    for(int i=0;i<len;i++)
    {
        if(*(data+i) > max_value)
        {
            max_value = *(data+i);
            max_index = i;
        }    
    }
    return max_index;
}

bool
gtlib_ncbfsk_freq_diversity::set_msequence_code(
  const std::string &msequence_code)
{
    unsigned len = msequence_code.length();	// # of bytes in string
  
    d_mseq_length = len;

    if (len > 64) return false;

    // set len top bits to 1.
    d_mask = ((~0ULL) >> (64 - len)) << (64 - len);

    d_flag_bit = 1LL << (64 - len);	// Where we or-in new flag values.
                                        // new data always goes in 0x0000000000000001
    d_msequence_code = 0;
    for (unsigned i=0; i < 64; i++){
        d_msequence_code <<= 1;
        if (i < len) d_msequence_code |= msequence_code[i] & 1;	// look at LSB only
        d_mseq[i] = msequence_code[i] & 1;
    }

    d_spade_length=0;
    
    for (int i=1;i<d_mseq_length-1;i++)
    {
        // Check isolated bit
        if ((d_mseq[i-1] != d_mseq[i]) && (d_mseq[i+1] != d_mseq[i]))
        {
            d_spade_index[d_spade_length++] = i;
        }
    }

    //fprintf(stdout,"SPADE bits : ");
    for (int i=0;i<d_spade_length;i++)
    {
        //fprintf(stdout,"%d ",d_spade_index[i]);
    }
    //fprintf(stdout,"\r\n");
    return true;
}

float  
gtlib_ncbfsk_freq_diversity::parabolic_peak_interpolation(float d1,float d2,float d3)
{
    // Parabolic Peak Interpolation
    float a,b,x_max;
    a = ((d3 - d2) - (d2 - d1)) / 2;
    b = ((d1 - d2) + (d2 - d3)) / 2;
    x_max=(0.5*b)/(a);
    return x_max;
}

float  
gtlib_ncbfsk_freq_diversity::peak_estimator(float *data)
{
    int     int_part,len;
    float   frac_part;
    
    len = 2 * d_sps;
    int_part = find_peak(data,len);    
    frac_part= parabolic_peak_interpolation(*(data+int_part-1),*(data+int_part),*(data+int_part+1));
    
    return (float)int_part + frac_part;
}
    
float  
gtlib_ncbfsk_freq_diversity::mean_estimator(float *data)
{
    float       *data_norm;
    float       sum=0;
    float       n_hat=0;
    
    data_norm = (float *)malloc(2*d_sps*sizeof(float));

    for (int i=0;i<2*d_sps;i++) sum += data[i];
    for (int i=0;i<2*d_sps;i++)
    {
        data_norm[i] = data[i]/sum;
        n_hat += (i*data_norm[i]);
    }
    
    return n_hat;
}
    
void
gtlib_ncbfsk_freq_diversity::SPADE_func(unsigned int *spade_int,float *spade_frac)
{
    float temp_waveform[64][MAX_SPS*2];
    unsigned int max_index=0;

    int         i,j;
    float       sop_peak_estimator;
    float       sop_mean_estimator;

    int        seq_window_margin=0;
    int        seq_window_length=0;
    int        seq_window_start=-1;
    int        seq_window_candidate_start;
    float      seq_temp_sum;
    float      seq_temp_sum_max;
    int        seq_temp_sum_max_index;
    

    memset(temp_waveform,0,sizeof(temp_waveform));
    memset(d_seq_SPADE_func,0,sizeof(d_seq_SPADE_func));

    // For testing

    for (i=0;i<2*d_sps;i++)
    {
        if (d_seq_window[i]==1)
        {
            if(seq_window_start==-1) seq_window_start=i;
            seq_window_length++;
        }
    }
    
    seq_window_margin = d_sps - 2 - seq_window_length;
    
    if (seq_window_margin < 0) seq_window_margin = 0;
    
    if (seq_window_start <= seq_window_margin)
    {
        seq_window_candidate_start = 0;
    }
    else
    {
        seq_window_candidate_start = seq_window_start - seq_window_margin;
    }

    // Checkout candidate points

    for(i=0;i<d_spade_length;i++)
    {
        for(j=0;j<d_sps;j++)
        {
            temp_waveform[i][j]=(d_seq_stack[(d_seq_stack_idx-1+d_spade_index[i]+MAX_SEQUENCE_PADDING)%(d_mseq_length+MAX_SEQUENCE_PADDING)][j]);
            temp_waveform[i][j+d_sps]=(d_seq_stack[(d_seq_stack_idx-1+1+d_spade_index[i]+MAX_SEQUENCE_PADDING)%(d_mseq_length+MAX_SEQUENCE_PADDING)][j]);
        }
    }    

    for(i=0;i<d_spade_length;i++)
    {
        for(j=0;j<2*d_sps;j++)
        {
            if (d_mseq[d_spade_index[i]]) d_seq_SPADE_func[j]+=temp_waveform[i][j];     
            else d_seq_SPADE_func[j]-=temp_waveform[i][j];    
    }
    }

    seq_temp_sum_max_index = seq_window_candidate_start;
    seq_temp_sum_max = 0;
    
    for (i=0;i<seq_window_margin;i++)
    {
        seq_temp_sum=0;
        for (j=0;j<d_sps-2;j++)
        {
            seq_temp_sum += d_seq_SPADE_func[seq_window_candidate_start+i+j];
        }    
        if (seq_temp_sum_max < seq_temp_sum)
        {
            seq_temp_sum_max = seq_temp_sum;
            seq_temp_sum_max_index = seq_window_candidate_start+i;
        }
    }

    for(i=0;i<d_sps*2;i++)
    {
        if ( i < seq_temp_sum_max_index || i >= seq_temp_sum_max_index+d_sps-2 )
        {
            d_seq_SPADE_func[i] = 0;
        }
    }
    
    sop_peak_estimator = peak_estimator(d_seq_SPADE_func);
    sop_mean_estimator = mean_estimator(d_seq_SPADE_func);

    if (sop_mean_estimator < 0) 
    {
        sop_mean_estimator = sop_peak_estimator;
    }
    
    if(d_gamma >= 0)
    {
        if (fabs(sop_peak_estimator-sop_mean_estimator)>d_gamma)
        {
            //fprintf(stdout,"MEAN : [%f],[%f]\r\n",sop_peak_estimator,sop_mean_estimator);
    
            
            // Mean Estimator
            *spade_int = (int)sop_mean_estimator;
            *spade_frac = sop_mean_estimator - (float)*spade_int;

        }
        else
        {
            //fprintf(stdout,"PEAK : [%f],[%f]\r\n",sop_peak_estimator,sop_mean_estimator);

            // Peak Estimator
            *spade_int = (int)sop_peak_estimator;
            *spade_frac = sop_peak_estimator - (float)*spade_int;

        }
    }
    else
    {
        //fprintf(stdout,"PEAK : [%f],[%f]\r\n",sop_peak_estimator,sop_mean_estimator);

        // Peak Estimator
        *spade_int = (int)sop_peak_estimator;
        *spade_frac = sop_peak_estimator - (float)*spade_int;
    }
}

void
gtlib_ncbfsk_freq_diversity::unlock(void)
{
    d_locked=0;
    memset(d_coarse_reg,0,sizeof(d_coarse_reg));
    memset(d_seq_stack,0,sizeof(d_seq_stack));
}

void 
gtlib_ncbfsk_freq_diversity::config_timestamp(long timestamp_gap)
{
    d_timestamp_gap = timestamp_gap;
}

static const int FUDGE = 64;

// Core routine for NON-COHERENT BFSK DEMODULATION (Yong)
// 1) Envelope Detector
// 2) Symbol Timing Synchronizer

int
gtlib_ncbfsk_freq_diversity::general_work (int noutput_items,
				       gr_vector_int &ninput_items,
				       gr_vector_const_void_star &input_items,
				       gr_vector_void_star &output_items)
{
    //unsigned long long  *in_ts = (unsigned long long*) input_items[0];
    //unsigned long long  *out_ts = (unsigned long long*) output_items[0];

    float           *in = (float *) input_items[0];   
    unsigned long   *out = (unsigned long *) output_items[0];
    

    //float *in_1 = (float *) input_items[1];
    //unsigned long *out_b = (unsigned long *) output_items[2];

    int 	ii = 0;				// input index
    int  	oo = 0;				// output index
    int     ni = ninput_items[0] - FUDGE;  // don't use more input than this

    int     temp = 0;
    
    // For M-Sequence Detection
    // compute hamming distance between desired msequence code and current data
    unsigned long long      wrong_bits = 0;
    unsigned int            nwrong = d_threshold+1;
 
    // SPADE function
    unsigned int    spade_int;
    float           spade_frac;
    
    float           symbol[MAX_SPS];
    long long       ts_temp;

    // Initialize sym_duration with two factors
    // d_window_size : Calculator margin coming from consume_each (ii-d_window_size)
 
    while (oo < noutput_items && ii < ni)
    {

        // Pick a single symbol from samples with diversity combining
        //for (temp=0;temp<d_sps;temp++) { symbol[temp] = in[ii+temp]; }
        memcpy(&symbol, &in[ii], sizeof(float)*d_sps);
        ii+=d_sps;
        
        if(!d_locked)
        {
            // Putting a symbol sequence into the preamble pipe for correlating
            // and check the preamble
            
            for (temp=0;temp<d_sps;temp++)        
            {
                d_coarse_reg[temp] = (d_coarse_reg[temp] << 1) | slice(symbol[temp]);
                d_seq_stack[d_seq_stack_idx][temp] = (symbol[temp]);
            
                wrong_bits  = (d_coarse_reg[temp] ^ d_msequence_code) & d_mask;
                nwrong = gr_count_bits64(wrong_bits);
                
                if(nwrong <= d_threshold)
                {
                    if(!d_status) d_status=1;
                    if(d_status<2) d_seq_window[temp]=1;
                    else d_seq_window[temp + (d_status-1)*d_sps]=1;
                }
                else
                {
                    if(d_status<2) d_seq_window[temp]=0;
                    else d_seq_window[temp + (d_status-1)*d_sps]=0;
                }

            }
            
            d_seq_stack_idx = (d_seq_stack_idx+1) % (d_mseq_length+MAX_SEQUENCE_PADDING);

            switch(d_status)
            {

                case 1 :    d_status = 2;
                            break;

                case 2 :    d_status = 0;
                            d_locked = 1;
                            
                            SPADE_func(&spade_int,&spade_frac);
                            if(fabs(spade_frac)>1) { spade_frac = 0; }

                            /*
                            ts_temp = (unsigned long long)in_ts[ii+spade_int-d_sps];
                            ts_temp += (unsigned long long)floor((spade_frac*(float)d_timestamp_gap)+0.5);
                            d_timestamp = (unsigned long long)ts_temp;
                            */
                            
                            ii+=(spade_int-(d_sps/2));


                            //d_prev_ts = in_ts[ii-1];
                            
                            break;
                default :   d_status = 0;
                            break;
            }
            out[oo] = (unsigned long)(d_locked<<1);
            //out_ts[oo] = (unsigned long long)d_timestamp;
            
        }
        else
        {
            d_unlock_value = 0;
            d_max_value = 0;

            d_max_idx = 0;

            // Peak maximum output
            for (temp=1;temp<d_sps-1;temp++)
            {
                d_unlock_value += fabs(symbol[temp]);
                if ( fabs(d_max_value) < fabs(symbol[temp]) )
                {
                    d_max_value = symbol[temp];
                    d_max_idx = temp;
                }
            }
              
            out[oo] = (((unsigned long)(fabs(d_max_value))<<2)&0xFFFFFFFC) | slice(d_max_value);
            
            float data_1,data_2,data_3;
            
            data_1 = symbol[d_max_idx-1];
            data_2 = symbol[d_max_idx];
            data_3 = symbol[d_max_idx+1];
            
            d_fractional_control_factor = parabolic_peak_interpolation(fabs(data_1),fabs(data_2),fabs(data_3));
            
            if(fabs(d_fractional_control_factor)>1) { d_fractional_control_factor = 0; }
            
            /*
            ts_temp = (unsigned long long)in_ts[ii-d_sps+d_max_idx];
            ts_temp += (unsigned long long)floor((d_fractional_control_factor*(float)d_timestamp_gap)+0.5);
            
            d_timestamp = (unsigned long long)ts_temp;
            out_ts[oo] = (unsigned long long)d_timestamp;   
            */

        }

	    oo++;
    }

    consume_each (ii);

    return oo;
}

