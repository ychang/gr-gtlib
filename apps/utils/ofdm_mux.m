close all;

ndata = 100000000;

tx_mapper = read_complex_binary('../OFDM/ofdm_mapper_c.dat',ndata);
tx_ifft = read_complex_binary('../OFDM/ofdm_ifft_c.dat',ndata);
tx_cp_adder = read_complex_binary('../OFDM/ofdm_cp_adder_c.dat',ndata);

data = read_complex_binary('../OFDM/mux.dat',ndata);

normalized = read_float_binary('../OFDM/ofdm_sync_pn-theta_f.dat',ndata);
nominator = read_float_binary('../OFDM/ofdm_sync_pn-nominator_f.dat',ndata); 
denominator = read_float_binary('../OFDM/ofdm_sync_pn-denominator_f.dat',ndata);  

figure(1);

subplot(4,1,1);
plot(real(tx_mapper),'b');
hold on;
plot(imag(tx_mapper),'r');

subplot(4,1,2);
plot(real(tx_ifft),'b');
hold on;
plot(imag(tx_ifft),'r');

subplot(4,1,3);
plot(real(tx_cp_adder),'b');
hold on;
plot(imag(tx_cp_adder),'r');

figure(2);

subplot(3,1,1);
plot(real(data),'b');
hold on;
plot(imag(data),'r');
subplot(3,1,2);
plot(nominator,'b');
hold on;
plot(denominator,'r');
subplot(3,1,3);
plot(normalized);


ofdm_sub_carrier =[156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198,199,200,201,202,203,204,205,206,207,208,209,210,211,212,213,214,215,216,217,218,219,220,221,222,223,224,225,226,227,228,229,230,231,232,233,234,235,236,237,238,239,240,241,242,243,244,245,246,247,248,249,250,251,252,253,254,257,258,259,260,261,262,263,264,265,266,267,268,269,270,271,272,273,274,275,276,277,278,279,280,281,282,283,284,285,286,287,288,289,290,291,292,293,294,295,296,297,298,299,300,301,302,303,304,305,306,307,308,309,310,311,312,313,314,315,316,317,318,319,320,321,322,323,324,325,326,327,328,329,330,331,332,333,334,335,336,337,338,339,340,341,342,343,344,345,346,347,348,349,350,351,352,353,354,355];

figure(3);
stem(ofdm_sub_carrier,ones(1,length(ofdm_sub_carrier)));

