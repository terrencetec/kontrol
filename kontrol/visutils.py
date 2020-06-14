"""KAGRA VIS system utility functions.
"""
import os
import numpy as np
try:
    import ezca
except:
    print('Cannot find ezca, importing local fakeezca as ezca.')
    from . import fakeezca as ezca
import time
from .utils import rms
from .unsorted import nlms_update

default_force = 1000  # default inject in counts.

class Vis:
    """Utility functions for KAGRA VIS system. Declare with the name of the
    optic. E.g. visutils.Vis('BS').

    Methods:
        actuator_diag(self, STAGE, DOFs, act_block='TEST', act_suffix='OFFSET',
                          sense_block='DAMP', sense_suffix='INMON',
                          matrix='EUL2COIL', force=[], no_of_coils=None, t_ramp=10,
                          t_avg=10, dt=1/8):
        And others...
    """

    def __init__(self, name, ifo='K1'):
        """
        Args:
            name: string
                The VIS suspension name. E.g. "BS" or "ITMY". This will be used
                to create ezca prefix, etc.
            ifo: string
                The interferometer prefix. E.g. "K1".
        """
        self.name = name
        self.ifo = ifo
        self.ezcaObj = ezca.Ezca(self.ifo+':VIS-'+self.name)

    def read_matrix(self, STAGE, matrix, i, j):
        """Read a single entry from a real-time model matrix.
        """
        matrix_prefix = STAGE + '_' + matrix
        return(self.ezcaObj.read(matrix_prefix+'_%d_%d'%(i,j)))

    def calming(self, channels, rms_thresholds, t_int=5, dt=1):
        """A function that will loop untils the given channels has residual RMS
        lower than the given rms_thresholds.
        """
        readout = [[]]*len(channels)
        t0 = time.time()
        previous_val=0
        while 1:
            for i in range(len(channels)):
                val = self.ezcaObj.read(channels[i])
                readout[i] = readout[i]+[val]  # FIXME append() is faster than +
                # print(len(readout[i]))
                # previous_val=val
            if time.time()-t0 >= t_int:
                flag = True
                for i in range(len(channels)):
                    # print(channels[i],':', rms(readout[i]))
                    flag *= rms(readout[i])<=rms_thresholds[i]
                    # print(flag)
                if flag:
                    break
                else:
                    # t0 = time.time()
                    for i in range(len(readout)):
                        readout[i].pop(0)
            # print(time.time()-t0)
            time.sleep(dt)

    def read_avg(self, channels, t_avg=10, dt=1/8):
        """Return a time-averaged value given an ezca channel.

        Args:
            channels: list
                A list of channel names to be measured.
        Optional Args:
            t_avg: int/float
                The averaging time for measuring the displacement readouts.
            dt: int/float
                The sampling spacing while measuring the average readouts.

        Returns:
            x0: list
                a list of average values read from the specified channels.
        """
        x0s = [[]]*len(channels)
        print('Getting average readings for %.1f seconds'%t_avg)
        t0 = time.time()
        while (time.time()-t0 <= t_avg):
            for i in range(len(channels)):
                x0s[i] = x0s[i] + [self.ezcaObj.read(channels[i])]
            time.sleep(dt)
        x0 = [np.average(readouts) for readouts in x0s]
        return(x0)

    def actuator_diag(self, STAGE, DOFs, act_block='TEST', act_suffix='OFFSET',
                      sense_block='DAMP', sense_suffix='INMON',
                      matrix='EUL2COIL', force=[], no_of_coils=None, t_ramp=10,
                      t_avg=10, dt=1/8):
        """ !!! INTERACTS WITH REAL SYSTEMS, USE WITH CAUTION !!!
        Actuates a particular stage in its degrees of freedom to obtain the
        stage-wise diagonalizaion actuation matrix. For now, the injection is
        only DC. The default actuation channel is 'K1:...TEST_OFFSET' and the
        default sensor channel is 'K1:...DAMP_INMON'.
        IMPORTANT: Do specify the force even though it is an optional argument.
        This is to prevent the system to be violently perturbed.

        Args:
            STAGE: string
                The stage of interest in capatal letter. E.g. 'BS' or 'ITMX'
            DOFS: list
                A list of strings containing the degrees of freedom of the stage
                . e.g. ['L', 'T', 'Y']. The order must follow how the actuation
                matrix is arranged.

        Optional Args:
            act_block: string
                The name of the block in the real-time system that is used for
                the injection. Defaults to 'TEST' because it is usually used for
                such purpose.
            act_suffix: string
                The suffix of the channel name which we inject the actuation
                signal. Defaults to 'OFFSET'.
            sense_block: string
                The name of the block in the real-time system that is used to
                measure readout. Note that the readouts must be diagonalized
                beforehand in order for actuation diagonalization to work.
                Defaults to 'DAMP'
            sense_prefix: string
                The suffix of the readout channel name. Defaults to 'INMON'.
            matrix: string
                The name of the block containing the actuation diagonalization
                matrix entries. Defaults to 'EUL2COIL'. The script automatically
                checks if the stage uses EUL2COIL or EUL2OSEM automatically. If
                other matrices is of interest, specify explicitly.
            force: list
                The force in number of counts to put in the actuation channels.
                If not specified, the default no. of counts for all channels
                is 1000 counts. If only one number is specified, all DoFs will
                be actuated by that number. If more numbers are specified but
                less than the number of DoFs specified, then the rest will be
                set to default. Note that this number is relative to any
                additional offsets already present in the actuation channel.
                E.g. if the actuation has originally 10 counts and a force of
                10 counts is specified, the final number of counts will be 20.
            no_of_coils: int
                The number of actuators/coils of the stage. If not specified,
                the scipt will guess from the number of rows of the actuation
                matrix.
            t_ramp: int/float
                The ramp time in seconds for actuation. Defaults to 10.
            t_avg: int/float
                The averaging time for measuring the displacement readouts.
            dt: int/float
                The sampling spacing while measuring the average readouts.

        Returns
            new_matrix: numpy.matrixlib.defmatrix.matrix
                The final matrix to be entered to the actuation matrix.
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

        if no_of_coils is None:
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
        original_matrix = np.array(original_matrix)  # FIXME use np.array
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

        act_prefix = STAGE+'_'+act_block
        act_channel = lambda DOF: act_prefix+'_'+DOF+'_'+act_suffix
        sense_prefix = STAGE+'_'+sense_block
        sense_channel = lambda DOF: sense_prefix+'_'+DOF+'_'+sense_suffix

        # x0s = [[]]*len(DOFs)
        # x0 = []
        # print('Getting initial readings for %.1f seconds'%t_avg)
        # t0 = time.time()
        # while (time.time()-t0 <= t_avg):
        #     for i in range(len(DOFs)):
        #         x0s[i] = x0s[i] + [self.ezcaObj.read(sense_channel(DOFs[i]))]
        #     time.sleep(dt)
        sense_channels = [sense_channel(DOF) for DOF in DOFs]
        x0 = self.read_avg(sense_channels, t_avg)
        print(x0)

        for i in range(len(DOFs)):
            readout = self.ezcaObj.read(act_channel(DOFs[i]))
            readout *= self.ezcaObj.read(act_prefix+'_'+DOFs[i]+'GAIN')
            if abs(readout) < 1e-5:
                try:
                    self.ezcaObj.switch(act_prefix+'_'+DOFs[i],
                                        act_suffix, 'OFF')
                except:
                    pass

                self.ezcaObj.write(act_channel(DOFs[i]), 0)  # Clear out any\
                    # initial readings if there is any.
            self.ezcaObj.write(act_prefix+'_'+DOFs[i]+'GAIN', 1)
            self.ezcaObj.write(act_prefix+'_'+DOFs[i]+'TRAMP', t_ramp)
            try:
                self.ezcaObj.switch(act_prefix+'_'+DOFs[i], act_suffix, 'ON')
            except:
                pass

        force0 = [self.ezcaObj.read(act_channel(DOF)) for DOF in DOFs]

        coupling= [[]]*len(DOFs)
        for i in range(len(DOFs)):
            self.ezcaObj.write(act_channel(DOFs[i]), force[i]+force0[i])
            time.sleep(t_ramp)
            # while (self.ezcaObj.is_offset_ramping(act_prefix) or
            #        self.ezcaObj.is_gain_ramping(act_prefix)):
            #     pass
            coupling[i] = self.read_avg(sense_channels, t_avg, dt)
            self.ezcaObj.write(act_channel(DOFs[i]), force0[i])
            time.sleep(t_ramp)
            # while (self.ezcaObj.is_offset_ramping(act_prefix) or
                #    self.ezcaObj.is_gain_ramping(act_prefix)):
                # pass
        # print(coupling)
        coupling = np.array(coupling)
        # print(coupling)
        for i in range(len(coupling)):
            coupling[i] = coupling[i]/force[i]
        # print(coupling)
        coupling = coupling.T
        normalization = np.array(np.diag(np.diag(coupling)))
        # print(coupling)
        decoupling = np.matmul(normalization, np.linalg.inv(coupling))
        new_matrix = np.matmul(original_matrix, decoupling)
        print('original %s:\n'%matrix, original_matrix)
        print('new %s:\n'%matrix, new_matrix)
        return new_matrix

    def find_sensor_correction_gain(self, gain_channel='IP_SENSCORR_L_GAIN',
            input_channel='IP_SENSCORR_L_INMON',
            error_channel='IP_BLEND_ACCL_OUTPUT',
            rms_threshold=0.01, t_int=10, dt=1/8, update_law=nlms_update,
            step_size=0.5, step_size_limits=(1e-3, 1), reducing_lms_step=False,
            reduction_ratio=0.99, timeout=300, *args, **kwargs):
        """!!! INTERACTS WITH REAL SYSTEMS, USE WITH CAUTION !!!
        Using LMS algorithms to find sensor correction gain.

        Optional args:
            gain_channel: string
                The sensor correction gain channel.
            input_channel: string
                The input channel to the adaptive filter. Seismometer
                displacement output in this case.
            error_channel: string
                The error signal used in LMS algorithm to correct the adaptive
                gain. The blended inertial sensor signal in this case.
            rms_threshold: float
                The RMS threshold of the adaptive gain for termination of the
                gain finding loop. Defaults to 0.01 (for 1% sensor correction
                mismatch).
            t_int: int/float
                Integration time for calculated the RMS in seconds.
                Defaults to 10 (roughly band-limited to above 0.1 Hz).
            dt: int/float
                Time space between each sample in seconds. Defaults to 1/8.
            update_law: function in kontrol.unsorted  ## FIXME unsorted
                LMS or normalized LMS algorithm for updating the sensor
                correction gain. Default to be kontrol.unsorted.nlms_update,
                a Normalized LMS algorithm.
            step_size: int/float
                Step size to be used in the LMS algorithm. Defaults to be 0.5.
            step_size_limits: 2-tuple
                Lower and upper limit of the step size. Defaults to be (1e-3, 1)
            reducing_lms_step: boolean
                Allow reducing step size for better convergence. The step size
                will be reduced by a factor of reduction_ratio when the cost
                function (RMS of the error) remains the same or increased.
                Defaults to be False.
            timeout: int/float
                Timeout for the loop in seconds. Defaults to be 300.

        Returns:
            ts: list
                Time axis of the whole process.
            gains: list
                Sensor correction gain time series history.
            inputs: list
                Input time series.
            errors: list
                Error time series.
        """
        kwargs['mu_limits'] = step_size_limits
        kwargs['returnmu'] = True
        gain = self.ezcaObj.read(gain_channel)
        t0 = time.time()
        ts = [0]
        inputs = [self.ezcaObj.read(input_channel)]
        errors = [self.ezcaObj.read(error_channel)]
        gains = [gain]
        last_error_rms=0
        while 1:
            gain, step_size = nlms_update(coefs=[gains[-1]],
                input=[inputs[-1]], error=errors[-1], mu=step_size, **kwargs)
            self.ezcaObj.write(gain_channel, gain[0])
            gains += [gain[0]]
            time.sleep(dt)
            input = self.ezcaObj.read(input_channel)
            error = self.ezcaObj.read(input_channel)
            ts += [time.time() - t0]
            errors += [error]
            if ts[-1] >= t_int:
                mask = np.array(ts) >= (ts[-1]-t_int)
                gains_masked = np.array(gains)[mask]
                errors_masked = np.array(errors)[mask]
                if rms(gains_masked) <= rms_threshold or ts[-1] >= timeout:
                    break
                if rms(errors_masked) >= last_error_rms and reducing_lms_step:
                    step_size *= reduction_ratio
                    # print(step_size)
                last_error_rms = rms(errors_masked)
        return(ts, gains, inputs, errors)
