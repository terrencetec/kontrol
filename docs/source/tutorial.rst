Tutorials
=========
This tutorial is divided into two parts, basic suspension
commissioning and advanced control methods.

In the first part, the commissioning of the active control system for
a stage of a virtual suspension with 3 degrees of freedom is demonstrated.
This covers topics including: sensor
calibration, sensing matrices, system modeling, and controller design.
By the end of the first part, users should be able
to commission suspensions to achieve basic damping and position control
with appropriate filtering.

The second part of the tutorial, advanced control methods, covers
specialized frontier control topics for seismic isolation that
are not considered standard.
This section is not compulsory for suspension commissioning.
The content in this section is everchanging and being updated
as new methods are being developed and coded into Kontrol.

Kontrol has more than what's covered in the tutorials.
Be sure to check out the :ref:`Main Utilities` and :ref:`Kontrol API`
sections for detailed documentation.

Basic suspension commissioning
------------------------------
In this section, we demonstrate the use of the Kontrol package
to obtain necessary components for setting up a stage of a multistage
pendulum suspension. The stage here simulates an inverted pendulum stage
of the KAGRA Type-A and Type-B suspension.

The inverted pendulum is
constrained on a horizontal plane so there're 2 translational degrees of
freedom and 1 rotational degree of freedom.
Without loss of generality, the three degrees of freedom are named
:math:`x_1`, :math:`x_2`, and :math:`x_3`.

To measure the motion of the inverted pendulum, 3 relative sensors
and 3 inertial sensors are available. The relative sensors measure
the relative displacement between the inverted pendulum while the inertial
sensors measure an inertial motion which can be used to achieve active
isolation.
To achieve basic damping and position control, the inertial sensors are
not required.
For simplicity, let's assume we have access to three sensor readout
:math:`y_1`, :math:`y_2`, and :math:`y_3`.

The inverted pendulum has three distinct resonances at 0.06, 0.1, and 0.2 Hz
in :math:`x_1`, :math:`x_2`, and :math:`x_3`, respectively.
The horizontal degrees of freedom also each coupled to two other modes,
at 0.5 and 0.8 Hz,
corresponding to the resonances of the multiple pendulum chain.
The transfer function from actuation to displacement in the :math:`x_1`
direction reads

.. math::

   P_h(s) = k_1\frac{\omega_1^2}{s^2+\frac{\omega_1}{Q_1}s+\omega_1^2}
          + k_2\frac{\omega_2^2}{s^2+\frac{\omega_2}{Q_2}s+\omega_2^2}
          + k_3\frac{\omega_3^2}{s^2+\frac{\omega_3}{Q_3}s+\omega_3^2}\,.

and that in the rotational direction :math:`x_3` reads

.. math::

   P_r(s) = k_4\frac{\omega_4^2}{s^2+\frac{\omega_4}{Q_4}s+\omega_4^2}\,.
 
The transfer function for `x_2` has the same form as that of `x_1` but
with different frequencies and Q values.

The objective here is to achieve a resonable damping and position control
for these three degress of freedom.

Sensors and actuators
^^^^^^^^^^^^^^^^^^^^^
Calibration
***********
A relative sensor outputs a voltage corresponding to the measured displacement
The voltage is converted into an integer number ranging from
, say -32768 to 32768, via a 16-bit analog-to-digital converter.
The sensor is linear about the operating range and we need
to obtain a calibration factor which converts the number into displacement.

Suppose we have a caliper so we can measure the displacement, we record
both the displacement and the sensor output as we scan the full range of the
sensor. We eventually obtained

.. code:: Python

   Displacement = [-10, -9, -8, -7, -6, -5, -4, -3, -2, -1, 0,
-1, 2, 3, 4, 5, 6, 8, 9, 10]

and 

Output = [-32765, -32760, -32741, -32680, -32504, -32060, -31068, -29109,
-25691, -20421, -13241, -4596, 4598, 13243, 20423, 25693, 29111, 31070, 32062, 32506, 32682]





Advanced Control Method
-----------------------


Complementary Filter
--------------------

.. toctree::
   :maxdepth: 1

   tutorials/complementary_filter_synthesis_using_h-infinity_methods
   tutorials/complementary_filter_synthesis_for_typical_lvdt_and_geophone

..
   Noise Spectrum Modeling
   -----------------------

   .. toctree::
      :maxdepth: 1

      tutorials/frequency_series_fitting_with_empirical_model
      tutorials/frequency_series_fitting_with_transfer_function
      tutorials/frequency_series_fitting_with_transfer_function_part2
      tutorials/noise_spectrum_modeling_with_optimization

Spectral Analysis
-----------------

.. toctree::
   :maxdepth: 1

   tutorials/noise_estimation_using_correlation_methods
   tutorials/spectral_time_series_simulation

Sensing Matrices
----------------

.. toctree::
   :maxdepth: 1

   tutorials/sensing_matrix_diagonalization
   tutorials/optical_lever_sensing_matrices

Foton Utilities
---------------

.. toctree::
   :maxdepth: 1

   tutorials/tf2foton

Ezca Utilities
--------------

.. toctree::
   :maxdepth: 1

   tutorials/ezca_get_put_matrices

Curve Fitting
-------------

.. toctree::
   :maxdepth: 1

   tutorials/curve_fitting
   tutorials/curve_fitting_transfer_function
   tutorials/curve_fitting_simple_zpk
   tutorials/curve_fitting_complex_zpk
   tutorials/curve_fitting_lvdt_and_geophone_noise

Control Regulator Design
------------------------

.. toctree::
   :maxdepth: 1

   tutorials/regulator_feedback_critical_damping
   tutorials/regulator_algorithmic_oscillator_control
   tutorials/regulator_post_filtering

Dynamic Mode Decomposition
--------------------------

.. toctree::
   :maxdepth: 1

   tutorials/dmd_time_series_prediction
