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
 
The transfer function for :math:`x_2` has the same form as that of :math:`x_1`
but with different frequencies and Q values.

The objective here is to achieve a resonable damping and position control
for these three degress of freedom.

Sensors and actuators
^^^^^^^^^^^^^^^^^^^^^
The first step is to set up the sensors and actuators for the
active isolation system.
Without sensors and actuators, there's no control.
The goal here is to set up the sensors and actuators such that
we can use them to obtain a measurement of the frequency response of the
system that we want to control.
To achieve this, we need to

1. Calibrate the sensors so they meausre physical units.
2. Align the sensors (and actuators, using control matrices)
   so we get a readout in the control basis.

Linear sensor calibration
*************************
We were told to calibrate a relative displacement sensor for the
suspension.
We took a caliper and measured the actual displacement while recording
the sensor output.
We scanned the displacement from -10 to 10 mm with 1 mm interval and
data below is what we got.

.. code:: Python

   displacement = [-10., -9, -8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 8, 9, 10]  # millimeters

and 

.. code:: Python

   output = [-32765., -32760, -32741, -32680, -32504, -32060, -31068, -29109, -25691, -20421, -13241, -4596, 4598, 13243, 20423, 25693, 29111, 31070, 32062, 32506, 32682]

The goal is to obtain a value that converts the output to displacement.
Click the link below to see how we can use the
``kontrol.sensact.calibrate()`` function to obtain the calibration
factor.

.. toctree::
   :maxdepth: 1

   tutorials/sensors_and_actuators/calibration_of_a_linear_sensor

The calibration factor turned out to be 0.1195 microns per ADC count.


.. _inertial_sensor_calibration:

Inertial sensor calibration
***************************
We were told to calibrate an inertial sensor: the geophone.
The inertial sensor is different from a relative sensor because
it has a frequency response.
The transfer function (from velocity to output) of a geophone is given by

.. math::
   H(s) = G\frac{s^2}{s^2+\frac{\omega_n}{Q}s+\omega_n^2}\,,

where :math:`G`, :math:`\omega_n`, :math:`Q`, are the calibration
values we need to obtain.

We happened to have a spare calibrated seismometer so we can measure the
ground velocity.
We placed the geophone next to the seismometer and took a measurement
simultaneously.
The ratio between the geophone output and the seismometer output
happens to be the frequency response of :math:`H(s)`, which we can use
to obtain the calibration values.

The goal is to fit the frequency response with the transfer function model
:math:`H(s)` and click the link below to see how we can use
``kontrol.curvefit.TransferfunctionFit`` class to obtain the fit.

.. toctree::
   :maxdepth: 1

   tutorials/sensors_and_actuators/calibration_of_an_inertial_sensor

And we obtained a Foton string of the calibration filter
using the ``kontrol.TransferFunction`` class:

.. code:: Python

   zpk([0.705852+i*0.707336;0.705852+i*-0.707336],[-0;-0],0.667203,"n")

With this filter, we can start measure velocity with the geophone.
If we want displacement instead, we can simply add an integrator.


Sensing matrices
****************
With all the sensors calibrated, we can now read the motion of the
suspension.
However, the sensors are usually not placed in a way they aligned
perfectly with the basis that we are interested in.
As in, we get 3 readouts, :math:`\vec{y}=(y_1, y_2, y_3)`,
but we want to control in some basis :math:`\vec{x}=(x_1, x_2, x_3)`,
which is typically the Cartesian/Euler angle basis.

With some geometry and linear algebra, we were able to obtain
a (geometric) sensing matrix

.. math::

   \mathbf{A} =
   \begin{pmatrix}
   -0.33333333 & -0.33333333 &  0.66666667\\
   0.57735027 & -0.57735027 & 0.\\
   0.33333333 &  0.33333333 &  0.33333333
   \end{pmatrix}\,,

such that :math:`\vec{x} \approx \mathbf{A}\vec{y}`.
With high hopes we installed this matrix into the digital system,
hoping to measure the crisp distinguishable 0.06, 0.1, 0.2 Hz resonances
in the :math:`\vec{x}=(x_1, x_2, x_3)` degrees of freedom measurement.
However, you inspect the readouts and discovered cross-coupling between
the three degrees of freedom, i.e. sensing matrix is not perfect.

The goal is to fine tune the sensing matrix to
reduce the observable cross-couplings so the sensors are
aligned with the control basis.
Click the link below to see how we can use ``kontrol.sensact.SensingMatrix``
to obtain a new sensing matrix that aligns the sensors.

.. toctree::
   :maxdepth: 1

   tutorials/sensors_and_actuators/sensing_matrix_diagonalization

By identifying the cross-couplings between sensor channels,
we were able to obtain a new sensing matrix,

.. math::

   \mathbf{A}_\mathrm{new} =
   \begin{pmatrix}
   -0.34648554 & -0.30189757 &  0.67664218\\
   0.56999299 & -0.58521291 & -0.00830399\\
   0.31314695 &  0.33465657 &  0.35344143
   \end{pmatrix}\,,

that aligns the sensors to the control basis.

To obtain or install the matrix to the digital system,
we can define a ``kontrol.ezca.Ezca`` instance and
use the ``get_matrix()`` or ``put_matrix()`` methods.


**Caveats:**

- Sensor cross-coupling is only true when the phase is close to
  0 or 180 degrees.


Actuation matrices
******************
Like sensing matrices, the initial actuation matrices are obtained from
first principles using geometry.
However, the diagonalization of an actuation matrix is not as simple.
Ideally, we want the actuation in one degree of freedom to move the system
in that degree of freedom only.
However, most of the time, this won't happen with a diagonalization of
a scalar actuation matrix.
This is because the actuation cross-coupling is frequency dependent,
meaning that it would require a transfer matrix
(a matrix of transfer functions)
to fully decouple all degrees of freedom.

The proper way to approach this is to measure all non-diagonal
frequency responses from actuation to output, put them into matrix
form, invert it, and fit them using transfer functions.
This can be extremely tedious and fortunately unneccessary.
If all degrees of freedom are under the action of feedback control,
then the actuation cross-coupling will be suppressed.
If a diagonalization is required, refer to the transfer function modeling
section below.


System modeling
^^^^^^^^^^^^^^^
Now with the sensors and actuators set up, we can start characterizing
the system that we'd like to control.
The goal is to obtain a model of the system so we can eventually design
a controller for it.

Transfer Function modeling
**************************
Using the actuation in the :math:`x_1` direction, we excite
the system across all frequencies (using a white noise or sweep sine signal).
The suspension responded by moving in that direction at all frequencies.
We measured the magnitude and phase relative to the actuation signal.
This gives us the frequency response of the system,
which is simply the transfer function evaluated along the imaginary axis.

Modeling frequency with a transfer function can be challenging
due to numerical instability and large dynamic range.
Luckily, with a few assumptions, we can obtain a fit easily.
Experienced user can even obtain a reasonable fit without the use of
optimization.
This can be used as an initial guess for a local optimization.

The goal is to obtain a transfer function, which has frequency response
that matches the data that we obtained. We can use
``kontrol.curvefit.TransferFunctionFit`` class, like what we did in
:ref:`Inertial Sensor Calibration <_inertial_sensor_calibration>`_.
Here, instead of defining the model, we can use the predefined
``kontrol.curvefit.ComplexZPK`` class as the model.
We can fit the frequency response 2 ways, with or without an initial guess.
Click the links below to see how the frequency response can be fitted.

.. toctree::
   :maxdepth: 1

   ./tutorials/system_modeling/transfer_function_modeling_without_guess
   ./tutorials/system_modeling/transfer_function_modeling_with_guess

Without guess easier to use
with guess hard to use but can be more accurate.






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
