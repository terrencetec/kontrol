# 2020/06/14 Wasn't successful in simulated virtual systems. Using a dummy\
    # random while using read() instead.
# 2020/06/13 Added fake_system compatibility for simulating virtual systems.
# 2020/06/12 Added random Gaussian noise to the readout.
# Fake guardian module with dummy Ezca class for debugging on non-CDS machines
""" Fake guardian module with dummy Ezca class for debugging on non-CDS \
machines
"""
from random import gauss

class Ezca():
    class Device():
        def __init__(self, prefix, delim=''):
            self._prefix=prefix

    def __init__(self, prefix, logger=None):
        self.dev = Ezca.Device(prefix, delim='')
        self.prefix = prefix

    def read(self, channel, **kw):
        """Read channel value."""
        print('Reading '+channel)
        value = 3.1415926 + gauss(mu=0, sigma=0.1)# dummy for now
        return value

    def write(self, channel, value):
        """Write value channel to channel."""
        print('Writing '+str(value)+' to '+channel)

    def switch(self, sfmname, *args):
        """Manipulate buttons in CDS Standard Filter Module (SFM)."""
        print('Switching '+sfmname+' '+args[0]+' '+args[1])
