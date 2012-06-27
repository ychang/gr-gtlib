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

#ifndef INCLUDED_GTLIB_OFDM_CYCLIC_PREFIXER_H
#define INCLUDED_GTLIB_OFDM_CYCLIC_PREFIXER_H


#include <gtlib_api.h>
#include <gr_sync_interpolator.h>
#include <stdio.h>

class gtlib_ofdm_cyclic_prefixer;
typedef boost::shared_ptr<gtlib_ofdm_cyclic_prefixer> gtlib_ofdm_cyclic_prefixer_sptr;

GTLIB_API gtlib_ofdm_cyclic_prefixer_sptr 
gtlib_make_ofdm_cyclic_prefixer (size_t input_size, size_t output_size);


/*!
 * \brief adds a cyclic prefix vector to an input size long ofdm
 * symbol(vector) and converts vector to a stream output_size long.
 * \ingroup ofdm_blk
 */
class GTLIB_API gtlib_ofdm_cyclic_prefixer : public gr_sync_interpolator
{
  friend GTLIB_API gtlib_ofdm_cyclic_prefixer_sptr
    gtlib_make_ofdm_cyclic_prefixer (size_t input_size, size_t output_size);

 protected:
  gtlib_ofdm_cyclic_prefixer (size_t input_size, size_t output_size);

 public:
  int work (int noutput_items,
	    gr_vector_const_void_star &input_items,
	    gr_vector_void_star &output_items);
 private:
  size_t d_input_size;
  size_t d_output_size;
};

#endif /* INCLUDED_GTLIB_OFDM_CYCLIC_PREFIXER_H */

