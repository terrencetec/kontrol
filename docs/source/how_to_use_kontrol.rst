How to use Kontrol
==================

``Kontrol`` was designed to help setting up a KAGRA vibration isolation system.
But, because many control systems in gravitational-wave detectors
are set up in a similar way,
``Kontrol`` can help setting up other control systems
as well.
You should have ``Kontrol`` installed.
If you haven't, refer to :ref:`Getting Started`.

``Kontrol`` provides the necessary modules and functionality for setting
a control system.

#. Sensors and actuators calibration and alignment (``kontrol.sensact``).

   #. ``kontrol.sensact.calibrate()`` for calibrating linear sensors.
   
   #. ``kontrol.curvefit.TransferFunctionFit`` for calibrated inertial
      sensors (sensors with frequency responses.)
   
   #. ``kontrol.sensact.SensingMatrix`` for refining sensing matrices
      for aligning signals.

#. System modeling (``kontrol.curvefit``).

   #. ``kontrol.curvefit.TransferFunctionFit`` for modeling system processes.
   #. ``kontrol.curvefit.spectrum_fit()`` for modeling frequency spectrums
      with the magnitude response of a transfer function.

#. Controller design (``kontrol.regulator``).

   #. ``kontrol.regulator.oscillator.pid()`` for designing position
      and damping PID controllers
      for oscillatory systems (systems with complex poles) with
      coefficients determined by critical criteria.
   #. ``kontrol.regulator.post_filter`` for designing post lower-pass
      and notch filters with stability constrains.

``Kontrol`` also provides advanced features for optimizing seismic isolation
systems.

#. H-infinity optimization for solve complementary filter problems
   (``kontrol.ComplementaryFilter``).

   #. Optimizes complementary filters for sensor fusion.
   
   #. Optimizes sensor correction filters for sensor correction.

   #. Optimizes feedback controller with known disturbance and noise.

All aforementioned funtionalities are detailed in Chapter 6 and 8 in Ref. [1]_.
These methods solve the static optimal control problem for
a seismic isolation system they you can find example usages of them in
the :ref:`Tutorials`.


References
----------

.. [1]
   Terrence Tak Lun Tsang. Optimizing Active Vibration Isolation Systems in
   Ground-Based Interferometric Gravitational-Wave Detectors.
   https://gwdoc.icrr.u-tokyo.ac.jp/cgi-bin/DocDB/ShowDocument?docid=14296
