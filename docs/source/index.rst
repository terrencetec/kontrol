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
* Complementary filter synthesis using :math:`\mathcal{H}_\infty`.

  * Synthesize optimal complementary filters in a 2-sensor configuration.
  * Only depends on sensor noises.
  * No specifications required.

* Frequency series modeling.

  * Model-based empirical fitting.
  * Model frequency series as zero-pole-gain and transfer function models.

* Sensing/Actuation Matrices.

  * Sensing/Actuation Matrices diagonalization with given coupling matrix.
  * General optical lever, horizontal and vertical optical lever sensing matrices,
    using parameters defined in "kagra-optical-lever<https://www.github.com/terrencetec/kagra-optical-lever>"_
    
- **Documentation:** https://kontrol.readthedocs.io/
- **Repository:** https://github.com/terrencetec/kontrol.git

.. toctree::
   :maxdepth: 5
   :caption: Contents:

   self
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
