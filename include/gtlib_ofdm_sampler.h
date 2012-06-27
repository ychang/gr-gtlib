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

#ifndef INCLUDED_GTLIB_OFDM_SAMPLER_H
#define INCLUDED_GTLIB_OFDM_SAMPLER_H

#include <gtlib_api.h>
#include <gr_sync_block.h>

class gtlib_ofdm_sampler;
typedef boost::shared_ptr<gtlib_ofdm_sampler> gtlib_ofdm_sampler_sptr;

GTLIB_API gtlib_ofdm_sampler_sptr gtlib_make_ofdm_sampler (unsigned int fft_length, 
						     unsigned int symbol_length,
						     unsigned int timeout=1000);

/*!
 * \brief does the rest of the OFDM stuff
 * \ingroup ofdm_blk
 */
class GTLIB_API gtlib_ofdm_sampler : public gr_block
{
  friend GTLIB_API gtlib_ofdm_sampler_sptr gtlib_make_ofdm_sampler (unsigned int fft_length, 
							      unsigned int symbol_length,
							      unsigned int timeout);

  gtlib_ofdm_sampler (unsigned int fft_length, 
			unsigned int symbol_length,
			unsigned int timeout);

 private:
  enum state_t {STATE_NO_SIG, STATE_PREAMBLE, STATE_FRAME};

  state_t d_state;
  unsigned int d_timeout_max;
  unsigned int d_timeout;
  unsigned int d_fft_length;
  unsigned int d_symbol_length;

 public:
  void forecast (int noutput_items, gr_vector_int &ninput_items_required);

  int general_work (int noutput_items,
		    gr_vector_int &ninput_items,
		    gr_vector_const_void_star &input_items,
		    gr_vector_void_star &output_items);
};

#endif /* INCLUDED_GTLIB_OFDM_SAMPLER_H */

