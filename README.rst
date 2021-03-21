|logo|

**A dedicated Python control system library for control system optimization and utilities in KAGRA**

|website| |release| |rtd| |license| |travis-ci| |codecov|

Kontrol (also pronounced "control") is a python package for KAGRA control system
related work. It is intented for both offline and real-time (via Ezca and maybe
diaggui and nds2 later) usage. In principle, it should cover all control related topics
ranging from sensor/actuator diagonalization to system identification and
control filter design.

Major Features
--------------
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

Getting Started
===============

Dependencies
------------

Required
^^^^^^^^

* numpy
* scipy
* matplotlib
* control

Optional
^^^^^^^^
* ezca (Needed for accessing EPICs records/real-time model process variables.

Use kontrol.fakeezca if not needed)

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

.. |logo| image:: /images/kontrol_logo_256x128.svg
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
    :target: https://travis-ci.com/terrencetec/kontrol

.. |codecov| image:: https://codecov.io/gh/terrencetec/kontrol/branch/master/graph/badge.svg?token=CI5TW1L81H
    :alt: codecov
    :target: https://codecov.io/gh/terrencetec/kontrol
