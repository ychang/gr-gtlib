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

#ifndef INCLUDED_GTLIB_OFDM_STBC_DECODER_H
#define INCLUDED_GTLIB_OFDM_STBC_DECODER_H

#include <gtlib_api.h>
#include <gr_block.h>

class gtlib_ofdm_stbc_decoder;
typedef boost::shared_ptr<gtlib_ofdm_stbc_decoder> gtlib_ofdm_stbc_decoder_sptr;

GTLIB_API gtlib_ofdm_stbc_decoder_sptr gtlib_make_ofdm_stbc_decoder (unsigned int fft_length);

/*!
 * \brief <+description+>
 *
 */
class GTLIB_API gtlib_ofdm_stbc_decoder : public gr_block
{
	friend GTLIB_API gtlib_ofdm_stbc_decoder_sptr gtlib_make_ofdm_stbc_decoder (unsigned int fft_length);

	gtlib_ofdm_stbc_decoder (unsigned int fft_length);

    private:
        unsigned int d_fft_length;

 public:
	~gtlib_ofdm_stbc_decoder ();


  int general_work (int noutput_items,
		    gr_vector_int &ninput_items,
		    gr_vector_const_void_star &input_items,
		    gr_vector_void_star &output_items);
};

#endif /* INCLUDED_GTLIB_OFDM_STBC_DECODER_H */

