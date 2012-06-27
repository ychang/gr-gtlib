ndata = 1000000;

data = read_complex_binary('../OFDM/mux.dat',ndata);

figure(1);
plot(real(data),'b');
hold on;
plot(imag(data),'r');
