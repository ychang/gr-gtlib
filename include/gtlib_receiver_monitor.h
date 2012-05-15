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

#ifndef INCLUDED_GTLIB_RECEIVER_MONITOR_H
#define INCLUDED_GTLIB_RECEIVER_MONITOR_H

#include <gtlib_api.h>
#include <gr_block.h>

class gtlib_receiver_monitor;
typedef boost::shared_ptr<gtlib_receiver_monitor> gtlib_receiver_monitor_sptr;

GTLIB_API gtlib_receiver_monitor_sptr gtlib_make_receiver_monitor ();

/*!
 * \brief <+description+>
 *
 */
class GTLIB_API gtlib_receiver_monitor : public gr_block
{
	friend GTLIB_API gtlib_receiver_monitor_sptr gtlib_make_receiver_monitor ();

	gtlib_receiver_monitor ();

 public:
	~gtlib_receiver_monitor ();


  int general_work (int noutput_items,
		    gr_vector_int &ninput_items,
		    gr_vector_const_void_star &input_items,
		    gr_vector_void_star &output_items);
};

#endif /* INCLUDED_GTLIB_RECEIVER_MONITOR_H */

