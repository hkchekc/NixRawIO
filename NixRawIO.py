from __future__ import print_function, division, absolute_import
from baserawio import (BaseRawIO, _signal_channel_dtype, _unit_channel_dtype, _event_channel_dtype)
import numpy as np
import nixio as nix


class NixRawIO (BaseRawIO):

    extensions = ['nix']
    rawmode = 'one-file'

    def __init__(self, filename=''):
        BaseRawIO.__init__(self)
        self.filename = filename
        print(filename)

    def _source_name(self):
        return self.filename

    def _parse_header(self):

        self.file = nix.File.open(self.filename, nix.FileMode.ReadOnly)
        channel_name = []
        for blk in self.file.blocks:
            for ch, src in enumerate(blk.sources):
                channel_name.append(src.name)
        sig_channels = []
        blk_sig_dict = {}  # for identifying sig in whihc blks, use in raw_ann later
        blsig_count = 0
        for i, bl in enumerate(self.file.blocks):
            sig_in_blk = []
            block_index = i
            for seg in bl.groups:
                for da in seg.data_arrays:
                    if da.type == "neo.analogsignal":
                        nixname = da.name
                        nixidx = int(nixname.split('.')[-1])
                        src = da.sources[0].sources[nixidx]
                        chan_id = src.metadata['channel_id']
                        ch_name = src.metadata['neo_name']
                        units = str(da.unit)
                        dtype = str(da.dtype)
                        sr = 1 / da.dimensions[0].sampling_interval
                        group_id = 0
                        for id, name in enumerate(channel_name):
                            if name == da.sources[0].name:
                                group_id = id # very important! group_id use to store channel groups!!!
                        gain = 1
                        offset = 0.
                        sig_channels.append((ch_name, chan_id, sr, dtype, units, gain, offset, group_id))
                        sig_in_blk.append(blsig_count)
                        blsig_count += 1
                blk_sig_dict[i] = sig_in_blk
                break
        sig_channels = np.array(sig_channels, dtype=_signal_channel_dtype)

        unit_channels = []
        unit_name = ""
        unit_id = ""
        for bl in self.file.blocks:
            for seg in bl.groups:
                for mt in seg.multi_tags:
                    if mt.type == "neo.spiketrain":
                        for usrc in mt.sources:
                            if usrc.type == "neo.unit":
                                unit_name = usrc.metadata['neo_name']
                                unit_id = usrc.id
                                pass
                        wf_units = mt.features[0].data.unit
                        wf_gain = 1
                        wf_offset = 0.
                        if "left_sweep" in mt.features[0].data.metadata:
                            wf_left_sweep = mt.features[0].data.metadata["left_sweep"]
                        else:
                            wf_left_sweep = 0
                        wf_sampling_rate = 1 / mt.features[0].data.dimensions[2].sampling_interval
                        unit_channels.append((unit_name, unit_id, wf_units, wf_gain,
                                              wf_offset, wf_left_sweep, wf_sampling_rate))
        unit_channels = np.array(unit_channels, dtype=_unit_channel_dtype)

        event_channels = []
        event_count = 0
        epoch_count = 0
        for bl in self.file.blocks:
            for mt in bl.multi_tags:
                if mt.type == "neo.event":
                    ev_name = mt.metadata['neo_name']
                    ev_id = event_count
                    event_count += 1
                    ev_type = "event"
                    event_channels.append((ev_name, ev_id, ev_type))
                if mt.type == "neo.epoch":
                    ep_name = mt.metadata['neo_name']
                    ep_id = epoch_count
                    epoch_count += 1
                    ep_type = "epoch"
                    event_channels.append((ep_name, ep_id, ep_type))
        event_channels = np.array(event_channels, dtype=_event_channel_dtype)

        self.header = {}
        self.header['nb_block'] = len(self.file.blocks)
        self.header['nb_segment'] = [len(bl.groups) for bl in self.file.blocks]
        # self.header['blocks'] = [{i:blocks} for i, blocks in enumerate(self.file.blocks)]
        #self.header['blocks'][i]['signal_channels'] = sig_channels[blk_sig_dict[i]]
        self.header['signal_channels'] = sig_channels
        self.header['unit_channels'] = unit_channels
        self.header['event_channels'] = event_channels

        self._generate_minimal_annotations()


        # for block_index in range(self.header['nb_block']):
        #     bl_ann = self.raw_annotations['blocks'][block_index]
        #     bl_ann['nb_siginblock'] = len(blk_sig_dict[block_index])
        #     bl_ann['signal_channels'] = sig_channels[blk_sig_dict[block_index]]


    def _segment_t_start(self, block_index, seg_index):
        t_start = 0
        for mt in self.file.blocks[block_index].groups[seg_index].multi_tags:
            if mt.type == "neo.spiketrain":
                t_start = mt.metadata['t_start']
        return t_start

    def _segment_t_stop(self, block_index, seg_index):
        t_stop = 0
        for mt in self.file.blocks[block_index].groups[seg_index].multi_tags:
            if mt.type == "neo.spiketrain":
                t_stop = mt.metadata['t_stop']
        return t_stop

    def _get_signal_size(self, block_index, seg_index, channel_indexes):
        size = 0
        if channel_indexes is None:
            channel_indexes = []
        ch_list = np.unique(self.header['signal_channels'][channel_indexes]['group_id'])
        for ch in ch_list:
            ch = int(ch)
            try:
                chan_name = self.file.blocks[block_index].sources[ch].name
            except KeyError:
                print("There is no channel index: {}".format(channel_indexes))
                continue
            for da in self.file.blocks[block_index].groups[seg_index].data_arrays:
                if da.type == 'neo.analogsignal' and da.sources[0].name == chan_name:
                    size = da.size
                    break
        return size

    def _get_signal_t_start(self, block_index, seg_index, channel_indexes):
        sig_t_start = 0
        if channel_indexes is None:
            channel_indexes = []
        ch_list = np.unique(self.header['signal_channels'][channel_indexes]['group_id'])
        for ch in ch_list:
            ch = int(ch)
            try:
                chan_name = self.file.blocks[block_index].sources[ch].name
            except KeyError:
                print("There is no channel index: {}".format(channel_indexes))
                continue
            for da in self.file.blocks[block_index].groups[seg_index].data_arrays:
                if da.type == 'neo.analogsignal' and da.sources[0].name == chan_name:
                    sig_t_start = float(da.metadata['t_start'])
                    break
        return sig_t_start

    def _get_analogsignal_chunk(self, block_index, seg_index, i_start, i_stop, channel_indexes):
        #print(block_index, seg_index, i_start, i_stop, channel_indexes)
        # ori_ch_index = channel_indexes
        # segment_id = self.file.blocks[block_index].groups[seg_index]
        # da_ref = []
        # da_count = 0
        # for bl in self.file.blocks:
        #     for seg in bl.groups:
        #         cur_seg = seg
        #         for da in seg.data_arrays:
        #             if da.type == 'neo.analogsignal':
        #                 da_ref.append((cur_seg,da, da_count))
        #                 da_count += 1
        # keep = [data[0]==segment_id for data in da_ref]
        # da_ref_real = [da_ref[i] for i in range(len(da_ref)) if keep[i]]
        #
        # ch_index = []
        # for i, da  in enumerate(da_ref_real):
        #     if da[2] in channel_indexes:
        #         ch_index.append(i)
        # channel_indexes = ch_index
        # # assert channel_indexes != [], "These indexes are not in the specified segment or block"

        if i_start is None:
            i_start = 0
        if i_stop is None:
            da_list = []
            for da in self.file.blocks[block_index].data_arrays:
                if da.type == 'neo.analogsignal':
                    da_list.append(da.size)
            for c in channel_indexes:
                i_stop = da_list[c]
                break

        chan_list = []
        for chan in self.file.blocks[block_index].sources:
            if chan.type == "neo.channelindex":
                chan_list.append(chan)
        if channel_indexes is None:
            nb_chan = []
            for i, data in enumerate(chan_list):
                nb_chan.append(i)
        else:
            keep =[]
            for ch in channel_indexes:
                keep.append(ch <= len(chan_list) - 1)
            nb_chan = [i for (i, v) in zip(channel_indexes, keep) if v]

        nb_chan = np.unique(self.header['signal_channels'][channel_indexes]['group_id'])

        same_group = []
        for idx, ch in enumerate(self.header['signal_channels']):
            if self.header['signal_channels'][idx]['group_id'] == nb_chan:
                same_group.append(idx)  # index start from 0
        id_in_group = []
        for x in channel_indexes:
            if x not in same_group:
                continue
            a = same_group.index(x)
            id_in_group.append(a)
        raw_signals_list = []
        for ch in nb_chan:
            ch = int(ch)
            try:
                chan_name = self.file.blocks[block_index].sources[ch].name
            except KeyError:
                print("There is no channel index: {}".format(channel_indexes))
                continue
        for i, da in enumerate(self.file.blocks[block_index].groups[seg_index].data_arrays):
            if i in channel_indexes:
                if da.type == 'neo.analogsignal' :
                    if da.sources[0].name == chan_name:
        #for ch in channel_indexes:
            #name = self.header['signal_channels'][ch]["name"]
            #for da in self.file.blocks[block_index].data_arrays:
                #for i in id_in_group:
                    #if i < len(da.sources) and da.sources[0].sources[i].metadata["neo_name"] == name:
                        raw_signals_list.append(da[i_start:i_stop])

        #raw_signals_list = [raw_signals_list[i] for i in id_in_group]
        raw_signals = np.array(raw_signals_list)
        raw_signals = np.transpose(raw_signals)
        if raw_signals.size == 0:
            raw_signals = np.zeros(shape=(5,5))
        return raw_signals

    def _spike_count(self, block_index, seg_index, unit_index):
        count = 0
        head_id = self.header['unit_channels'][unit_index][1]
        for mt in self.file.blocks[block_index].groups[seg_index].multi_tags:
            for src in mt.sources:
                if mt.type == 'neo.spiketrain' and [src.type == "neo.unit"]:
                    if head_id == src.id:
                        return len(mt.positions)
        return count

    def _get_spike_timestamps(self, block_index, seg_index, unit_index, t_start, t_stop):
        spike_timestamps = []
        head_id = self.header['unit_channels'][unit_index][1]  # not going to work unit_index can be list or array
        for mt in self.file.blocks[block_index].groups[seg_index].multi_tags:
            for src in mt.sources:
                if mt.type == 'neo.spiketrain' and [src.type == "neo.unit"]:
                    if head_id == src.id:
                        st_times = mt.positions
                        spike_timestamps = np.array(st_times)
                        break
        spike_timestamps = np.transpose(spike_timestamps)

        if t_start is not None or t_stop is not None:
            lim0 = t_start
            lim1 = t_stop
            mask = (spike_timestamps >= lim0) & (spike_timestamps <= lim1)
            spike_timestamps = spike_timestamps[mask]
        return spike_timestamps

    def _rescale_spike_timestamp(self, spike_timestamps, dtype):
        spike_times = spike_timestamps.astype(dtype)
        sr= self.header['signal_channels'][0][2]
        spike_times *= sr
        return spike_times

    def _get_spike_raw_waveforms(self, block_index, seg_index, unit_index, t_start, t_stop):
        # this must return a 3D numpy array (nb_spike, nb_channel, nb_sample)
        waveforms = []
        for mt in self.file.blocks[block_index].groups[seg_index].multi_tags:
            if mt.type == "neo.spiketrain":
                if mt.features[0].data.type == "neo.waveforms":
                    waveforms = mt.features[0].data
        raw_waveforms = np.array(waveforms)
        rs = raw_waveforms.shape
        # raw_waveforms = raw_waveforms.reshape(rs[1], rs[2], rs[3])

        if t_start is not None or t_stop is not None:
            lim0 = t_start
            lim1 = t_stop
            mask = (raw_waveforms >= lim0) & (raw_waveforms <= lim1)
            raw_waveforms = np.where(mask, raw_waveforms, np.nan)
        return raw_waveforms

    def _event_count(self, block_index, seg_index, event_channel_index):
        event_count = 0
        for event in self.file.blocks[block_index].groups[seg_index].multi_tags:
            if event.type == 'neo.event':
                event_count += 1
        return event_count

    def _get_event_timestamps(self, block_index, seg_index, event_channel_index, t_start, t_stop):
        seg_t_start = self._segment_t_start(block_index, seg_index)
        timestamp = []
        labels = []

        for mt in self.file.blocks[block_index].groups[seg_index].multi_tags:
            if mt.type == "neo.event":
                labels.append(mt.positions.dimensions[0].labels)
                po = mt.positions
                if po.type == "neo.event.times":
                    timestamp.append(po)
        timestamp = np.array(timestamp, dtype="float") + seg_t_start
        labels = np.array(labels, dtype='U')

        if t_start is not None:
            keep = timestamp >= t_start
            timestamp, labels = timestamp[keep], labels[keep]

        if t_stop is not None:
            keep = timestamp <= t_stop
            timestamp, labels = timestamp[keep], labels[keep]
        durations = None
        return timestamp, durations, labels

    def _rescale_event_timestamp(self, event_timestamps, dtype):
        event_times = event_timestamps.astype(dtype)  # supposing unit is second, other possibilies maybe mS microS...
        return event_times

    def _rescale_epoch_duration(self, raw_duration, dtype):
        durations = raw_duration.astype(dtype)  # supposing unit is second, other possibilies maybe mS microS...
        return durations


