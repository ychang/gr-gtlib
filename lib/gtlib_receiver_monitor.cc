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

#include <unistd.h>
#include <stdio.h>
#include <time.h>
#include <gr_io_signature.h>
#include <gtlib_receiver_monitor.h>


gtlib_receiver_monitor_sptr
gtlib_make_receiver_monitor ()
{
	return gtlib_receiver_monitor_sptr (new gtlib_receiver_monitor ());
}

timespec diff(timespec start, timespec end)
{
	timespec temp;
	if ((end.tv_nsec-start.tv_nsec)<0) {
		temp.tv_sec = end.tv_sec-start.tv_sec-1;
		temp.tv_nsec = 1000000000+end.tv_nsec-start.tv_nsec;
	} else {
		temp.tv_sec = end.tv_sec-start.tv_sec;
		temp.tv_nsec = end.tv_nsec-start.tv_nsec;
	}
	return temp;
}



gtlib_receiver_monitor::gtlib_receiver_monitor ()
	: gr_block ("receiver_monitor",
		gr_make_io_signature (1, 1, sizeof (gr_complex)),
		gr_make_io_signature (1, 1, sizeof (gr_complex)))
{

    timespec current_time;

    clock_gettime(CLOCK_REALTIME, &initial_time);
    usleep(1000000);
    clock_gettime(CLOCK_REALTIME, &current_time);
    fprintf(stderr,">>> [RxMon] Time diff= %f\n", diff(initial_time,current_time).tv_sec + (float)(diff(initial_time,current_time).tv_nsec)/1000000000);

}


gtlib_receiver_monitor::~gtlib_receiver_monitor ()
{
}

int
gtlib_receiver_monitor::general_work (int noutput_items,
			       gr_vector_int &ninput_items,
			       gr_vector_const_void_star &input_items,
			       gr_vector_void_star &output_items)
{
  const gr_complex *in = (const gr_complex *) input_items[0];
  gr_complex *out = (gr_complex *) output_items[0];

  timespec current_time;
  timespec time_diff;
  
  clock_gettime(CLOCK_REALTIME, &current_time);
  time_diff = diff(initial_time,current_time);
  
  printf(">>> [RxMon] nitems=%d @ %ld.%09ld\n",noutput_items,time_diff.tv_sec,time_diff.tv_nsec );
  
  // Tell runtime system how many input items we consumed on
  // each input stream.
  consume_each (noutput_items);

  // Tell runtime system how many output items we produced.
  return noutput_items;
}

