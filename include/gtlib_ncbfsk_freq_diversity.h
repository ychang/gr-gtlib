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

#ifndef INCLUDED_gtlib_ncbfsk_freq_diversity_H
#define	INCLUDED_gtlib_ncbfsk_freq_diversity_H

#include <gtlib_api.h>
#include <gr_block.h>
#include <gr_math.h>
#include <stdio.h>

#define MAX_SPS             64
#define MAX_DIVERSITY_ORDER 4
#define MAX_SEQUENCE_LENGTH     64
#define MAX_SEQUENCE_PADDING    2

class gri_mmse_fir_interpolator;

class gtlib_ncbfsk_freq_diversity;
typedef boost::shared_ptr<gtlib_ncbfsk_freq_diversity> gtlib_ncbfsk_freq_diversity_sptr;


// public constructor
GTLIB_API gtlib_ncbfsk_freq_diversity_sptr 
gtlib_make_ncbfsk_freq_diversity (int sps,float gamma,const std::string &msequence_code, int threshold);

class GTLIB_API gtlib_ncbfsk_freq_diversity : public gr_block
{
 public:
  ~gtlib_ncbfsk_freq_diversity ();
  void forecast(int noutput_items, gr_vector_int &ninput_items_required);
  int general_work (int noutput_items,
		    gr_vector_int &ninput_items,
		    gr_vector_const_void_star &input_items,
		    gr_vector_void_star &output_items);

    bool            set_msequence_code (const std::string &msequence_code);
    float           parabolic_peak_interpolation(float d1,float d2,float d3);
    void            SPADE_func(unsigned int *spade_int,float *spade_frac);
    void            unlock(void);


    float           mean_estimator(float *data);
    float           peak_estimator(float *data);
    void            config_timestamp(long timestamp_gap);
    timespec diff(timespec start, timespec end);
    timespec initial_time;

protected:
  gtlib_ncbfsk_freq_diversity (int sps,float gamma,const std::string &msequence_code, int threshold);

    private:
    int             d_sps;
    float           d_gamma;

    unsigned long long  d_coarse_reg[MAX_SPS];	// used to look for msequence_code

    unsigned long long  d_msequence_code;	// msequence code to locate start of packet
    unsigned int        d_mseq_length;
    bool                d_mseq[MAX_SEQUENCE_LENGTH];
    unsigned int	    d_threshold;	// how many bits may be wrong in sync vector
    unsigned int        d_pkt_len;

    int                 d_spade_index[MAX_SEQUENCE_LENGTH];
    int                 d_spade_length;

    unsigned long long  d_data_reg;	// used to look for msequence_code
    unsigned long long  d_flag_reg;	// keep track of decisions
    unsigned long long  d_flag_bit;	// mask containing 1 bit which is location of new flag
    unsigned long long  d_mask;		// masks msequence_code bits (top N bits are set where

    unsigned long long  d_timestamp;

    float               d_seq_stack[MAX_SEQUENCE_LENGTH+2][MAX_SPS];
    unsigned int        d_seq_stack_idx;
    unsigned int        d_seq_window[MAX_SPS*2];
    float               d_seq_SPADE_func[MAX_SPS*2];

    unsigned int        d_locked;
    unsigned int        d_status;
    float               d_max_value;
    float               d_max_noise;
    float               d_unlock_value;
    unsigned int        d_max_idx;

    float               d_fractional_control_factor;

    unsigned long       d_prev_ts;

    unsigned long       d_timestamp_gap;

    FILE *fp;

    friend GTLIB_API gtlib_ncbfsk_freq_diversity_sptr
    gtlib_make_ncbfsk_freq_diversity (int sps,float gamma,const std::string &msequence_code, int threshold);
};

#endif
