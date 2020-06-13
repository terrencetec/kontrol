import numpy as np
default_val = 0
noise_sigma = 0.1
default_readout = [default_val, noise_sigma]

prefix = {
    'INMON': default_readout,
    'OUTMON': default_readout,
    'OFFSET': default_readout,
    'GAIN': default_readout,
    'TRAMP': default_readout}
dof_LTY = {
    'L': dict(prefix),
    'T': dict(prefix),
    'Y': dict(prefix)
    }
dof_gas ={
    'gas': dict(prefix),
    }
blocks = lambda dof: {
    'DAMP': dict(dof),
    'TEST': dict(dof)
    }

system = {
    'IP': dict(blocks(dof_LTY)),
    'F0': dict(blocks(dof_gas)),
    'connections':{
        'IP_TEST_L_OFFSET':{
            'IP_DAMP_L_INMON': 1,
            'IP_DAMP_T_INMON': 0,
            'IP_DAMP_Y_INMON': 0},
        'IP_TEST_T_OFFSET':{
            'IP_DAMP_L_INMON': 0,
            'IP_DAMP_T_INMON': 1,
            'IP_DAMP_Y_INMON': 0},
        'IP_TEST_Y_OFFSET':{
            'IP_DAMP_L_INMON': 0,
            'IP_DAMP_T_INMON': 0,
            'IP_DAMP_Y_INMON': 1},
        }
    }
