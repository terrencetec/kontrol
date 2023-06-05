|logo|

**A dedicated Python control system library for control system optimization and utilities in KAGRA**

|website| |release| |rtd| |license| |build_and_tests| |codecov|

Kontrol
=======
Kontrol (also pronounced "control") is a python package for KAGRA control system
related work. It is intented for both offline and real-time (via Ezca and maybe
diaggui and nds2 later) usage. In principle, it should cover all control related topics
ranging from sensor/actuator diagonalization to system identification and
control filter design.

Features
--------
* Complementary filter synthesis using :math:`\mathcal{H}_\infty` methods [1]_.

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

* Spectral analysis

  * Noise spectral density estimation using 2-channel method [2]_
  * Noise spectral density estimation using 3-channel method [3]_
  * Time series simulation of a given spectral density.

* Foton utilities.

  * Convert Python transfer function objects to Foton expressions
  * Support for translating transfer functions with higher than 20 order (the
    Foton limit).

* Easy Channel Access (EZCA) utilities (wrapper)

  * Read and write matrices to EPICS record.

* Transfer Function
  
  * Export transfer functions to foton expressions.
  * Save TransferFunction objects to pickle files.

* Controller design

  * Auto-design of PID controller for oscillatory systems (like pendulum suspensions)
  * Auto-design of post-filters such as notch filters and low-pass filters.

* Dynamic mode decomposition

  * Time series modeling using dynamic mode decomposition

Don't hesitate to check out the `tutorials <https://kontrol.readthedocs.io/en/latest/tutorial.html>`_!

- **Documentation:** https://kontrol.readthedocs.io/
- **Repository:** https://github.com/terrencetec/kontrol.git

Getting Started
===============

Dependencies
------------

Required
^^^^^^^^

* control>=0.9
* numpy
* matplotlib 
* scipy

Optional
^^^^^^^^
* ezca (Needed for accessing EPICs records/real-time model process variables. Use conda to install it.)
* `vishack <https://github.com/gw-vis/vishack>`_ or `dttxml <https://github.com/mccullerlp/dttxml>`_ (For extracting data from diaggui xml files.)

If you would like to install Kontrol on your local machine with, then pip
should install the required dependencies automatically for you. However, if
you use Kontrol in a Conda environment, you should install the dependencies
before installing Kontrol to avoid using pip. In Conda environment, simply type

.. code-block:: bash

  conda install -c conda-forge numpy scipy matplotlib control ezca

Install from source
-------------------

For local usage, type

.. code-block:: bash

  $ git clone https://github.com/terrencetec/kontrol.git
  $ cd kontrol
  $ pip install .

For k1ctr workstations, make sure a virtual environment is enabled before
installing any packages.

For Developers
==============

Standards and Tools
-------------------
Please comply with the following standards/guides as much as possible.

Coding style
^^^^^^^^^^^^
- **PEP 8**: https://www.python.org/dev/peps/pep-0008/

CHANGELOG
^^^^^^^^^
- **Keep a Changelog**: https://keepachangelog.com/en/1.0.0/

Versioning
^^^^^^^^^^
- **Semantic Versioning**: https://semver.org/spec/v2.0.0.html

Packaging
^^^^^^^^^
- **PyPA**: https://www.pypa.io
- **python-packaging**: https://python-packaging.readthedocs.io

Documentation
^^^^^^^^^^^^^
- **NumPy docstrings**: https://numpydoc.readthedocs.io/en/latest/format.html
- **Sphinx**: https://www.sphinx-doc.org/
- **Read The Docs**: https://readthedocs.org/
- **Documenting Python Code: A Complete Guide**: https://realpython.com/documenting-python-code/

How to Contribute
-----------------
Just do it.

Pending
^^^^^^^
- Documentation.
- tests!
- Model reference sensor/actuator diagonalization
- Add support for reading Shoda-san's SUMCON simulations.
- Controller optimization
- Optimal controller synthesis
- python-foton interface.
- Diaggui support.
- **Issues**: https://github.com/terrencetec/kontrol/issues

.. |logo| image:: /docs/source/_static/kontrol_logo_256x128.svg
    :alt: Logo
    :target: https://github.com/terrencetec/kontrol

.. |website| image:: https://img.shields.io/badge/website-kontrol-blue.svg
    :alt: Website
    :target: https://github.com/terrencetec/kontrol

.. |release| image:: https://img.shields.io/github/v/release/terrencetec/kontrol?include_prereleases
   :alt: Release
   :target: https://github.com/terrencetec/kontrol/releases

.. |rtd| image:: https://readthedocs.org/projects/kontrol/badge/?version=latest
   :alt: Read the Docs
   :target: https://kontrol.readthedocs.io/

.. |license| image:: https://img.shields.io/github/license/terrencetec/kontrol
    :alt: License
    :target: https://github.com/terrencetec/kontrol/blob/master/LICENSE

.. |travis-ci| image:: https://travis-ci.com/terrencetec/kontrol.svg?branch=master
    :alt: travis-ci
    :target: https://app.travis-ci.com/github/terrencetec/kontrol

.. |build_and_tests| image:: https://github.com/terrencetec/kontrol/actions/workflows/github-action-ci.yml/badge.svg
   :alt: built and tests
   :target: https://github.com/terrencetec/kontrol/actions/workflows/github-action-ci.yml

.. |codecov| image:: https://codecov.io/gh/terrencetec/kontrol/branch/master/graph/badge.svg?token=CI5TW1L81H
    :alt: codecov
    :target: https://codecov.io/gh/terrencetec/kontrol

.. [1]
    T. T. L. Tsang, T. G. F. Li, T. Dehaeze, C. Collette.
    Optimal Sensor Fusion Method for Active Vibration Isolation Systems in
    Ground-Based Gravitational-Wave Detectors.
    https://arxiv.org/pdf/2111.14355.pdf

.. [2]
    Aaron Barzilai, Tom VanZandt, and Tom Kenny.
    Technique for measurement of the noise of a sensor in the
    presence of large background signals. Review of Scientific Instruments,
    69:2767–2772, 07 1998.

.. [3]
    R. Sleeman, A. Wettum, and J. Trampert.
    Three-channel correlation analysis: A new technique to measure
    instrumental noise of digitizers and seismic sensors.
    Bulletin of the Seismological Society of America, 96:258–271, 2006.

