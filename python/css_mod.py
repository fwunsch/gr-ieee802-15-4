import css_constants
import css_phy
import numpy as np
import matplotlib.pyplot as plt

class modulator(css_phy.physical_layer):
	def modulate_random(self):
		payload_total = np.zeros((0,));
		complex_baseband_total = np.zeros((0,))

		for n in range(self.nframes):
			print "process frame", n+1, "/", self.nframes

			#print "- create random payload data and PHR"	
			payload = np.random.randint(0,2,size=(self.nframes*self.phy_packetsize_bytes*8,))
			payload_total = np.concatenate((payload_total, payload))
			payload = np.concatenate((self.PHR, payload)) # append payload to PHR

			#print "- divide payload up into I and Q stream"
			[payload_I, payload_Q] = self.demux(payload)

			#print "- map bits to codewords"
			payl_sym_I = self.bits_to_codewords(payload_I)
			payl_sym_Q = self.bits_to_codewords(payload_Q)
		
			if self.slow_rate == True:
				#print "- interleave codewords if in 250 kbps mode"
				payl_sym_I = self.interleaver(payl_sym_I)
				payl_sym_Q = self.interleaver(payl_sym_Q)

			#print "- create frame structure"
			frame_sym_I = self.create_frame(payl_sym_I)
			frame_sym_Q = self.create_frame(payl_sym_Q)

			#print "- modulate DQPSK symbols"
			frame_QPSK = self.mod_QPSK(frame_sym_I, frame_sym_Q)
			frame_DQPSK = self.mod_DQPSK(frame_QPSK)

			#print "- modulate DQCSK symbols"
			frame_DQCSK = self.mod_DQCSK(frame_DQPSK)
			complex_baseband_total = np.concatenate((complex_baseband_total,frame_DQCSK)) 	


		return [payload_total, complex_baseband_total]

	def modulate(payload):
		print "not implemented yet, shall be used to pipe in special payload"


	def demux(self, in_stream):
		return [in_stream[0::2], in_stream[1::2]]

	def bits_to_codewords(self, in_bits):
		in_bits = in_bits.reshape((len(in_bits)/self.bits_per_symbol), self.bits_per_symbol)
		idx = in_bits.dot(1 << np.arange(in_bits.shape[-1] - 1, -1, -1))
		len_cw = len(self.codewords[0])
		cw_serialized = np.array([self.codewords[int(i)] for i in idx])
		cw_serialized = cw_serialized.reshape((len(cw_serialized.flat),))
		return cw_serialized

	def interleaver(self, in_stream):
		return np.array([in_stream[i] for i in self.intlv_seq])

	def create_frame(self, PHR_PPSDU):
		return np.concatenate((self.preamble, self.SFD, PHR_PPSDU))

	def mod_QPSK(self, in_I, in_Q):
		sym_out = []
		QPSK_symbols = [1+0j, 0+1j, 0-1j, -1+0j]
		for i in range(len(in_I)):
			if (in_I[i], in_Q[i]) == (1,1):	
				sym_out.append(QPSK_symbols[0])
			elif (in_I[i], in_Q[i]) == (-1,1):
				sym_out.append(QPSK_symbols[1])
			elif (in_I[i], in_Q[i]) == (1,-1):
				sym_out.append(QPSK_symbols[2])
			elif (in_I[i], in_Q[i]) == (-1,-1):
				sym_out.append(QPSK_symbols[3])
			else:
				print "ERROR in mod_QPSK: Invalid input sequence"
		return sym_out

	def mod_DQPSK(self, in_QPSK):
		# a distance of 4 symbols is used to calculate the phase difference
		# the delay chain is initialized with exp(1j*pi/4)
		delay_chain = np.array([np.exp(1j*np.pi/4) for i in range(4)])
		sym_out = []
		for i in range(len(in_QPSK)):
			sym_out.append(in_QPSK[i]*delay_chain[3])
			delay_chain[1::] = delay_chain[0::-1]
			delay_chain[0] = sym_out[i]
		return sym_out

	def mod_DQCSK(self, in_DQPSK):
		if len(in_DQPSK) % 4 != 0:
			print "Number of DQCSK input symbols must be a multiple of 4. Drop tailing symbols"
			in_DQPSK = in_DQPSK[:-len(in_DQPSK)%4]
		
		n_seq = len(in_DQPSK)/4
		cplx_bb = np.zeros((0,), dtype=np.complex64)
		
		time_gap_1 = np.zeros((css_constants.n_chirp - 2*self.n_tau - 4*css_constants.n_sub,),dtype=np.complex64)
		time_gap_2 = np.zeros((css_constants.n_chirp + 2*self.n_tau - 4*css_constants.n_sub,),dtype=np.complex64)
		for i in range(n_seq):
			tmp = self.chirp_seq
			for k in range(4):
				tmp[k*css_constants.n_sub:(k+1)*css_constants.n_sub] *= in_DQPSK[i*4+k]
			cplx_bb = np.concatenate((cplx_bb, tmp))
			if i%2 == 0:
				cplx_bb = np.concatenate((cplx_bb, time_gap_1))
			else:
				cplx_bb = np.concatenate((cplx_bb, time_gap_2))
		return cplx_bb







