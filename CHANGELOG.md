# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.2.0] - 2020-08-09
### Added
- kontrol.model.fit.noise2zpk() regress noise spectrum with ZPK model. 
- kontrol.utils.zpk() a wrapper on control for specifying transfer functions
  with lists of zeros and poles.
- kontrol.utils.remove_unstable() for negating the real part of the unstable
  poles and zeros of a transfer function.
- kontrol.model.fit.make_weight() for making weighting functions for data
  fitting.
- kontrol.filter.optimize.h2complementary() for synthesizing optimal
  complementary filters given two noise profiles (as transfer functions).

## [1.1.0] - 2020-07-19
### Added
- kontrol.sensact.diagonalization.rediagonalization() for refining
  diagonalization matrices given coupling matrix. Works for both actuation and
  sensing matrix.
- Added kontrol.visutils.Vis.read_full_matrix() for reading the full matrix
  from the real-time model.

### Changed
- Used rediagonalization() in kontrol.visutils.Vis.actuator_diag()

## [1.0.0] - 2020-07-18
### Changed
- filter subpackage for filter related and moved content from filters submodule
  to kontrol.filter.complementary
- rename unsorted subpackage to alogrithm subpackage.
- moved optimize.py to the filter subpackage.
- moved scripts in /kontrol/kontrol/test to the /kontrol/examples.

### Added
- kontrol.filter.comlementary.complementary_lucia(), a complementary filter
  with 8th-order polynomial designed by Lucia Trozzo that takes 7 parameters.
- model subpackage for any kind of model related operations, noise models,
  system models, etc. Also added generic piecewise expoenent noise models, LVDT
  and geophone noise models and fitting function.
- empty sensact and systemid subpackage for sensor/actuator related and
  system identification related (maybe move to model instead).
- kontrol.utils.tfmatrix2tf(). A function to convert transfer function matrix
  to a MIMO transfer function. In this way we can specify MIMO in a list of
  (list of control.xferfcn.TransferFunction) and then converted to a general
  MIMO control.xferfcn.TransferFunction.

### Removed
- kontrol.filters submodules, moved to kontrol.filter subpackage.

## [0.0.1] - 2020-06-17
### Added
- This CHANGELOG file to hopefully serve as an evolving example of a
  standardized open source project CHANGELOG.

[0.0.1]: https://github.com/terrencetec/kontrol/releases/tag/v0.0.1
