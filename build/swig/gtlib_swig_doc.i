
/*
 * This file was automatically generated using swig_doc.py.
 *
 * Any changes to it will be lost next time it is regenerated.
 */




%feature("docstring") gtlib_bfsk_modulator_fc "Frequency modulator block

float input; complex baseband output."

%feature("docstring") gtlib_bfsk_modulator_fc::gtlib_bfsk_modulator_fc "

Params: (sensitivity_a, sensitivity_b)"

%feature("docstring") gtlib_bfsk_modulator_fc::set_sensitivity "

Params: (sensitivity_a, sensitivity_b)"

%feature("docstring") gtlib_bfsk_modulator_fc::work "

Params: (noutput_items, input_items, output_items)"

%feature("docstring") gtlib_make_bfsk_modulator_fc "Frequency modulator block

float input; complex baseband output.

Params: (sensitivity_a, sensitivity_b)"

%feature("docstring") gtlib_framer_sink_2 "Given a stream of bits and access_code flags, assemble packets.

input: stream of bytes from gr_correlate_access_code_bb output: none. Pushes assembled packet into target queue.

The framer expects a fixed length header of 2 16-bit shorts containing the payload length, followed by the payload. If the 2 16-bit shorts are not identical, this packet is ignored. Better algs are welcome.

The input data consists of bytes that have two bits used. Bit 0, the LSB, contains the data bit. Bit 1 if set, indicates that the corresponding bit is the the first bit of the packet. That is, this bit is the first one after the access code."

%feature("docstring") gtlib_framer_sink_2::gtlib_framer_sink_2 "

Params: (sfo, target_queue, complementary_header)"

%feature("docstring") gtlib_framer_sink_2::enter_search "

Params: (NONE)"

%feature("docstring") gtlib_framer_sink_2::enter_have_sync "

Params: (NONE)"

%feature("docstring") gtlib_framer_sink_2::enter_have_header "

Params: (payload_len, whitener_offset)"

%feature("docstring") gtlib_framer_sink_2::enter_have_scsf_wait "

Params: (payload_len, whitener_offset, length)"

%feature("docstring") gtlib_framer_sink_2::ull2dbl "

Params: (data)"

%feature("docstring") gtlib_framer_sink_2::dbl2ull "

Params: (data)"

%feature("docstring") gtlib_framer_sink_2::least_square "

Params: ()"

%feature("docstring") gtlib_framer_sink_2::header_ok "

Params: (NONE)"

%feature("docstring") gtlib_framer_sink_2::header_payload "

Params: (len, offset)"

%feature("docstring") gtlib_framer_sink_2::work "

Params: (noutput_items, input_items, output_items)"

%feature("docstring") gtlib_framer_sink_2::meta_header "

Params: (idx)"

%feature("docstring") gtlib_framer_sink_2::meta_rssi "

Params: (idx)"

%feature("docstring") gtlib_framer_sink_2::meta_rtg "

Params: (idx)"

%feature("docstring") gtlib_framer_sink_2::meta_sps "

Params: (idx)"

%feature("docstring") gtlib_make_framer_sink_2 "Given a stream of bits and access_code flags, assemble packets.

input: stream of bytes from gr_correlate_access_code_bb output: none. Pushes assembled packet into target queue.

The framer expects a fixed length header of 2 16-bit shorts containing the payload length, followed by the payload. If the 2 16-bit shorts are not identical, this packet is ignored. Better algs are welcome.

The input data consists of bytes that have two bits used. Bit 0, the LSB, contains the data bit. Bit 1 if set, indicates that the corresponding bit is the the first bit of the packet. That is, this bit is the first one after the access code.

Params: (sfo, target_queue, complementary_header)"



%feature("docstring") gtlib_ncbfsk_freq_diversity::~gtlib_ncbfsk_freq_diversity "

Params: (NONE)"

%feature("docstring") gtlib_ncbfsk_freq_diversity::forecast "

Params: (noutput_items, ninput_items_required)"

%feature("docstring") gtlib_ncbfsk_freq_diversity::general_work "

Params: (noutput_items, ninput_items, input_items, output_items)"

%feature("docstring") gtlib_ncbfsk_freq_diversity::set_msequence_code "

Params: (msequence_code)"

%feature("docstring") gtlib_ncbfsk_freq_diversity::parabolic_peak_interpolation "

Params: (d1, d2, d3)"

%feature("docstring") gtlib_ncbfsk_freq_diversity::SPADE_func "

Params: (spade_int, spade_frac)"

%feature("docstring") gtlib_ncbfsk_freq_diversity::unlock "

Params: ()"

%feature("docstring") gtlib_ncbfsk_freq_diversity::mean_estimator "

Params: (data)"

%feature("docstring") gtlib_ncbfsk_freq_diversity::peak_estimator "

Params: (data)"

%feature("docstring") gtlib_ncbfsk_freq_diversity::config_timestamp "

Params: (timestamp_gap)"

%feature("docstring") gtlib_ncbfsk_freq_diversity::gtlib_ncbfsk_freq_diversity "

Params: (sps, gamma, msequence_code, threshold)"

%feature("docstring") gtlib_make_ncbfsk_freq_diversity "

Params: (sps, gamma, msequence_code, threshold)"

%feature("docstring") gtlib_receiver_monitor "<+description+>"

%feature("docstring") gtlib_receiver_monitor::gtlib_receiver_monitor "

Params: (NONE)"

%feature("docstring") gtlib_receiver_monitor::~gtlib_receiver_monitor "

Params: (NONE)"

%feature("docstring") gtlib_receiver_monitor::general_work "

Params: (noutput_items, ninput_items, input_items, output_items)"

%feature("docstring") gtlib_make_receiver_monitor "<+description+>

Params: (NONE)"

%feature("docstring") std::allocator "STL class."

%feature("docstring") std::auto_ptr "STL class."

%feature("docstring") std::bad_alloc "STL class."

%feature("docstring") std::bad_cast "STL class."

%feature("docstring") std::bad_exception "STL class."

%feature("docstring") std::bad_typeid "STL class."

%feature("docstring") std::basic_fstream "STL class."

%feature("docstring") std::basic_ifstream "STL class."

%feature("docstring") std::basic_ios "STL class."

%feature("docstring") std::basic_iostream "STL class."

%feature("docstring") std::basic_istream "STL class."

%feature("docstring") std::basic_istringstream "STL class."

%feature("docstring") std::basic_ofstream "STL class."

%feature("docstring") std::basic_ostream "STL class."

%feature("docstring") std::basic_ostringstream "STL class."

%feature("docstring") std::basic_string "STL class."

%feature("docstring") std::basic_stringstream "STL class."

%feature("docstring") std::bitset "STL class."

%feature("docstring") std::complex "STL class."

%feature("docstring") std::list::const_iterator "STL iterator class."

%feature("docstring") std::map::const_iterator "STL iterator class."

%feature("docstring") std::multimap::const_iterator "STL iterator class."

%feature("docstring") std::set::const_iterator "STL iterator class."

%feature("docstring") std::basic_string::const_iterator "STL iterator class."

%feature("docstring") std::multiset::const_iterator "STL iterator class."

%feature("docstring") std::vector::const_iterator "STL iterator class."

%feature("docstring") std::string::const_iterator "STL iterator class."

%feature("docstring") std::wstring::const_iterator "STL iterator class."

%feature("docstring") std::deque::const_iterator "STL iterator class."

%feature("docstring") std::list::const_reverse_iterator "STL iterator class."

%feature("docstring") std::map::const_reverse_iterator "STL iterator class."

%feature("docstring") std::multimap::const_reverse_iterator "STL iterator class."

%feature("docstring") std::set::const_reverse_iterator "STL iterator class."

%feature("docstring") std::multiset::const_reverse_iterator "STL iterator class."

%feature("docstring") std::basic_string::const_reverse_iterator "STL iterator class."

%feature("docstring") std::vector::const_reverse_iterator "STL iterator class."

%feature("docstring") std::string::const_reverse_iterator "STL iterator class."

%feature("docstring") std::wstring::const_reverse_iterator "STL iterator class."

%feature("docstring") std::deque::const_reverse_iterator "STL iterator class."

%feature("docstring") std::deque "STL class."

%feature("docstring") std::domain_error "STL class."

%feature("docstring") std::exception "STL class."

%feature("docstring") std::ios_base::failure "STL class."

%feature("docstring") std::fstream "STL class."

%feature("docstring") std::ifstream "STL class."

%feature("docstring") std::invalid_argument "STL class."

%feature("docstring") std::ios "STL class."

%feature("docstring") std::ios_base "STL class."

%feature("docstring") std::istream "STL class."

%feature("docstring") std::istringstream "STL class."

%feature("docstring") std::map::iterator "STL iterator class."

%feature("docstring") std::multimap::iterator "STL iterator class."

%feature("docstring") std::set::iterator "STL iterator class."

%feature("docstring") std::basic_string::iterator "STL iterator class."

%feature("docstring") std::vector::iterator "STL iterator class."

%feature("docstring") std::string::iterator "STL iterator class."

%feature("docstring") std::multiset::iterator "STL iterator class."

%feature("docstring") std::wstring::iterator "STL iterator class."

%feature("docstring") std::deque::iterator "STL iterator class."

%feature("docstring") std::list::iterator "STL iterator class."

%feature("docstring") std::length_error "STL class."

%feature("docstring") std::list "STL class."

%feature("docstring") std::logic_error "STL class."

%feature("docstring") std::map "STL class."

%feature("docstring") std::multimap "STL class."

%feature("docstring") std::multiset "STL class."

%feature("docstring") std::ofstream "STL class."

%feature("docstring") std::ostream "STL class."

%feature("docstring") std::ostringstream "STL class."

%feature("docstring") std::out_of_range "STL class."

%feature("docstring") std::overflow_error "STL class."

%feature("docstring") std::priority_queue "STL class."

%feature("docstring") std::queue "STL class."

%feature("docstring") std::range_error "STL class."

%feature("docstring") std::map::reverse_iterator "STL iterator class."

%feature("docstring") std::set::reverse_iterator "STL iterator class."

%feature("docstring") std::multimap::reverse_iterator "STL iterator class."

%feature("docstring") std::list::reverse_iterator "STL iterator class."

%feature("docstring") std::basic_string::reverse_iterator "STL iterator class."

%feature("docstring") std::wstring::reverse_iterator "STL iterator class."

%feature("docstring") std::deque::reverse_iterator "STL iterator class."

%feature("docstring") std::vector::reverse_iterator "STL iterator class."

%feature("docstring") std::multiset::reverse_iterator "STL iterator class."

%feature("docstring") std::string::reverse_iterator "STL iterator class."

%feature("docstring") std::runtime_error "STL class."

%feature("docstring") std::set "STL class."

%feature("docstring") std::stack "STL class."

%feature("docstring") std::string "STL class."

%feature("docstring") std::stringstream "STL class."

%feature("docstring") std::underflow_error "STL class."

%feature("docstring") std::valarray "STL class."

%feature("docstring") std::vector "STL class."

%feature("docstring") std::wfstream "STL class."

%feature("docstring") std::wifstream "STL class."

%feature("docstring") std::wios "STL class."

%feature("docstring") std::wistream "STL class."

%feature("docstring") std::wistringstream "STL class."

%feature("docstring") std::wofstream "STL class."

%feature("docstring") std::wostream "STL class."

%feature("docstring") std::wostringstream "STL class."

%feature("docstring") std::wstring "STL class."

%feature("docstring") std::wstringstream "STL class."