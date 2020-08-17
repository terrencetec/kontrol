Introduction
============

Kontrol (also pronounced "control") is a python package for KAGRA control system
related work. It is intented for both offline and real-time (via Ezca and maybe
diaggui and nds2 later) usage. In principle, it should cover all control related topics
ranging from sensor/actuator diagonalization to system identification and
control filter design.

Features
--------
* filter: Complementary filter definitions, optimization, and H2 optimal
  complementary filter synthesis.
* model: Sensor noise models, fitting, noise to zpk regression.
* algorithm: LMS and normalized-LMS algorithms.
* utils: quadrature sum, 2-norm, rms, transfer function matrix to MIMO tf, zpk
  transfer function definition.
* visutils: VIS utility functions, actuator diagonalization, sensor correction
  gain finding
* sensact: rediagonalization of actuation/sensing matrices given coupling
  matrix.

Upcoming
--------
* filter: More filters. Hinf complementary filter and sensor correction
  synthesis.
* model: Conversion functions for Shoda-san's SUMCON suspension simulations.
  Transfer function fitting. Seismic noise models (maybe)
* sensact: maybe calibration?
* utils: control.xferfcn.TransferFunction to fonton zpk format.

example codes.

There will be an upcoming Hinf/H2 function for controller synthesis which uses
the python-control package and depends on the slycot module. This is
automatically installed when installing python-control with Conda while not
with pip. So, using under Conda environment is highly recommended.
