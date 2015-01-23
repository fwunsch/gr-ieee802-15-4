aMacMaxBeaconOrder = 14
aMacMaxSuperframeOrder = aMacMaxBeaconOrder
aBaseSuperframeDuration = 60*16
aMacLIFSPeriod = 40
aMacSIFSPeriod = 12
aMacMaxSIFSFrameSize = 18 # in bytes, refers to the MPDU (MAC frame)
t_ACK = aMacSIFSPeriod # this is still in symbols
aPhyMaxNumBytesPayload = 127
aMacMinNumBytesBeaconFrame = 13 # 2+1+4+0+2+1+1+0+2
aMacNumBytesAckFrame = 5
aMacMinNumBytesDataFrameOverhead = 7 # 2+1+2+0+2
aMacMaxNumDataBytesPayload = aPhyMaxNumBytesPayload - aMacMinNumBytesDataFrameOverhead
aPhyNumBitsPHR = 7
aMacMaxBytesPayload = aPhyMaxNumBytesPayload - aMacMinNumBytesDataFrameOverhead
vPhySHRDuration = [6.0, 6.0, 12.0]
vPhySymbolsPerOctet = [2.0, 1.3, 5.3]
vPhySymbolDurationSec = [16e-6, 6e-6, 6e-6]
PHY_OQPSK = 0
PHY_CSS1M = 1
PHY_CSS250k = 2
vPhyModeDict = {"OQPSK": PHY_OQPSK, "CSS1M": PHY_CSS1M, "CSS250k": PHY_CSS250k}
NB0 = 0 # start value for number of backoffs
CW0 = 2 # start value for contention window length
aMacMinBE = 3 # default value in the standard
aMacMaxBE = 5 # default value in the standard
aMacMaxCSMABackoffs = 4 # default value in the standard
aUnitBackoffPeriod = 20 # number of symbols per backoff period
aTurnaroundTime = 12
vPhySHRDuration = [6.0, 6.0, 12.0]
vPhySymbolsPerOctet = [2.0, 1.3, 5.3]
vPhySymbolDurationSec = [16e-6, 6e-6, 6e-6]
vPhyDataRate = [250e3, 1e6, 250e3] # this treats every information (incl. SHR & PHR) as data!
aMacAvgCSMABackoff = 3.5 * aUnitBackoffPeriod # E[uniformdistribution(0...2**3)] = (7+1)/2 = 3.5