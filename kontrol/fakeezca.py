# 2020/06/14 Wasn't successful in simulated virtual systems. Using a dummy\
    # random while using read() instead.
# 2020/06/13 Added fake_system compatibility for simulating virtual systems.
# Fake guardian module with dummy Ezca class for debugging on non-CDS machines
from random import gauss
from . import fake_system
class Ezca():
    class Device():
        def __init__(self, prefix, delim=''):
            self._prefix=prefix

    def __init__(self, prefix, system=None, use_fake_system=False, logger=None):
        if use_fake_system:
            if system == None:
                import sys
                sys.path.append('sample')
                from sample_system_def import system
                self.system = system
            else:
                self.system = system
        self.dev = Ezca.Device(prefix, delim='')
        self.prefix = prefix
        self.use_fake_system = use_fake_system

    def read(self, channel, **kw):
        """Read channel value."""
        print('Reading '+channel)
        if self.use_fake_system:
            _stage, _block, _dof, _prefix = channel.split('_')
            value = float(self.system[_stage][_block][_dof][_prefix][0])
            # value += gauss(0,self.system[stage][block][dof][prefix][1])
        else:
            value = 3.1415926 + gauss(mu=0, sigma=0.1)# dummy for now
        return value

    def write(self, channel, value):
        """Write value channel to channel."""
        if self.use_fake_system:
            _stage, _block, _dof, _prefix = channel.split('_')
            v0 = float(self.read(channel))
            self.system[_stage][_block][_dof][_prefix][0] = float(value)
            # print(self.read(channel))
            if channel in self.system['connections'].keys():
                for output in self.system['connections'][channel].keys():
                    coupling = float(self.system['connections'][channel][output])
                    # a, b, c, d = output.split('_')
                    # print('hi',self.read(channel))
                    self.write(str(output), self.read(str(output))+float((value-v0)*coupling))
                    # self.system[str(a)][str(b)][str(c)][str(d)][0]=float(self.system[str(a)][str(b)][str(c)][str(d)][0])+(value-v0)*coupling
                    # print(self.read(channel))
            # print(stage,block,dof,prefix, value)
            # print(self.read(stage+'_'+block+'_'+dof+'_'+prefix))
            # self.update()
        print('Writing '+str(value)+' to '+channel)

    def switch(self, sfmname, *args):
        """Manipulate buttons in CDS Standard Filter Module (SFM)."""
        print('Switching '+sfmname+' '+args[0]+' '+args[1])

    def update(self):
        for input in list(self.system['connections'].keys()):
            for output in list(self.system['connections'][input].keys()):
                stage, block, dof, prefix = output.split('_')
                self.system[stage][block][dof][prefix][0] = 1
                print(self.read(output))
        for input in list(self.system['connections'].keys()):
            for output in list(self.system['connections'][input].keys()):
                stage, block, dof, prefix = input.split('_')
                val = float(self.system[stage][block][dof][prefix][0])
                coupling = float(self.system['connections'][input][output])
                stage, block, dof, prefix = output.split('_')
                print(val*coupling, self.read(output))
                self.system[stage][block][dof][prefix][0] = self.system[stage][block][dof][prefix][0] + val*coupling
                # print(input, self.read(input), output, self.read(output))
