Concept
=======
``Kontrol`` is a Python package that is programmed to help setting
KAGRA control systems, particularly vibration isolation systems.
``Kontrol`` can be used designed to be used side-by-side with
KAGRA software for data acquisition and control systems implementation,
such as ``diaggui`` and ``Foton``.
``Kontrol`` provides the neccessary tools for completing a control system setup
jobs, including

#. Sensor and actuator calibration and diagonalization (``kontrol.sensact`` module),
#. Transfer function and frequency spectrum modeling (``kontrol.curvefit`` module), and
#. Controller and filter design (``kontrol.regulator`` and ``kontrol.complementary_filter`` modules).

And, other utilities interfacing Python and KAGRA digital systems, such as
``kontrol.ezca``, are provided.

Basic control systems setup
---------------------------
A typical complete control systems setup workflow would be the following:

#. Calibration:
  #. Obtain sensor calibration data.
    * For linear sensors, obtain a 2-array consisting of physical quantity (e.g. displacement) and readout (e.g. voltage or digital counts).
    * For sensors requiring calibration filters, it is necessary to do an inter-calibration between the sensor and another calibrated sensor. In this case, obtain atransfer function between the readouts of the calibrated sensor and the sensor of interest.
  #. Obtain calibration factor/filter
    * For linear sensors, use ``kontrol.sensact.calibrate()``.
    * For sensors requiring calibration filters, fit the transfer function using ``kontrol.curvefit.TransferFunctionFit`` class. This requires the user to define a model of the calibration filter.
  #. Implement the calibration factor/filter
    * For calibration factors, simply copy it into the MEDM interface.
    * For calibration filters, convert the calibrated transfer function into a ``kontrol.TransferFunction`` object and then use the ``kontrol.TransferFunction.foton()`` method to extract a Foton string, which can be directly copied to the Foton interface.
#. Diagonalization (We assume geometric matrices are implemented):
  #. Sensors:
    #. Somehow obtain obtain a coupling matrix that maps the control space to the sensor space.
    #. Define a ``kontrol.sensact.SensingMatrix`` class and use ``kontrol.sensact.SensingMatrix.diagonalize()`` method to obtain a diagonalizing sensing matrix. If the geometric matrix and diagonalization matrix can be implemented separately, the object can be defined with an identity matrix. Otherwise, the method returns a diagonalized geometric matrix.
  #. Actuators:
    * Terrence doesn't believe there's a true way to diagonalize actuators so the method is not implemented. Hint: diagonalizing actuation matrices are different from diagonalizing sensing matrices.
#. test
