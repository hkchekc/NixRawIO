from NixRawIO import NixRawIO
import  numpy as np
import  collections


localfile = '/home/choi/PycharmProjects/Nixneo/neoraw.nix'


reader = NixRawIO(filename=localfile)
reader.__init__('neoraw.nix')
reader.parse_header()

r = reader.get_analogsignal_chunk(0,1,None,None,[9])
print(reader.raw_annotations['blocks'][0]['segments'][0]['signals'])
print(reader.source_name())
print(r)
print("====================================================")

r = reader.get_analogsignal_chunk(1,1,None,None,[1,2,3])
print(r)






