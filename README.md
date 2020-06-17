# Kontrol
KAGRA control python package

Recommend using under Conda environment if using k1ctr workstations.

## How to Install
For local usage, type
  $ git clone https://github.com/terrencetec/kontrol.git
  $ cd kontrol
  $ pip install .

For k1ctr workstations, make sure a virtual environment is enabled before
installing anything

## Required packages
* numpy
* scipy
* matplotlib
* control
* ezca (installed in KAGRA workstations, will use local fakeezca if not installed.)

## Standards and Tools
Please comply with the following standards/guides as much as possible.
* Coding style
  * [PEP 8](https://www.python.org/dev/peps/pep-0008/)
* CHANGELOG
  * [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
* Versioning
  * [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
* Packaging
  * [PyPa](https://www.pypa.io)
  * [python-packaging](https://python-packaging.readthedocs.io)
* Documentation
  * [NumPy docstrings](https://numpydoc.readthedocs.io/en/latest/format.html)
  * [Sphinx](https://www.sphinx-doc.org/)
  * [Read The Docs](https://readthedocs.org/)
  * [Documenting Python Code: A Complete Guide](https://realpython.com/documenting-python-code/)

## Modules
### optimize
Optimization package
#### methods
optimize_complementary_filter(filter_, spectra, f, method=differential_evolution, bounds=None, x0=None, \*args, \*\*kwargs)

### filters
Standard filter definitions
#### methods
complementary_sekiguchi(coefs)

complementary_modified_sekiguchi(coefs)

### utils
Utilities
#### methods
quad_sum(\*spectra)

norm2(spectrum)

rms(ts)

### unsorted
unsorted methods
#### methods
lms_update(coefs, input, error, mu=None, mu_limits=(0, np.inf), returnmu=False,
        small_number=1e-3, \*args, \*\*kwargs):

nlms_update(coefs, input, error, mu=0.5, mu_limits=(0, 1), returnmu=False,
        small_number=1e-3, \*args, \*\*kwargs):

### visutils
Utilities for VIS system.

These methods are wrappers around Ezca
and will interact with the real-time systems. Any methods and interacts with the
actual system falls into the category of this visutils. Refer to other modules
of Kontrol for other offline methods.
#### classes
Vis(optic)
#### methods
Vis.actuator_diag(stage, dofs, act_block='TEST', act_suffix='OFFSET',
                      sense_block='DAMP', sense_suffix='INMON',
                      matrix='EUL2COIL', force=[], no_of_coils=None, t_ramp=10,
                      t_avg=10, dt=1/8)

Vis.find_sensor_correction_gain(gain_channel='IP_SENSCORR_L_GAIN',
            input_channel='IP_SENSCORR_L_INMON',
            error_channel='IP_BLEND_ACCL_OUTPUT',
            rms_threshold=0.01, t_int=10, dt=1/8, update_law=nlms_update,
            step_size=0.5, step_size_limits=(1e-3, 1), reducing_lms_step=False,
            reduction_ratio=0.99, timeout=300, \*args, \*\*kwargs)

### fakeezca
A replacement for ezca for testing purpose. Copied from Mark Barton's folder.
Ezca.read(channel) used to return the number of pi. Now it was modified to
return pi plus a random gaussian noise with sigma=0.1.
#### classes
Ezca(prefix)
#### methods
Ezca.read(channel)

Ezca.write(channel)

Ezca.switch(sfname, *args)
