#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: BER AWGN Test CSS SD/HD vs OQPSK
# Author: Felix Wunsch
# Generated: Mon Nov 10 19:00:50 2014
##################################################

execfile("/home/wunsch/.grc_gnuradio/ieee802_15_4_css_phy_hd.py")
execfile("/home/wunsch/.grc_gnuradio/ieee802_15_4_css_phy_sd.py")
execfile("/home/wunsch/.grc_gnuradio/ieee802_15_4_oqpsk_phy_nosync.py")
from gnuradio import analog
from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from optparse import OptionParser
import foo
import ieee802_15_4
import numpy as np
import pmt
import time
import matplotlib.pyplot as plt

# configuration parameters
snr_vals = np.arange(-30.0,-5.0,1.0)
enable_vals = [0.0, 0.0, 0.0]
nbytes_per_frame = 127
min_err = 1e4
min_len = 1e5
msg_interval = 10 # ms
sleeptime = 1.0

class ber_awgn_comp_nogui(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "BER AWGN Test OQPSK")

        ##################################################
        # Variables
        ##################################################
        self.snr = snr = 0
        self.c = c = ieee802_15_4.css_phy(slow_rate=True, phy_packetsize_bytes=127)

        ##################################################
        # Blocks
        ##################################################
        self.ieee802_15_4_oqpsk_phy_nosync_0 = ieee802_15_4_oqpsk_phy_nosync(
            payload_len=c.phy_packetsize_bytes,
        )
        self.ieee802_15_4_make_pair_with_blob_0 = ieee802_15_4.make_pair_with_blob(np.random.randint(0,256,(c.phy_packetsize_bytes,)))
        self.foo_periodic_msg_source_0 = foo.periodic_msg_source(pmt.cons(pmt.PMT_NIL, pmt.string_to_symbol("trigger")), 1, 5, True, False)
        # self.msg_trigger = blocks.message_strobe(pmt.cons(pmt.intern("trigger"), pmt.intern("dummy")), 1000)
        self.comp_bits = ieee802_15_4.compare_blobs(packet_error_mode=False)
        self.blocks_add_xx_0_0 = blocks.add_vcc(1)
        self.analog_noise_source_x_0_0 = analog.noise_source_c(analog.GR_GAUSSIAN, 0.5*(10**(-snr/20)), 0)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_noise_source_x_0_0, 0), (self.blocks_add_xx_0_0, 1))
        self.connect((self.blocks_add_xx_0_0, 0), (self.ieee802_15_4_oqpsk_phy_nosync_0, 0))
        self.connect((self.ieee802_15_4_oqpsk_phy_nosync_0, 0), (self.blocks_add_xx_0_0, 0))

        ##################################################
        # Asynch Message Connections
        ##################################################
        self.msg_connect(self.ieee802_15_4_make_pair_with_blob_0, "out", self.ieee802_15_4_oqpsk_phy_nosync_0, "txin")
        self.msg_connect(self.foo_periodic_msg_source_0, "out", self.ieee802_15_4_make_pair_with_blob_0, "in")
        # self.msg_connect(self.msg_trigger, "strobe", self.ieee802_15_4_make_pair_with_blob_0, "in")
        self.msg_connect(self.ieee802_15_4_make_pair_with_blob_0, "out", self.comp_bits, "ref")
        self.msg_connect(self.ieee802_15_4_oqpsk_phy_nosync_0, "rxout", self.comp_bits, "test")
        self.msg_connect(self.ieee802_15_4_oqpsk_phy_nosync_0, "rxout", self.ieee802_15_4_make_pair_with_blob_0, "in")

    def get_snr(self):
        return self.snr

    def set_snr(self, snr):
        self.snr = snr
        self.analog_noise_source_x_0_0.set_amplitude(0.5*(10**(-snr/20)))

    def get_c(self):
        return self.c

    def set_c(self, c):
        self.c = c
        self.ieee802_15_4_oqpsk_phy_nosync_0.set_payload_len(self.c.phy_packetsize_bytes)

if __name__ == '__main__':
    parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
    (options, args) = parser.parse_args()
    if gr.enable_realtime_scheduling() != gr.RT_OK:
        print "Error: failed to enable realtime scheduling."

    if min_len <= 1e3:
        raise Exception("min_len too short")
    min_ram_usage_mb = 2.0*min_len/1024/1024
    print "Simulation needs at least", min_ram_usage_mb, "MB of RAM"
    if min_ram_usage_mb > 4000:
        print "Careful, simulation needs more than 4GB RAM!"
    print "Simulate from", min(snr_vals), "to", max(snr_vals), "dB SNR"
    print "Collect",min_len,"bytes per step"
    ber_vals = [];
    for i in range(len(snr_vals)):
        t0 = time.time()
        tb = None
        tb = ber_awgn_comp_nogui()
        tb.set_snr(snr_vals[i])
        tb.start()
        while(True):
            len_res = tb.comp_bits.get_bits_compared()
            print snr_vals[i], "dB:", 100.0*len_res/min_len, "% done"
            time.sleep(sleeptime)
            if(len_res >= min_len):
                if tb.comp_bits.get_errors_found() >= min_err or tb.comp_bits.get_bits_compared() > min_len*50:
                    tb.stop()
                    tb.wait()
                    break

        ber = tb.comp_bits.get_ber()
        print "BER at", snr_vals[i], "dB SNR: ", ber
        ber_vals.append(ber)
        t_elapsed = time.time() - t0
        print "approximately",t_elapsed*(len(snr_vals)-len(ber_vals))/60, "minutes remaining"

    np.save("ber_awgn_oqpsk_"+str(min(snr_vals))+"_to_"+str(max(snr_vals))+"dB_"+time.strftime("%Y-%m-%d_%H-%M-%S"), ber_vals)
    plt.plot(snr_vals, ber_vals)
    plt.yscale('log')
    plt.title("ber_awgn_oqpsk_"+str(min(snr_vals))+"_to_"+str(max(snr_vals))+"dB_"+time.strftime("%Y-%m-%d_%H-%M-%S"))
    plt.savefig("ber_awgn_oqpsk_"+str(min(snr_vals))+"_to_"+str(max(snr_vals))+"dB_"+time.strftime("%Y-%m-%d_%H-%M-%S")+".pdf")
    plt.show()


