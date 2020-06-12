import os
import numpy as np
try:
    import ezca
except:
    print('Cannot find ezca, importing local fakeezca as ezca.')
    import fakeezca as ezca

class visutils:
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
        read_matrix = lambda i, j: self.ezcaObj[matrix_prefix+'_%d_%d'%(i,j)]

        if no_of_coils == None:
            print('no_of_coils not specified, trying to guess from matrix')
        no_of_coils = 1
        while 1:
            try:
                read_matrix(no_of_coils, 1)
                no_of_coils += 1
            except:
                break
            if no_of_coils >= 10:
                print('no_of_coils greater or equals to 10. Assume fakeezca is'\
                      ' used.')
                break

        original_matrix = np.zeros((no_of_coils, len(DOFs)))
        original_matrix = np.matrix(original_matrix)
        for i in range(no_of_coils):
            for j in range(len(DOFs)):
                original_matrix[i, j] = read_matrix(i+1, j+1)
        print(original_matrix)
