from nixrawio import NIXRawIO
import  numpy as np
import  collections
import nixio as nix
import quantities as pq


x = np.arange(0,10,1)
print(x, 'x')
print(x.shape)
rl = [12,13,13,15]
x =[v for i,v in enumerate(rl) if i%2==0]
print(x)


localfile = '/home/choi/PycharmProjects/Nixneo/test_case.nix'
file = nix.File.open('test_case.nix', 'a')

reader = NIXRawIO(filename=localfile)
print(reader)
reader.parse_header()
r = reader.get_analogsignal_chunk(0,0,None,None, [0])
print(r)
print(reader.header['event_channels'][1]['type'])
print(reader.event_channels_count())
# print("====================================================")
r = reader.get_spike_raw_waveforms(1,0,0,None, None)
print(r.shape)

