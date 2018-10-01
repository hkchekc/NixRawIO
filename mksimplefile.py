from neo import (Block, Segment,
                 AnalogSignal, IrregularlySampledSignal,
                 Event, Epoch, SpikeTrain,
                 ChannelIndex, Unit)
from neo.io.nixio import NixIO

import numpy as np
import quantities as pq



block1 = Block("nix-raw-block1", description="The 1st block")
block2 = Block("nix-raw-block2", description="The 2nd block")

for block in (block1, block2):
    ch_count = 0
    asig_count = 0
    nsegments = 1

    # Generate 3 fake data signals using numpy's random function
    # The shapes of the arrays are arbitrary
    data_a = np.random.random((300, 1)) # make the shape all the same, to make sure array generation is goodt
    nchannels = 1

    sampling_rate = pq.Quantity(1, "Hz")

    indexes = np.arange(nchannels)

    chx = ChannelIndex(name="channel-{}".format(0),
                       index=indexes,
                       channel_names=["S" + str(0) + chr(ord("a") + i) for i in indexes],
                       channel_ids=1 * 100 + indexes + 1)
    block.channel_indexes.append(chx)

    for idx in range(nsegments):
        seg = Segment("seg-ex{}".format(idx),
                      description="Segment number {}".format(idx))
        block.segments.append(seg)


        asig = AnalogSignal(name="Seg {} :: Data {}".format(idx, 0),
                            signal=data_a+1, units="V",
                            sampling_rate=sampling_rate, t_start=1* pq.s)
        print("Seg {} :: Data {}".format(idx, 0))
        seg.analogsignals.append(asig)
        # random sampling times for data_b

        # Event, Epoch, SpikeTrain
        tstart = 10 * pq.ms
        event_times = tstart + np.cumsum(np.random.random(5)) * pq.ms
        event = Event(name="Seg {} :: Event".format(idx),
                      times=event_times,
                      labels=["A", "B", "C", "D", "E"])
        seg.events.append(event)

        epoch_times = tstart + np.cumsum(np.random.random(3)) * pq.ms
        epoch = Epoch(name="Seg {} :: Epoch".format(idx),
                      times=epoch_times,
                      durations=np.random.random(4)*pq.ms,
                      labels=["A+", "B+", "C+"])
        seg.epochs.append(epoch)

        st_times = tstart + np.cumsum(np.random.random(10)) * pq.ms
        tstop = max(event_times[-1], epoch_times[-1], st_times[-1]) + 1 * pq.ms
        st = SpikeTrain(name="Seg {} :: SpikeTrain".format(idx),
                        times=st_times, t_start=tstart, t_stop=tstop)
        st.sampling_rate = sampling_rate

        seg.spiketrains.append(st)

        unit = Unit(name="unit-{}".format(idx))
        chx.units.append(unit)

# Write the Block to file using the NixIO
# Any existing file will be overwritten
fname = "test_case.nix"
io = NixIO(fname, "ow")
io.write_block(block1)
io.write_block(block2)
io.close()

print("Done. Saved to {}".format(fname))
