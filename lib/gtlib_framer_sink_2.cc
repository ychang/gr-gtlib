/* -*- c++ -*- */
/*
 * Copyright 2004,2006 Free Software Foundation, Inc.
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

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gtlib_framer_sink_2.h>
#include <gr_io_signature.h>
#include <cstdio>
#include <stdexcept>
#include <string.h>

#define VERBOSE 0

gtlib_framer_sink_2_sptr
gtlib_make_framer_sink_2(int sfo,gr_msg_queue_sptr target_queue, bool complementary_header)
{
  return gtlib_framer_sink_2_sptr(new gtlib_framer_sink_2(sfo,target_queue, complementary_header));
}

gtlib_framer_sink_2::gtlib_framer_sink_2(int sfo,gr_msg_queue_sptr target_queue, bool complementary_header)
  : gr_sync_block ("framer_sink_2",
		   gr_make_io_signature2 (1, 2, sizeof(unsigned long long), sizeof(unsigned long)),
		   gr_make_io_signature (0, 0, 0)),
           d_sfo(sfo),
           d_target_queue(target_queue),
           d_complementary_header(complementary_header)
{
    cum_rssi=0;
    cum_noise = 0;
    avg_rssi_count = 0; 

    d_state = STATE_SYNC_SEARCH;

}


inline void
gtlib_framer_sink_2::enter_search()
{
//  if (VERBOSE)
//    fprintf(stderr, "@ enter_search\n");

  d_state = STATE_SYNC_SEARCH;
}
    
inline void
gtlib_framer_sink_2::enter_have_sync()
{
  if (VERBOSE)
    fprintf(stderr, "@ enter_have_sync\n");

  d_state = STATE_HAVE_SYNC;
  d_header = 0;
  d_headerbitlen_cnt = 0;
}

inline void
gtlib_framer_sink_2::enter_have_header(int payload_len, int whitener_offset)
{
  if (VERBOSE)
    fprintf(stderr, "@ enter_have_header (payload_len = %d) (offset = %d)\n", payload_len, whitener_offset);

  d_state = STATE_HAVE_HEADER;
  d_packetlen = payload_len;
  d_packet_whitener_offset = whitener_offset;
  d_packetlen_cnt = 0;
  d_packet_byte = 0;
  d_packet_byte_index = 0;
  d_pktmeta_idx = 0;
  
}

inline void
gtlib_framer_sink_2::enter_have_scsf_wait(int payload_len, int whitener_offset, int length)
{
  if (VERBOSE)
    fprintf(stderr, "@ enter_have_scsf_wait (payload_len = %d) (offset = %d)\n", payload_len, whitener_offset);

  d_state = STATE_HAVE_SCSF_WAIT;
  d_packetlen = payload_len;
  d_packet_whitener_offset = whitener_offset;
  d_packetlen_cnt = 0;
  d_packet_byte = 0;
  d_packet_byte_index = 0;
  d_pktmeta_idx = 0;
  d_scsf_wait = length;
}

double 
gtlib_framer_sink_2::ull2dbl(unsigned long long data)
{
    double dbl_data;
    
    dbl_data = (double)(data>>8);
    dbl_data += (double)(data&0xFF)/256;
    return dbl_data;
    
}

unsigned long long 
gtlib_framer_sink_2::dbl2ull(double data)
{
    unsigned long long ull_data;
    
    ull_data = (unsigned long long)floor(data)<<8;
    ull_data += ((unsigned long long)floor(data*256)&0xFF);
    return ull_data;
    
}

double
gtlib_framer_sink_2::least_square(void)
{
    double SUMx, SUMy, SUMxy, SUMxx, slope,y_intercept;
    int d_stf_len;
    
    d_stf_len = d_wlsq_track.index-1;

    SUMx = 0; SUMy = 0; SUMxy = 0; SUMxx = 0;

    for (int i=1; i<(d_stf_len+1); i++)
    {
        SUMx = SUMx + d_wlsq_track.bit[i];
        SUMy = SUMy + d_wlsq_track.stack[i];
        SUMxy = SUMxy + d_wlsq_track.bit[i]*d_wlsq_track.stack[i];
        SUMxx = SUMxx + d_wlsq_track.bit[i]*d_wlsq_track.bit[i];
    }
    
    //y_intercept = (SUMxx*(STF_M_LENGTH*d_wlsq_track.stack[0]+SUMy) - SUMx*SUMxy) / ((STF_M_LENGTH+d_stf_len)*SUMxx - SUMx*SUMx);
    slope = (d_stf_len*SUMxy - SUMx*SUMy) / (d_stf_len*SUMxx - SUMx*SUMx);
   
    d_wlsq_sps = slope;
    d_wlsq_toa = y_intercept;

    return y_intercept;
}


int
gtlib_framer_sink_2::work (int noutput_items,
			gr_vector_const_void_star &input_items,
			gr_vector_void_star &output_items)
{
  unsigned long long *in_ts = (unsigned long long*) input_items[0];
  const unsigned long *in_symbol = (const unsigned long *) input_items[1];
  //const unsigned long *in_noise = (const unsigned long *) input_items[2];
  int count=0;
    
    unsigned long rssi_temp;
    unsigned long noise_temp;
    
 
    unsigned long long time_tag;
    
 // if (VERBOSE)
 //   fprintf(stderr,">>> Entering state machine\n");

    while (count < noutput_items){
        switch(d_state) {
            case STATE_SYNC_SEARCH:    // Look for flag indicating beginning of pkt

                while (count < noutput_items) {
                
                    // =============================================
                    // START OF PACKET DETECTION
                    // =============================================
                   
                    if (in_symbol[count] & 0x6){  // Found it, set up for header decode
                            
	                    //enter_have_sync();
	                    d_state = STATE_HAVE_SYNC;
                        d_header = 0;
                        d_headerbitlen_cnt = 0;
                        d_wlsq_track.index=0;
                        
                        d_wlsq_track.stack[d_wlsq_track.index]=ull2dbl(in_ts[count]);                                            
                        d_wlsq_track.bit_cnt=0;
                        d_wlsq_track.bit[d_wlsq_track.index]=d_wlsq_track.bit_cnt;
                        d_wlsq_track.index++;	
                        prev_symbol = 0xFF;                    
	                    break;
	                }
	                count++;
                }
                break;

            case STATE_HAVE_SYNC:
                if (VERBOSE)
	                fprintf(stderr,"Header Search bitcnt=%d, header=0x%08x\n",d_headerbitlen_cnt, d_header);

                while (count < noutput_items) {	// Shift bits one at a time into header
                    d_header = (d_header << 1) | (in_symbol[count] & 0x1);

                    // ===================================================================
                    // GET WLSQ DATA
                    // ===================================================================
                    
                    if((prev_symbol!=(in_symbol[count]&0x1)) && (prev_symbol!=0xFF)) 
                    {
                        d_wlsq_track.stack[d_wlsq_track.index]=ull2dbl(in_ts[count]);                                
                        d_wlsq_track.bit[d_wlsq_track.index]=d_wlsq_track.bit_cnt;
                        d_wlsq_track.index++;
                    }
                    d_wlsq_track.bit_cnt++;            

                    prev_symbol = in_symbol[count]&0x1;
                    count++;
                    
                    if (++d_headerbitlen_cnt == HEADERBITLEN) 
                    {
                        if (VERBOSE) fprintf(stderr, "got header: 0x%08x\n", d_header);

	                    // we have a full header, check to see if it has been received properly
	                    if (header_ok()){
                            int payload_len;
                            int whitener_offset;
                            header_payload(&payload_len, &whitener_offset);
                            
                            avg_rssi_count=0;
                            cum_rssi=0;
                            cum_noise=0;

                            enter_have_header(payload_len, whitener_offset);

                            if (d_packetlen == 0 || d_packetlen > 1500){	    // check for zero-length payload
	                            // build a zero-length message
	                            // NOTE: passing header field as arg1 is not scalable
                                

                                gr_message_sptr msg =
                                      gr_make_message(0, 0, 0, 0);
                                d_target_queue->insert_tail(msg);		// send it
                                msg.reset();  				// free it up
                                
	                            d_state = STATE_SYNC_SEARCH;
	                        }
	                    }
	                    // Bad header
	                    else 
	                    {
                            // build a zero-length message
                            // NOTE: passing header field as arg1 is not scalable
                            
                            gr_message_sptr msg =
                                  gr_make_message(0, 0, 0, 0);
                            d_target_queue->insert_tail(msg);		// send it
                            msg.reset();  				// free it up
	                    
	                        d_state = STATE_SYNC_SEARCH;
	                    }
	                    
	                    break;					// we're in a new state
	                }
                }
                break;
        
            case STATE_HAVE_SCSF_WAIT:
                if (VERBOSE) fprintf(stderr,"SCSF Wait\n");
                
                while (count < noutput_items && (d_scsf_wait--))
                {	// Shift bits one at a time into header
                    count++;
                    if (!d_scsf_wait) break;
                }
                if (!d_scsf_wait)
                {
                    d_state = STATE_HAVE_HEADER;
                }
                break;
                                
      
            case STATE_HAVE_HEADER:
                if (VERBOSE) fprintf(stderr,"Packet Build\n");

                while (count < noutput_items)
                {   // shift bits into bytes of packet one at a time
	                d_packet_byte = (d_packet_byte << 1) | (in_symbol[count] & 0x1);

                    // ===================================================================
                    // GET WLSQ DATA
                    // ===================================================================
                    
                    if (d_wlsq_track.index < WLSQ_MAX)
                    {
                        if((prev_symbol!=(in_symbol[count]&0x1)) && (prev_symbol!=0xFF)) 
                        {
                            d_wlsq_track.stack[d_wlsq_track.index]=ull2dbl(in_ts[count]);                                
                            d_wlsq_track.bit[d_wlsq_track.index]=d_wlsq_track.bit_cnt;
                            d_wlsq_track.index++;
                        }
                        d_wlsq_track.bit_cnt++;            
                    }
                    prev_symbol = in_symbol[count]&0x1;
                    count++;
                    
                    rssi_temp = (in_symbol[count-1]>>2);
                    //noise_temp = (in_noise[count-1]>>2);
                    

                    cum_rssi += (unsigned long long)(rssi_temp);
                    //cum_noise += (unsigned long long)(noise_temp);
                    
                    avg_rssi_count++;

	                if (d_packet_byte_index++ == 7)
	                {	  	// byte is full so move to next byte
	                    d_packet[d_packetlen_cnt++] = d_packet_byte;
	                    d_packet_byte_index = 0;

	                    if (d_packetlen_cnt == d_packetlen){		// packet is filled
	                        // build a message
	                        // NOTE: passing header field as arg1 is not scalable
                            
                            if (d_sfo) least_square();

                            time_tag = dbl2ull(d_wlsq_track.stack[0]);
                            //fprintf(stdout,"RTG : %f, %lld\n",d_wlsq_track.stack[0],time_tag);

                            
                            d_signal_power = (unsigned long int)(cum_rssi / avg_rssi_count);
                            
                              //gr_make_message(0, time_tag, d_signal_power, (unsigned long)(d_wlsq_sps*100000));

                            //gr_message_sptr msg =
                            //      gr_make_message(0, time_tag, d_signal_power, d_wlsq_sps, d_packetlen_cnt);

                            d_pktmeta[d_pktmeta_idx].header = (unsigned int)((d_header>>16)&0xFFFF);
                            d_pktmeta[d_pktmeta_idx].rtg = time_tag;
                            d_pktmeta[d_pktmeta_idx].rssi = d_signal_power;
                            d_pktmeta[d_pktmeta_idx].sps = d_wlsq_sps;
                            
                            gr_message_sptr msg =
                                  gr_make_message(d_pktmeta_idx, 0, 0, d_packetlen_cnt);
                            memcpy(msg->msg(), d_packet, d_packetlen_cnt);
                            d_target_queue->insert_tail(msg);		// send it
                            msg.reset();  				// free it up

                            d_state = STATE_SYNC_SEARCH;
                            
                            d_pktmeta_idx = (d_pktmeta_idx+1)%META_MAX;
                            
	                        break;
	                    }
	                }
                }
                break;

            default: assert(0);

        } // switch

    }   // while

    return noutput_items;
}
