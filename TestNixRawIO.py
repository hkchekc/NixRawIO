from NixRawIO import NixRawIO
import  numpy as np
import  collections


localfile = '/home/choi/PycharmProjects/Nixneo/neoraw.nix'


reader = NixRawIO(filename=localfile)
reader.__init__('neoraw.nix')
reader.parse_header()

r = reader.get_analogsignal_chunk(0,0,None,None,[0])
print(r)
print("====================================================")
r = reader.get_analogsignal_chunk(0,1,None,None,[8])
print(r)






