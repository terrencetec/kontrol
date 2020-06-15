from kontrol import visutils
from kontrol import fakeezca as ezca
# import ezca  #  Alternatively import fakeezca as ezca for testing.

def test_actuator_diag():
    """Expected output at the end (numbers are ~ pi for the oringal matrix):
    original EUL2COIL:
     [[3.12307805 3.10118585 3.00159104]
     [3.04553458 3.29171708 3.12165122]
     [3.25032618 3.14461291 3.20363117]]
    new EUL2COIL:
     [[-16.47052991   0.23618048  19.3326145 ]
     [ 85.14613189 -73.80129973  -8.02682917]
     [-35.42087779  29.40472295   9.15054005]]
    [[-16.47052991   0.23618048  19.3326145 ]
     [ 85.14613189 -73.80129973  -8.02682917]
     [-35.42087779  29.40472295   9.15054005]]
    """
    BS = visutils.Vis('BS', ezca)  # Define a visutils.Vis object with optic\
    	#  name and the ezca module.

    stage = 'IP'

    dofs = ['L', 'T', 'Y']  # Make sure the order is the same as appeared\
    	# in the real-time system.

    force  =[1000, 2000, 3000]  # Actuate 1000 counts in longitudinal,\
    	# 2000 counts in transverse and 3000 counts in yaw. Do specify\
    	# this or else the program will default actuations to 1000 counts.

    no_of_coils = 3  # Optional. Determined by the EUL2COIL matrix if\
    	# not specified.

    t_ramp = 0.1  # For testing pupose, we put a small number.\
        # In practice, this should be around 10 seconds or more.

    t_avg = 1  # Again, this is for test only. Put a reasonable number
        # when using this.

    EUL2COIL_new = BS.actuator_diag(stage, dofs, act_block='TEST',
    	act_suffix='OFFSET', sense_block='DAMP', sense_suffix='INMON',
    	matrix='EUL2COIL', force=force, no_of_coils=no_of_coils,
    	update_matrix=False, t_ramp=t_ramp, t_avg=t_avg, dt=1/8)

    print(EUL2COIL_new)
