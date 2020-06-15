from kontrol import visutils
from kontrol import fakeezca as ezca
# import ezca  #  Alternatively import fakeezca as ezca for testing.

BS = visutils.Vis('BS', ezca)  # Define a visutils.Vis object with optic\
	#  name and the ezca module.

stage = 'IP'

dofs = ['L', 'T', 'Y']  # Make sure the order is the same as appeared\
	# in the real-time system.

force  =[1000, 2000, 3000]  # Actuate 1000 counts in longitudinal,\
	# 2000 counts in transverse and 3000 counts in yaw. Do specify\
	# this or else the program will

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
