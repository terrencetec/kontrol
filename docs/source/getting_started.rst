Getting Started
===============

.. toctree::
  :maxdepth: 2

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

Concept and Tutorials
---------------------

Check out :ref:`How to use Kontrol` and :ref:`Tutorials` to see how this package
can be utilized for setting up and optimizing
seismic isolation control systems.
