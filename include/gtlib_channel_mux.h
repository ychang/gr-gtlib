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

#ifndef INCLUDED_GTLIB_CHANNEL_MUX_H
#define INCLUDED_GTLIB_CHANNEL_MUX_H

#include <gtlib_api.h>
#include <gr_block.h>

#define TRUE  1
#define FALSE 0

class gtlib_channel_mux;
typedef boost::shared_ptr<gtlib_channel_mux> gtlib_channel_mux_sptr;

GTLIB_API gtlib_channel_mux_sptr 
gtlib_make_channel_mux (size_t itemsize, const std::vector<int> &lengths);

/*!
 * \brief Stream muxing block to multiplex many streams into
 * one with a specified format.
 * 
 * Muxes N streams together producing an output stream that
 * contains N0 items from the first stream, N1 items from the second,
 * etc. and repeats:
 *
 * [N0, N1, N2, ..., Nm, N0, N1, ...]
 */

class GTLIB_API gtlib_channel_mux : public gr_block
{
  friend gtlib_channel_mux_sptr
    gtlib_make_channel_mux (size_t itemsize, const std::vector<int> &lengths);
  
 protected:
   gtlib_channel_mux (size_t itemsize, const std::vector<int> &lengths);

 private:
  size_t d_itemsize;
  unsigned int d_stream;    // index of currently selected stream
  int d_residual;           // number if items left to put into current stream
  gr_vector_int d_lengths;  // number if items to pack per stream
  gr_vector_int d_lengths_scheduled;  // number if items to pack per stream
  bool d_scheduled;
 
  void increment_stream();

 public:
  ~gtlib_channel_mux(void);

 void reset_stream();

 void forecast (int noutput_items, gr_vector_int &ninput_items_required);
 void schedule_stream_length(const std::vector<int> &lengths);
 
  int general_work(int noutput_items,
		   gr_vector_int &ninput_items,
		   gr_vector_const_void_star &input_items,
		   gr_vector_void_star &output_items);

};


#endif
