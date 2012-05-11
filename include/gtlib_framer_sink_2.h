/* -*- c++ -*- */
/*
 * Copyright 2005,2006 Free Software Foundation, Inc.
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

#ifndef INCLUDED_gtlib_framer_sink_2_H
#define INCLUDED_gtlib_framer_sink_2_H

#include <gtlib_api.h>
#include <gr_sync_block.h>
#include <gr_msg_queue.h>

#define WLSQ_MAX        4096*4
#define STF_M_LENGTH    32
#define META_MAX        1024

class gtlib_framer_sink_2;
typedef boost::shared_ptr<gtlib_framer_sink_2> gtlib_framer_sink_2_sptr;

typedef struct {
    unsigned int        header;
    unsigned long       rssi;
    unsigned long long  rtg;    // Received time-tag
    double              sps;
} t_pktmeta;


typedef struct {
    int             index;
    int             bit_cnt;
    double          stack[WLSQ_MAX];
    int             bit[WLSQ_MAX];
} t_wlsq_stack;

GTLIB_API gtlib_framer_sink_2_sptr 
gtlib_make_framer_sink_2 (int sfo,gr_msg_queue_sptr target_queue, bool complementary_header);

/*!
 * \brief Given a stream of bits and access_code flags, assemble packets.
 * \ingroup sink
 *
 * input: stream of bytes from gr_correlate_access_code_bb
 * output: none.  Pushes assembled packet into target queue
 *
 * The framer expects a fixed length header of 2 16-bit shorts
 * containing the payload length, followed by the payload.  If the 
 * 2 16-bit shorts are not identical, this packet is ignored.  Better
 * algs are welcome.
 *
 * The input data consists of bytes that have two bits used.
 * Bit 0, the LSB, contains the data bit.
 * Bit 1 if set, indicates that the corresponding bit is the
 * the first bit of the packet.  That is, this bit is the first
 * one after the access code.
 */
class GTLIB_API gtlib_framer_sink_2 : public gr_sync_block
{
    friend GTLIB_API gtlib_framer_sink_2_sptr 
    gtlib_make_framer_sink_2 (int sfo,gr_msg_queue_sptr target_queue, bool complementary_header);

    gtlib_framer_sink_2(int sfo,gr_msg_queue_sptr target_queue, bool complementary_header);

    enum state_t {STATE_SYNC_SEARCH, STATE_HAVE_SYNC, STATE_HAVE_HEADER, STATE_HAVE_SCSF_WAIT};

    static const int MAX_PKT_LEN    = 4096;
    static const int HEADERBITLEN   = 32;

    gr_msg_queue_sptr  d_target_queue;		// where to send the packet when received
    state_t         d_state;
    unsigned int    d_header;			// header bits
    int		        d_headerbitlen_cnt;	// how many so far

    bool            d_complementary_header;
    
    unsigned char   d_packet[MAX_PKT_LEN];	// assembled payload
    unsigned char	d_packet_byte;		// byte being assembled
    int		        d_packet_byte_index;	// which bit of d_packet_byte we're working on
    int 		    d_packetlen;		// length of packet
    int             d_packet_whitener_offset;  // offset into whitener string to use
    int             d_packetlen_cnt;		// how many so far
    unsigned long int   d_signal_power;

    unsigned int    d_scsf_wait;

    double      d_wlsq_sps;
    double      d_wlsq_toa;

    unsigned long int avg_rssi_count;
    unsigned long long int cum_rssi;
    unsigned long long int cum_noise;

    int         d_sfo;

    t_wlsq_stack         d_wlsq_track;
    t_pktmeta            d_pktmeta[META_MAX];
    
    unsigned int         prev_symbol;
    long                 d_pktmeta_idx;
 

    void enter_search();
    void enter_have_sync();
    void enter_have_header(int payload_len, int whitener_offset);
    void enter_have_scsf_wait(int payload_len, int whitener_offset, int length);

    double ull2dbl(unsigned long long data);
    unsigned long long dbl2ull(double data);

    double least_square(void);

 
    bool header_ok()
    {
        if (d_complementary_header)
            // confirm that two copies of header info are identical
            return ((d_header >> 16) ^ ((d_header & 0xffff)^0xffff)) == 0;
        else
            // confirm that two copies of header info are identical
            return ((d_header >> 16) ^ (d_header & 0xffff)) == 0;
        
    }

    void header_payload(int *len, int *offset)
    {
        // header consists of two 16-bit shorts in network byte order
        // payload length is lower 12 bits
        // whitener offset is upper 4 bits
        *len = (d_header >> 16) & 0x0fff;
        *offset = (d_header >> 28) & 0x000f;
    }

    public:

    int work(int noutput_items,
	   gr_vector_const_void_star &input_items,
	   gr_vector_void_star &output_items);
	   
    
    unsigned int meta_header(long idx)
    {
        return (d_pktmeta[idx%META_MAX].header); 
    }   
    
    unsigned long meta_rssi(long idx)
    {
        return (d_pktmeta[idx%META_MAX].rssi); 
    }   

    unsigned long long meta_rtg(long idx)
    {
        return (d_pktmeta[idx%META_MAX].rtg); 
    }   

    double meta_sps(long idx)
    {
        return (d_pktmeta[idx%META_MAX].sps); 
    }   

};

#endif /* INCLUDED_gtlib_framer_sink_2_H */
