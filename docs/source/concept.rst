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

In :ref:`Tutorials`, these tools in Kontrol will be demonstrated
by setting up a virtual single stage suspension.
For advanced usage, refer to :ref:`Main Utilities` and :ref:`Kontrol API`
for detailed documentation of the package.

Basic control systems setup
---------------------------
A typical complete control systems setup workflow would be the following:

1. Calibration:

  a. Obtain sensor calibration data.

    * For linear sensors, obtain a 2-array consisting of physical quantity (e.g. displacement) and readout (e.g. voltage or digital counts).
    * For sensors requiring calibration filters, it is necessary to do an inter-calibration between the sensor and another calibrated sensor. In this case, obtain a frequency response between the readouts of the calibrated sensor and the sensor of interest.

  b. Obtain calibration factor/filter
    * For linear sensors, use ``kontrol.sensact.calibrate()``.
    * For sensors requiring calibration filters, fit the transfer function using ``kontrol.curvefit.TransferFunctionFit`` class. This requires the user to define a model of the calibration filter.

  c. Implement the calibration factor/filter
    * For calibration factors, simply copy it into the MEDM interface.
    * For calibration filters, convert the calibrated transfer function into a ``kontrol.TransferFunction`` object and then use the ``kontrol.TransferFunction.foton()`` method to extract a Foton string, which can be directly copied to the Foton interface.

2. Diagonalization (We assume geometric matrices are implemented):

  a. Sensors:

    i. Somehow obtain obtain a coupling matrix that maps the control space to the sensor space.
    ii. Define a ``kontrol.sensact.SensingMatrix`` class and use ``kontrol.sensact.SensingMatrix.diagonalize()`` method to obtain a diagonalizing sensing matrix. If the geometric matrix and diagonalization matrix can be implemented separately, the object can be defined with an identity matrix. Otherwise, the method returns a diagonalized geometric matrix.

  b. Actuators:

    * Terrence doesn't believe there's a true way to diagonalize actuators so the method is not implemented. Hint: diagonalizing actuation matrices are different from diagonalizing sensing matrices.

3. Transfer function modeling

   #. Obtain the frequency response data and load it using something like ``vishack.data.diaggui.Diaggui.tf()`` from `VISHack <https://github.com/gw-vis/vishack>`_.
   #. (Optional) Initial guess: Fit the frequency response manually by tweaking a ``kontrol.curvefit.model.ComplexZPK`` class (or other models).
   #. Fit the frequency response with a ``kontrol.curvefit.TransferFunctionFit`` class. If the an initial guess is not provided, then a global optimization method, such as ``scipy.optimize.differential_evolution``, is needed to be specified as the optimizer attribute.
   #. (Optional) Obtain a transfer function from ``kontrol.curvefit.model.ComplexZPK.tf`` (or otherwise), define it as a ``kontrol.TransferFunction`` object and export a Foton expression using ``kontrol.TransferFunction.foton()`` method.
   #. (Optional) Alternatively, export the transfer function object using ``kontrol.TransferFunction.save()`` method.

4. Obtain the optimal PID controller (For systems that have 2 more complex poles than complex zeros).

   #. Obtain a transfer function (from above or otherwise).
   #. Use ``kontrol.regulator.oscillator.pid()`` to optimize a derivative, PD, or PID controller.
      * Derivative gain is optimized by converting two complex poles to simple double poles.
   #. Use ``kontrol.regulator.post_filter.post_notch()`` and ``kontrol.regulator.post_filter.post_low_pass()`` to obtain necessary notch filter and low-pass filter (with a specified phase margin) for stabilization and practical implementation.
   #. Again, use ``kontrol.TransferFunction`` to extract their Foton expressions for implementation.


Advanced control methods
------------------------
* ``kontrol.complementary_filter.ComplementaryFilter`` class provides an option use H-infinity synthesis to optimize complementary filters according to modeled sensor noises.
  
  * The same method can be used to optimize sensor correction filters and feedback controllers.

Don't hesitate to check out the :ref:`Tutorials` for examples. 
