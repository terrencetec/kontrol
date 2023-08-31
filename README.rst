|logo|

**Python package for KAGRA suspension and seismic isolation control.**

|website| |release| |pypi| |rtd| |license| |build_and_tests| |codecov|

Kontrol
=======
The name "Kontrol" is a blend word combining KAGRA,
the gravitational-wave detector in Japan, and control, as in control system.
The package contains necessary features for commissioning
a KAGRA suspension.
These features include:

* **Sensor and actuation utilities** (``kontrol.sensact``): 
  Calibration and Sensing/Actuation Matrices
* **System Modeling** (``kontrol.curvefit``): Fitting frequency response data
  using Transfer function model.
* **Basic suspension controller design** (``kontrol.regulator``):
  Damping and position controller
  with stabilizing post filters such as low-pass and notch filters.

To interface the results generated from the above functionalities to 
the KAGRA control system, Kontrol also provides:

* **Foton utilities** (``kontrol.foton``): converting transfer function to/from
  Foton strings.
* **Ezca wrapper** (``kontrol.ezca``): Fetch/put control matrices to/from
  the digital system.

The above features form a control design pipeline from calibration
to controller design for commissioning
KAGRA suspension with basic functionality.

Besides the basic functionalities, Kontrol also contains
advanced features are being continuously developed in order to
further enhance seismic isolation performance.
Currently, Kontrol contains:

* **H-infinity optimal complementary filters** (``kontrol.ComplementaryFilter``):
  Solves complementary control problems, optimizing control filters for
  sensor fusion, sensor correction, and vibration isolation control
  problems [1]_ [2]_.
* **Dynamic mode decomposition** (``kontrol.dmd``): Dynamic mode decomposition
  for time-series forecasting and modeling. For future model predictive
  control work.

To familiarize users with the package, 
step-by-step
`tutorials <https://kontrol.readthedocs.io/en/latest/tutorial.html>`_
are provided. Upon finishing the tutorials, the users should
be able to convert the scripts into usable ones interfacing real data that
can be used for the physical systems.

While Kontrol was created for setting up active isolation systems for
systems in gravitational-wave detectors, it is not exclusive for
usage in gravitaional-wave detectors or suspensions.
The setup of an active isolation system is similar to many control systems.
Kontrol is coded with no presumption of the system in question.
So users outside the gravitational-wave and active isolation community
may also find this tutorial/package useful.

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
* ezca (Needed for accessing EPICs records/real-time model process variables.
  Use conda to install it.)
* `vishack <https://github.com/gw-vis/vishack>`_
  or `dttxml <https://github.com/mccullerlp/dttxml>`_
  (For extracting data from diaggui xml files.)

If you would like to install Kontrol on your local machine with, then pip
should install the required dependencies automatically for you. However, if
you use Kontrol in a Conda environment, you should install the dependencies
before installing Kontrol to avoid using pip. In Conda environment, simply type

.. code-block:: bash

  conda install -c conda-forge numpy scipy matplotlib control ezca

Using **Conda** is strongly recommended because ``control``
depends on ``slycot`` which can be cumbersome to install without conda.
Check `this issue <https://github.com/terrencetec/kontrol/issues/19>`_ out
if you wish to install ``slycot`` on a Linux machine.

Install from PyPI
-----------------

.. code-block:: bash
   
   pip install kontrol

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


.. |logo| image:: https://raw.githubusercontent.com/terrencetec/kontrol/master/images/kontrol_logo_256x128.svg
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

.. |pypi| image:: https://badge.fury.io/py/kontrol.svg
    :target: https://badge.fury.io/py/kontrol


.. [1]
    T. T. L. Tsang, T. G. F. Li, T. Dehaeze, C. Collette.
    Optimal Sensor Fusion Method for Active Vibration Isolation Systems in
    Ground-Based Gravitational-Wave Detectors.
    https://arxiv.org/pdf/2111.14355.pdf

.. [2]
   Terrence Tak Lun Tsang. Optimizing Active Vibration Isolation Systems in
   Ground-Based Interferometric Gravitational-Wave Detectors.
   https://gwdoc.icrr.u-tokyo.ac.jp/cgi-bin/DocDB/ShowDocument?docid=14296
