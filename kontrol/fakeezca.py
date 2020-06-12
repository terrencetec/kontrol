# Fake guardian module with dummy Ezca class for debugging on non-CDS machines
class Ezca():
    class Device():
        def __init__(self, prefix, delim=''):
            self._prefix=prefix
    def __init__(self, prefix, logger=None):
        self.dev = Ezca.Device(prefix, delim='')
        self.prefix=prefix
    def read(self, channel, **kw):
        """Read channel value."""
        print('Reading '+channel)
        value = 3.1415926 # dummy for now
        return value

    def write(self, channel, value):
        """Write value channel to channel."""
        print('Writing '+str(value)+' to '+channel)

    def switch(self, sfmname, *args):
        """Manipulate buttons in CDS Standard Filter Module (SFM)."""
        print('Switching '+sfmname+' '+args[0]+' '+args[1])

