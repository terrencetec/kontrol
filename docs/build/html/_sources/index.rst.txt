.. kontrol documentation master file, created by
   sphinx-quickstart on Thu Jun 18 04:39:35 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Kontrol Home
====================

Kontrol (also pronounced "control") is a python package for KAGRA control system
related work. It is intented for both offline and real-time (via Ezca and maybe
diaggui and nds2 later) usage. In principle, it should cover all control related topics
ranging from sensor/actuator diagonalization to system identification and
control filter design.

There will be an upcoming Hinf/H2 function for controller synthesis which uses
the python-control package and depends on the slycot module. This is
automatically installed when installing python-control with Conda while not
with pip. So, using under Conda environment is highly recommended.

- **Documentation:** Does not exist yet.
- **GitHub:** https://github.com/terrencetec/kontrol

.. toctree::
   :maxdepth: 3
   :caption: Contents:

   self
   introduction
   installation
   modules
   contact

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
