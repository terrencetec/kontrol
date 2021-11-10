Main Utilities
==============
Be sure to check out :ref:`Tutorials` for example usages of these utilities!

.. toctree::
   :maxdepth: 3


Complementary Filter Synthesis
------------------------------
Optimal complementary filter synthesis using :math:`\mathcal{H}_\infty` methods.

.. autoclass:: kontrol.ComplementaryFilter
   :members:
   :undoc-members:
   :show-inheritance:

Frequency Series Class
----------------------
Frequency domain and transfer function data modeling

.. autoclass:: kontrol.FrequencySeries
   :members:
   :undoc-members:
   :show-inheritance:

Sensors and Actuators Utilities
-------------------------------

Sensing Matrix Classes
^^^^^^^^^^^^^^^^^^^^^^
Sensing matrix and diagonalization.

.. autoclass:: kontrol.SensingMatrix
   :members:
   :undoc-members:
   :show-inheritance:

Optical Lever Sensing Matrices
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Sensing matrices for optical levers in KAGRA.

.. autoclass:: kontrol.OpticalLeverSensingMatrix
   :members:
   :undoc-members:
   :show-inheritance:

Horizontal Optical Lever Sensing Matrices
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Sensing matrices for horizontal optical levers (Type-A, Type-Bp) in KAGRA.

.. autoclass:: kontrol.HorizontalOpticalLeverSensingMatrix
   :members:
   :undoc-members:
   :show-inheritance:

Vertical Optical Lever Sensing Matrices
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Sensing matrices for vertical optical levers (Type-B) in KAGRA.

.. autoclass:: kontrol.VerticalOpticalLeverSensingMatrix
   :members:
   :undoc-members:
   :show-inheritance:

Sensor Calibration Functions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Functions for calibrating sensor readouts.

.. automodule:: kontrol.sensact.calibration
   :members:
   :undoc-members:
   :show-inheritance:


Spectral Analysis Functions
---------------------------
Spectral analysis related functions library.

.. automodule:: kontrol.core.spectral
   :members:
   :undoc-members:
   :show-inheritance:

Foton Utilities
---------------
KAGRA/LIGO Foton related utilities.

.. automodule:: kontrol.core.foton
   :members:
   :undoc-members:
   :show-inheritance:

Curve Fitting
-------------
Curve fitting

Curve fitting class
^^^^^^^^^^^^^^^^^^^
.. autoclass:: kontrol.curvefit.CurveFit
   :members:
   :undoc-members:
   :show-inheritance:

Models for Curve Fitting
^^^^^^^^^^^^^^^^^^^^^^^^
These classes are designed to use with ``kontrol.curvefit``

.. .. automodule:: kontrol.curvefit.model
..    :members:
..    :undoc-members:
..    :show-inheritance:

.. autoclass:: kontrol.curvefit.model.Model
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: kontrol.curvefit.model.TransferFunctionModel
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: kontrol.curvefit.model.DampedOscillator
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: kontrol.curvefit.model.SimpleZPK
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: kontrol.curvefit.model.ComplexZPK
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: kontrol.curvefit.model.StraightLine
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: kontrol.curvefit.model.Erf
   :members:
   :undoc-members:
   :show-inheritance:


Control Regulator Design
------------------------
Functions for algorithmic design of control regulators

Feedback Control
^^^^^^^^^^^^^^^^

.. automodule:: kontrol.regulator.feedback
   :members:
   :undoc-members:
   :show-inheritance:
   
.. automodule:: kontrol.regulator.oscillator
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: kontrol.regulator.predefined
   :members:
   :undoc-members:
   :show-inheritance:

