.. kontrol documentation master file, created by
   sphinx-quickstart on Thu Jun 18 04:39:35 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Kontrol Home
============

Kontrol (also pronounced "control") is a python package for KAGRA control system
related work. It is intented for both offline and real-time (via Ezca and maybe
diaggui and nds2 later) usage. In principle, it should cover all control related topics
ranging from sensor/actuator diagonalization to system identification and
control filter design.

Major Features
--------------

**Core**

* Complementary filter synthesis using :math:`\mathcal{H}_\infty`.

  * Synthesize optimal complementary filters in a 2-sensor configuration.
  * Only depends on sensor noises.
  * No specifications required.

Other Features
--------------
* filter: Complementary filter definitions and optimization.
* model: Sensor noise models, fitting, noise to zpk regression.
* utils: quadrature sum, 2-norm, rms
* controlutils: transfer function matrix to MIMO tf, zpk
  transfer function definition.
* visutils: VIS utility functions, actuator diagonalization, sensor correction
  gain finding
* sensact: rediagonalization of actuation/sensing matrices given coupling
  matrix.

- **Documentation:** https://kontrol.readthedocs.io/
- **Repository:** https://github.com/terrencetec/kontrol.git

.. toctree::
   :maxdepth: 5
   :caption: Contents:

   self
   getting_started
   tutorial
   core_functions
   kontrol
   contact
   developers

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
