import nixio as nix
import numpy as np
import unittest
from nixio_fr import NixIOfr
import quantities as pq
from neo import NixIO


class TestNixfr(unittest.TestCase):

    def setUp(self):
        self.testfilename = "test_case.nix"
        self.file = nix.File.open(self.testfilename)
        self.reader_fr = NixIOfr(filename=self.testfilename)
        self.reader_norm = NixIO(filename=self.testfilename, mode='ro')
        self.blk = self.reader_fr.read_block(block_index=1, load_waveforms=True)  # read block in NixIOfr
        self.blk1 = self.reader_norm.read_block(index=1)  # read block NIXio
        # self.blk = self.reader.read_block(0, load_waveforms = True)

    def tearDown(self):
        self.file.close()
        self.reader_fr.file.close()
        self.reader_norm.close()

    def test_check_same_neo_structure(self):
        self.assertEqual(len(self.blk.segments), len(self.blk1.segments))
        # self.assertEqual(len(self.blk.channel_indexes), len(self.blk1.channel_indexes))
        for seg1, seg2 in zip(self.blk.segments, self.blk1.segments):
            self.assertEqual(len(seg1.analogsignals), len(seg2.analogsignals))
            self.assertEqual(len(seg1.spiketrains), len(seg2.spiketrains))

        # for chid1, chid2 in zip(self.blk.channel_indexes, self.blk1.channel_indexes):
        #     self.assertEqual(len(chid1.units), len(chid2.units))
        #     self.assertEqual(len(chid1.analogsignals), len(chid2.analogsignals))
        #     for unit1, unit2 in zip(chid1.units, chid2.units):
        #         self.assertEqual(len(unit1.spiketrains), len(unit2.spiketrains))

    def test_check_same_data_content(self):
        for seg1, seg2 in zip(self.blk.segments, self.blk1.segments):
            for asig1, asig2 in zip(seg1.analogsignals, seg2.analogsignals):
                np.testing.assert_almost_equal(asig1.magnitude, asig2.magnitude)  # not completely equal
            for st1, st2 in zip(seg1.spiketrains, seg2.spiketrains):
                np.testing.assert_array_equal(st1.magnitude, st2.times)

        # for chid1, chid2 in zip(self.blk.channel_indexes, self.blk1.channel_indexes):
        #     for asig1, asig2 in zip(chid1.analogsignals, chid2.analogsignals):
        #         np.testing.assert_array_equal(asig1.magnitude, asig2.magnitude)

    def test_analog_signal(self):
        seg1 = self.blk.segments[0]
        an_sig1 = seg1.analogsignals[0]
        assert len(an_sig1) == 30

        an_sig2 = seg1.analogsignals[1]
        list_c = an_sig2.tolist()
        assert an_sig2.shape == (50,3)

        an_sig3 = self.blk.segments[1].analogsignals[1]
        list_a = an_sig3.tolist()
        an_sig4 = self.blk1.segments[1].analogsignals[1]
        list_b = an_sig4.tolist()

    def test_spiketrain(self):
        st1 = self.blk.segments[0].spiketrains[0]
        assert np.all(st1.times == np.cumsum(np.arange(0,1,0.1)).tolist() * pq.s + 10 *pq.s)

    def test_event(self):
        seg1 = self.blk.segments[0]
        event1 = seg1.events[0]
        raw_time = 10 + np.cumsum(np.array([0,1,2,3,4]))
        assert np.all(event1.times == np.array(raw_time *pq.s / 1000))
        assert np.all(event1.labels == np.array([b'A', b'B', b'C', b'D', b'E']))
        assert len(seg1.events) == 1

    def test_epoch(self):
        seg1 = self.blk.segments[1]
        epoch1 = seg1.epochs[0]

    def test_waveform(self):
        pass


# localfile = '/home/choi/PycharmProjects/Nixneo/neoraw.nix'
#
# reader = NixIOfr(filename=localfile)
#
# blk = reader.read_block(0, load_waveforms= False)
#
# blk1 = reader.read_block(1, load_waveforms= False)
# print(blk)
# print(blk1)
# print('//////////////////////////////////////////////////')
# print(blk.segments)
# for asig in blk1.segments[0].analogsignals:
#     print("asigname with block 2", asig.name)
#     print(asig.shape)
#     print(asig)
#
# for seg in blk.segments:
#     for st in seg.spiketrains:
#         print(st)
#
# print('------------------------------------------------')
# print(blk.channel_indexes)
# for chx in blk.channel_indexes:
#      print(chx.name, 'name')
#      print(chx.channel_ids, 'id')
#      print(chx.channel_names, 'chan_name')
#      print("index: {}:".format(chx.index))
# #
#      print(chx.units)
#      for i, u in enumerate(chx.units):
#          print(u.name)
#          print(u.spiketrains)
#          print(u.spiketrains[0].times)
#          print(u.spiketrains[0].t_start)
#          print(u.spiketrains[0].t_stop)
#          print(u.spiketrains[0].waveforms)
#
# print(blk.segments[0].events)
# print(blk.segments[0].events[0].labels)
# print(blk.segments[0].events[0].times)
# print('------------------------------------------------')
# print(blk.segments[0].epochs[0].name)
# print(blk.segments[0].epochs[0].durations)
# print(blk.segments[0].epochs[0].times)
# print(blk.segments[0].epochs[0].labels)
# print(blk.segments[0].spiketrains)

if __name__ == '__main__':
    unittest.main()
