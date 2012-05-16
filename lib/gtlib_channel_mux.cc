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
#include <gtlib_channel_mux.h>
#include <string.h>
#include <cstdio>

#define VERBOSE 0

gtlib_channel_mux_sptr
gtlib_make_channel_mux (size_t itemsize, const std::vector<int> &lengths)
{
  return gnuradio::get_initial_sptr(new gtlib_channel_mux (itemsize, lengths));
}

gtlib_channel_mux::gtlib_channel_mux (size_t itemsize, const std::vector<int> &lengths)
  : gr_block ("channel_mux",
	      gr_make_io_signature (1, -1, itemsize),
	      gr_make_io_signature (1, 1, itemsize)),
    d_itemsize(itemsize),
    d_stream(0),
    d_residual(0),
    d_lengths(lengths), d_lengths_scheduled(lengths)
{
  if(d_lengths[d_stream] == 0) {
    increment_stream();
  }
  d_residual = d_lengths[d_stream];
  if(VERBOSE) {
      printf("Stream Mux is setup\n");
  }
  d_scheduled = FALSE;
}    

gtlib_channel_mux::~gtlib_channel_mux(void)
{
}

void 
gtlib_channel_mux::forecast (int noutput_items, gr_vector_int &ninput_items_required)
{
  unsigned ninputs = ninput_items_required.size ();
  for (unsigned i = 0; i < ninputs; i++)
    ninput_items_required[i] = (d_lengths[i] == 0 ? 0 : 1);
}

void gtlib_channel_mux::schedule_stream_length(const std::vector<int> &lengths)
{
 d_scheduled = TRUE;
 
 //for (int ii=0;ii<lengths.size();ii++)
 copy(lengths.begin(),lengths.end(),d_lengths_scheduled.begin());   
}

void gtlib_channel_mux::increment_stream()
{
  do {
    d_stream = (d_stream+1) % d_lengths.size();
  } while(d_lengths[d_stream] == 0);

  if (d_stream == 0)
  {
    copy(d_lengths_scheduled.begin(),d_lengths_scheduled.end(),d_lengths.begin());     
    d_scheduled=FALSE;
  }
  
  d_residual = d_lengths[d_stream];
}

void gtlib_channel_mux::reset_stream()
{
  d_stream = 0;
  d_residual = d_lengths[d_stream];
}


int
gtlib_channel_mux::general_work(int noutput_items,
			    gr_vector_int &ninput_items,
			    gr_vector_const_void_star &input_items,
			    gr_vector_void_star &output_items)
{
    char *out = (char *) output_items[0];
    const char *in;
    int out_index = 0;
    std::vector<int> input_index(d_lengths.size(), 0);

    if(VERBOSE) {
      printf("mux: nouput_items: %d   d_stream: %d\n", noutput_items, d_stream);
      for(size_t i = 0; i < d_lengths.size(); i++)
	printf("\tninput_items[%zu]: %d\n", i, ninput_items[i]);
    }

    while (1) {
      int r = std::min(noutput_items - out_index,
		       std::min(d_residual,
				ninput_items[d_stream] - input_index[d_stream]));
      if(VERBOSE) {
	printf("mux: r=%d\n", r);
	printf("\tnoutput_items - out_index: %d\n", 
	       noutput_items - out_index);
	printf("\td_residual: %d\n", 
	       d_residual);
	printf("\tninput_items[d_stream] - input_index[d_stream]: %d\n", 
	       ninput_items[d_stream] - input_index[d_stream]);
      }

      if(r <= 0) {
	return out_index;
      }

      in = (const char *) input_items[d_stream] + input_index[d_stream]*d_itemsize;
      
      memcpy(&out[out_index*d_itemsize], in, r*d_itemsize);
      out_index += r;
      input_index[d_stream] += r;
      d_residual -= r;

      consume(d_stream, r);
      
      if(d_residual == 0) {
      
	increment_stream();
      }
    }
}
