from nixrawio import NIXRawIO
from neo.io.basefromrawio import BaseFromRaw


class NixIOfr(NIXRawIO, BaseFromRaw):

    name = 'NIX IO'

    _prefered_signal_group_mode = 'group-by-same-units'
    _prefered_units_group_mode = 'split-all'

    def __init__(self, filename):
        NIXRawIO.__init__(self, filename)
        BaseFromRaw.__init__(self, filename)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.header = None
        self.file.close()
