Kontrol
=======
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

## How to Install Kontrol
### Required packages
* numpy
* scipy
* matplotlib
* control
* ezca (installed in KAGRA workstations, will use local fakeezca if not installed.)
###
For local usage, type
```
$ git clone https://github.com/terrencetec/kontrol.git
$ cd kontrol
$ pip install .
```
For k1ctr workstations, make sure a virtual environment is enabled before
installing anything.

## Standards and Tools
Please comply with the following standards/guides as much as possible.
* Coding style
  * [PEP 8](https://www.python.org/dev/peps/pep-0008/)
* CHANGELOG
  * [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
* Versioning
  * [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
* Packaging
  * [PyPa](https://www.pypa.io)
  * [python-packaging](https://python-packaging.readthedocs.io)
* Documentation
  * [NumPy docstrings](https://numpydoc.readthedocs.io/en/latest/format.html)
  * [Sphinx](https://www.sphinx-doc.org/)
  * [Read The Docs](https://readthedocs.org/)
  * [Documenting Python Code: A Complete Guide](https://realpython.com/documenting-python-code/)

## How to Contribute
Just do it.
### Pending
- Documentation.
- tests!
- Model reference sensor/actuator diagonalization
- Add support for reading Shoda-san's SUMCON simulations.
- Controller optimization
- Optimal controller synthesis
- python-foton interface.
- Diaggui support.
- [Issues](https://github.com/terrencetec/kontrol/issues)
