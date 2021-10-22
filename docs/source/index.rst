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

Features
--------
* Complementary filter synthesis using :math:`\mathcal{H}_\infty` methods.

  * Synthesize optimal complementary filters in a 2-sensor configuration.

* Curve fitting

  * Fit transfer functions, spectral densities, etc.

* Frequency series modeling (Soon deprecating. See Curve fitting).

  * Model-based empirical fitting.
  * Model frequency series as zero-pole-gain and transfer function models.

* Sensing/Actuation Matrices.

  * Sensing/Actuation Matrices diagonalization with given coupling matrix.
  * General optical lever, horizontal and vertical optical lever sensing matrices,
    using parameters defined in `kagra-optical-lever <https://www.github.com/terrencetec/kagra-optical-lever>`_.

* Noise spectral density estimation using correlation methods.

  * 2-channel method [1]_
  * 3-channel method [2]_

* Foton utilities.

  * Convert Python transfer function objects to Foton expressions
  * Support for translating transfer functions with higher than 20 order (the
    Foton limit).

* Easy Channel Access (EZCA) utilities (wrapper)

  * Read and write matrices to EPICS record.

Don't hesitate to check out the `tutorials <https://kontrol.readthedocs.io/en/latest/tutorial.html>`_!

- **Documentation:** https://kontrol.readthedocs.io/
- **Repository:** https://github.com/terrencetec/kontrol.git

.. toctree::
   :maxdepth: 5
   :caption: Contents:

   self
   concept
   getting_started
   tutorial
   main_utilities
   kontrol
   contact
   developers

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


.. [1]
    Aaron Barzilai, Tom VanZandt, and Tom Kenny.
    Technique for measurement of the noise of a sensor in the
    presence of large background signals. Review of Scientific Instruments,
    69:2767–2772, 07 1998.

.. [2]
    R. Sleeman, A. Wettum, and J. Trampert.
    Three-channel correlation analysis: A new technique to measure
    instrumental noise of digitizers and seismic sensors.
    Bulletin of the Seismological Society of America, 96:258–271, 2006.
