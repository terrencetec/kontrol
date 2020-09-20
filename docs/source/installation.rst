Getting Started
===============

.. toctree::
  :maxdepth: 2

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
* ezca (Needed for accessing EPICs records/real-time model process variables. Use kontrol.fakeezca if not needed)

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
