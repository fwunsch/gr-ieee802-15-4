import css_constants
import numpy as np

class physical_layer:
	def __init__(self, slow_rate=False, phy_packetsize_bytes=18, nframes=1, chirp_number=1):
		self.slow_rate = True
		self.phy_packetsize_bytes = phy_packetsize_bytes if phy_packetsize_bytes <= css_constants.max_phy_packetsize_bytes else css_constants.max_phy_packetsize_bytes
		if self.phy_packetsize_bytes % 6 != 0: # in order to match all periodicites the standard imposes the number of payload bytes has to be a multiple of 6
			self.phy_packetsize_bytes = self.phy_packetsize_bytes - (self.phy_packetsize_bytes % 6)
			print "changed packet size to", self.phy_packetsize_bytes
		self.nframes = nframes
		self.chirp_number = chirp_number
		self.bits_per_symbol = 6 if self.slow_rate == True else 3
		self.codewords = css_constants.codewords_250kbps if self.slow_rate == True else css_constants.codewords_1mbps
		self.intlv_seq = css_constants.intlv_seq if self.slow_rate == True else []
		self.preamble = css_constants.preamble_250kbps if self.slow_rate == True else css_constants.preamble_1mbps
		self.SFD = css_constants.SFD_250kbps if self.slow_rate == True else css_constants.SFD_1mbpsg
		self.PHR = self.gen_PHR()
		self.rcfilt = self.gen_rcfilt()
		self.possible_chirp_sequences = self.gen_chirp_sequences()
		if self.chirp_number < 1 or self.chirp_number > 4:
			print "Invalid chirp sequence number, must be [1..4]. Use chirp 1"
			self.chirp_number = 1
		self.chirp_seq = self.possible_chirp_sequences[self.chirp_number-1]
		self.n_tau = css_constants.n_tau[self.chirp_number-1]

	def gen_rcfilt(self):
		alpha = 0.25
		rcfilt = np.ones((css_constants.n_sub,))
		start_slope = round((1-alpha)/(1+alpha)*css_constants.n_sub/2)
		rcfilt[len(rcfilt)/2+start_slope:] = [0.5*(1+np.cos((1+alpha)*np.pi/(alpha*css_constants.n_sub)*i)) for i in range(int(css_constants.n_sub/2-start_slope))]
		rcfilt[0:len(rcfilt)/2-start_slope] = rcfilt[-1:len(rcfilt)/2+start_slope-1:-1]
		return rcfilt

	def gen_chirp_sequences(self):
		# first, generate subchirps
		subchirp_low_up = np.array([np.exp(1j*(2*np.pi*css_constants.fc_low + css_constants.mu/2*i/css_constants.bb_samp_rate)*i/css_constants.bb_samp_rate)*self.rcfilt[i] for i in range(css_constants.n_sub)])
		subchirp_low_down = np.array([np.exp(1j*(2*np.pi*css_constants.fc_low - css_constants.mu/2*i/css_constants.bb_samp_rate)*i/css_constants.bb_samp_rate)*self.rcfilt[i] for i in range(css_constants.n_sub)])
		subchirp_high_up = np.array([np.exp(1j*(2*np.pi*css_constants.fc_high + css_constants.mu/2*i/css_constants.bb_samp_rate)*i/css_constants.bb_samp_rate)*self.rcfilt[i] for i in range(css_constants.n_sub)])
		subchirp_high_down = np.array([np.exp(1j*(2*np.pi*css_constants.fc_high - css_constants.mu/2*i/css_constants.bb_samp_rate)*i/css_constants.bb_samp_rate)*self.rcfilt[i] for i in range(css_constants.n_sub)])

		# put together the chirp sequences (without DQPSK symbols)
		chirp_seq_I = np.concatenate((subchirp_low_up, subchirp_high_up, subchirp_high_down, subchirp_low_down))
		chirp_seq_II = np.concatenate((subchirp_high_up, subchirp_low_down, subchirp_low_up, subchirp_high_down))
		chirp_seq_III = np.concatenate((subchirp_low_down, subchirp_high_down, subchirp_high_up, subchirp_low_up))
		chirp_seq_IV = np.concatenate((subchirp_high_down, subchirp_low_up, subchirp_low_down, subchirp_high_up))

		return [chirp_seq_I, chirp_seq_II, chirp_seq_III, chirp_seq_IV]

	def gen_PHR(self):
		PHR = np.zeros((12,))
		payl_len_bitstring = '{0:07b}'.format(self.phy_packetsize_bytes)
		payl_len_list = [int(payl_len_bitstring[i],2) for i in range(0,len(payl_len_bitstring))]
		PHR[0:7] = payl_len_list
		return PHR	