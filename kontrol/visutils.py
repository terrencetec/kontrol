import os
import numpy as np
try:
    import ezca
except:
    print('Cannot find ezca, importing local fakeezca as ezca.')
    import fakeezca as ezca
import time
from utils import rms
default_force = 1000  # default inject in counts.

class Vis:
    """
    """
    def __init__(self, NAME, IFO=None):
        """
        Args:
            VIS: string
                The VIS suspension name. E.g. "BS" or "ITMY". This will be used
                to create ezca prefix, etc.
            IFO: string
                The interferometer prefix. E.g. "K1".
        """
        self.NAME = NAME
        if IFO == None:
            self.IFO = os.getenv('IFO', 'K1')
        else:
            self.IFO = IFO
        self.ezcaObj = ezca.Ezca(self.IFO+':VIS-'+self.NAME)

    def read_matrix(self, STAGE, matrix, i, j):
        """
        """
        matrix_prefix = STAGE + '_' + matrix
        return(self.ezcaObj.read(matrix_prefix+'_%d_%d'%(i,j)))

    def calming(self, channels, rms_thresholds, t_int=5):
        """
        """
        readout = [[]]*len(channels)
        t0 = time.time()
        while 1:
            for i in range(len(channels)):
                val = self.ezcaObj.read(channels[i])
                if val!=readout[i][-1]:
                    readout[i] += readout[i]+[val]
                print(readout[i])
            if time.time()-t0 >= t_int:
                flag = True
                for i in range(len(channels)):
                    print(channels[i],':', rms(readout[i]))
                    flag*=rms(readout[i])<=rms_thresholds[i]
                    print(flag)
                if flag:
                    break
                else:
                    t0 = time.time()
                    readout = [[]]*len(channels)

    def actuator_diag(self, STAGE, DOFs, act_block='TEST', act_suffix='OFFSET',
                      sense_block='DAMP', sense_suffix='INMON',
                      matrix='EUL2COIL', force=[], no_of_coils=None):
        """
        """
        if matrix == 'EUL2COIL':
            try:
                self.ezcaObj.read(STAGE+'_'+matrix+'_1_1')
            except:
                try:
                    matrix='EUL2OSEM'
                    self.ezcaObj.read(STAGE+'_'+matrix+'_1_1')
                except:
                    print('Actuation matrix is neither EUL2COIL nor EUL2OSEM, '\
                          'returning')
                    return(None)

        matrix_prefix = STAGE + '_' + matrix
        _read_matrix = lambda i, j: self.read_matrix(STAGE, matrix, i, j)

        if no_of_coils == None:
            print('no_of_coils not specified, trying to guess from matrix')
            no_of_coils = 1
            while 1:
                try:
                    _read_matrix(no_of_coils+1, 1)
                    no_of_coils += 1
                except:
                    # no_of_coils -= 1
                    break
                if no_of_coils >= 6:  ## FIXME: Think of a better way.
                    print('no_of_coils greater or equals to 6. Specify '\
                          'no_of_coils to bypass this.')
                    break

        original_matrix = np.zeros((no_of_coils, len(DOFs)))  # Here we assume\
            # that the number of rows is the number of coils and columns are\
            # numbers of DOFs.
        original_matrix = np.matrix(original_matrix)
        for i in range(no_of_coils):
            for j in range(len(DOFs)):
                original_matrix[i, j] = _read_matrix(i+1, j+1)
        print('Current '+matrix+'\n', original_matrix)

        if force == []:
            print('force not specified, defaulting to %d cnts '\
                  'for all degrees of freedom.'%(default_force))
            force = [default_force]*len(DOFs)
        elif len(force) != len(DOFs):
            print('len(force):%d not equal to len(DOFs):'\
                  '%d.'%(len(force),len(DOFs)))
            if len(force) == 1:
                print('Assume force = %d cnts for all DOFs'%force[0])
                force=[force[0]]*len(DOFs)
            else:
                print('Replacing unspecified force with default %d cnts'\
                      %(default_force))
                for _ in range(len(DOFs)-len(force)):
                    force += [default_force]
        print('Actuating in '+STAGE+'_'+act_block+'_', DOFs, '_'+act_suffix,
              'with force', force,' cnts')

        act_channel = lambda DOF: STAGE+'_'+act_block+'_'+DOF+'_'+act_suffix
        sense_channel = lambda DOF: (STAGE+'_'+sense_block+'_'+DOF+'_'+
                                    sense_suffix)
        x0 = np.zeros_like(DOFs)
        for i in range(len(DOFs)):
            x0[i] = self.ezcaObj.read(sense_channel(DOFs[i]))
