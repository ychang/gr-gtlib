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

#ifndef INCLUDED_gtlib_bfsk_MODULATOR_FC_H
#define INCLUDED_gtlib_bfsk_MODULATOR_FC_H

#include <gtlib_api.h>
#include <gr_sync_block.h>

class gtlib_bfsk_modulator_fc;
typedef boost::shared_ptr<gtlib_bfsk_modulator_fc> gtlib_bfsk_modulator_fc_sptr;

GTLIB_API gtlib_bfsk_modulator_fc_sptr gtlib_make_bfsk_modulator_fc (double sensitivity_a,double sensitivity_b);

/*!
 * \brief Frequency modulator block
 * \ingroup modulation
 *
 * float input; complex baseband output
 */
class GTLIB_API gtlib_bfsk_modulator_fc : public gr_sync_block
{
  double	d_sensitivity_a;
  double	d_sensitivity_b;
  double	d_phase;

  friend GTLIB_API gtlib_bfsk_modulator_fc_sptr
  gtlib_make_bfsk_modulator_fc (double sensitivity_a,double sensitivity_b);

  gtlib_bfsk_modulator_fc (double sensitivity_a,double sensitivity_b);

 public:
    void set_sensitivity(double sensitivity_a,double sensitivity_b);
  int work (int noutput_items,
	    gr_vector_const_void_star &input_items,
	    gr_vector_void_star &output_items);
};

#endif /* INCLUDED_gtlib_bfsk_modulator_FC_H */
