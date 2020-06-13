class FakeSystem():
    def __init__(self, system=None):
        if system == None:
            import sys
            sys.path.append('sample')
            from sample_system_def import system
            self.system = system
        else:
            self.system = system

    def update(self):
        for input in list(self.system['connections'].keys()):
            for output in list(self.system['connections'][input].keys()):
                stage, block, dof, prefix = input.split('_')
                val = self.system[stage][block][dof][prefix][0]
                coupling = self.system['connections'][input][output]
                stage, block, dof, prefix = output.split('_')
                self.system[stage][block][dof][prefix][0] = val*coupling
                print(input, output, coupling)
