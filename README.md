# kontrol
KAGRA control python package

## Required packages
numpy, scipy, matplotlib, control

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

### unsorted
unsorted methods
#### methods
lms_filter(coefs, input, error)
