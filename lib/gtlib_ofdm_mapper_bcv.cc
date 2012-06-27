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
#include <gtlib_ofdm_mapper_bcv.h>

#define VERBOSE 0

#include <stdexcept>
#include <string.h>
#include <stdio.h>
#include <iostream>

gtlib_ofdm_mapper_bcv_sptr
gtlib_make_ofdm_mapper_bcv (const std::vector<gr_complex> &constellation, unsigned int msgq_limit, 
			 const std::vector<int> &carrier_map, unsigned int fft_length)
{
  return gnuradio::get_initial_sptr(new gtlib_ofdm_mapper_bcv (constellation, msgq_limit, 
							  carrier_map, fft_length));
}

// Consumes 1 packet and produces as many OFDM symbols of fft_length to hold the full packet
gtlib_ofdm_mapper_bcv::gtlib_ofdm_mapper_bcv (const std::vector<gr_complex> &constellation, unsigned int msgq_limit, 
					const std::vector<int> &carrier_map, unsigned int fft_length)
  : gr_sync_block ("ofdm_mapper_bcv",
		   gr_make_io_signature (0, 0, 0),
		   gr_make_io_signature2 (1, 2, sizeof(gr_complex)*fft_length, sizeof(char))),
    d_constellation(constellation),
    d_msgq(gr_make_msg_queue(msgq_limit)), d_msg_offset(0), d_eof(false),
    d_carrier_map(carrier_map),
    d_fft_length(fft_length),
    d_bit_offset(0),
    d_pending_flag(0),
    d_resid(0),
    d_nresid(0)
{
    if (!(d_carrier_map.size() <= d_fft_length))
        throw std::invalid_argument("gtlib_ofdm_mapper_bcv: occupied carriers must be <= fft_length");

    d_nbits = (unsigned long)ceil(log10(float(d_constellation.size())) / log10(2.0));
    
    printf ( "[OFDM] Sub Carrier Mapping \n");

    for(int i = 0; i < d_carrier_map.size(); i++)
    {
        printf ( "%d, ",d_carrier_map[i]);
    }    
    printf ( "\n");
    printf ( "[OFDM] Carrier Map Size=%d\n",d_carrier_map.size());
    
}

gtlib_ofdm_mapper_bcv::~gtlib_ofdm_mapper_bcv(void)
{
}

int gtlib_ofdm_mapper_bcv::randsym()
{
  return (rand() % d_constellation.size());
}

int
gtlib_ofdm_mapper_bcv::work(int noutput_items,
			  gr_vector_const_void_star &input_items,
			  gr_vector_void_star &output_items)
{
    gr_complex *out = (gr_complex *)output_items[0];

    unsigned int i=0;

    //printf("OFDM BPSK Mapper:  ninput_items: %d   noutput_items: %d\n", ninput_items[0], noutput_items);

    if(d_eof)
    {
        return -1;
    }
  
    if(!d_msg)
    {
        d_msg = d_msgq->delete_head();	   // block, waiting for a message
        d_msg_offset = 0;
        d_bit_offset = 0;
        d_pending_flag = 1;			   // new packet, write start of packet flag
    
        printf("[OFDM] Make message length = %d, msg_offset =%d, bit_offset=%d\n",d_msg->length(),d_msg_offset,d_bit_offset);
    
        if((d_msg->length() == 0) && (d_msg->type() == 1))
        {
            d_msg.reset();
            return -1;		// We're done; no more messages coming.
        }
    }

    

    char *out_flag = 0;
    if(output_items.size() == 2)
    out_flag = (char *) output_items[1];

    // Build a single symbol:
    // Initialize all bins to 0 to set unused carriers
    memset(out, 0, d_fft_length*sizeof(gr_complex));

    i = 0;
    unsigned char bits = 0;
    //while((d_msg_offset < d_msg->length()) && (i < d_occupied_carriers)) {
  
    while((d_msg_offset < d_msg->length()) && (i < d_carrier_map.size())) 
    {

        // need new data to process
        if(d_bit_offset == 0) 
        {
            d_msgbytes = d_msg->msg()[d_msg_offset];
          //if (VERBOSE)
          //    printf("mod message byte: %x\n", d_msgbytes);
        }

        if(d_nresid > 0) {
            // take the residual bits, fill out nbits with info from the new byte, and put them in the symbol
            d_resid |= (((1 << d_nresid)-1) & d_msgbytes) << (d_nbits - d_nresid);
            bits = d_resid;

            out[d_carrier_map[i]] = d_constellation[bits];
            i++;

            d_bit_offset += d_nresid;
            d_nresid = 0;
            d_resid = 0;
            if (VERBOSE)
            printf("mod bit(r): %x   resid: %x   nresid: %d    bit_offset: %d\n", 
              bits, d_resid, d_nresid, d_bit_offset);
        }
        else 
        {
            // test to make sure we can fit nbits
            if((8 - d_bit_offset) >= d_nbits)   
            {  
                // take the nbits number of bits at a time from the byte to add to the symbol

                bits = ((1 << d_nbits)-1) & (d_msgbytes >> d_bit_offset);
                
                d_bit_offset += d_nbits;
	
                out[d_carrier_map[i]] = d_constellation[bits];
	
                i++;
            }
            // if we can't fit nbits, store them for the next 
            else
            {  
                // saves d_nresid bits of this message where d_nresid < d_nbits
                unsigned int extra = 8-d_bit_offset;
                d_resid = ((1 << extra)-1) & (d_msgbytes >> d_bit_offset);
                d_bit_offset += extra;
                d_nresid = d_nbits - extra;
            }
        }
                
        if(d_bit_offset == 8)
        {
            d_bit_offset = 0;
            d_msg_offset++;
        }
    }

    // Ran out of data to put in symbol
    if (d_msg_offset == d_msg->length())
    {
        if(d_nresid > 0) 
        {
            d_resid |= 0x00;
            bits = d_resid;
            d_nresid = 0;
            d_resid = 0;
        }

        //while(i < d_occupied_carriers) {   // finish filling out the symbol

        // finish filling out the symbol
        while(i < d_carrier_map.size()) 
        {   
        //out[d_subcarrier_map[i]] = d_constellation[randsym()];
        //out[d_subcarrier_map[i]] = d_constellation[0];

            i++;
        }

        // type == 1 sets EOF
        if (d_msg->type() == 1) d_eof = true;
        d_msg.reset();   			// finished packet, free message
        assert(d_bit_offset == 0);
    }

    if (out_flag) out_flag[0] = d_pending_flag;
    
    d_pending_flag = 0;

    return 1;  // produced symbol
}
