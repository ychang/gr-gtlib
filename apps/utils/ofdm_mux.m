ndata = 1000000;

data = read_complex_binary('../OFDM/mux.dat',ndata);
normalized = read_float_binary('../OFDM/ofdm_sync_pn-theta_f.dat',ndata);
nominator = read_float_binary('../OFDM/ofdm_sync_pn-nominator_f.dat',ndata); 
denominator = read_float_binary('../OFDM/ofdm_sync_pn-denominator_f.dat',ndata);  

figure(1);
subplot(4,1,1);
plot(real(data),'b');
hold on;
plot(imag(data),'r');
subplot(4,1,2);
plot(nominator,'b');
hold on;
plot(denominator,'r');
subplot(4,1,3);
plot(normalized);
