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

.. toctree::
   :maxdepth: 4

   Basic Suspension Commissioning
   Advanced Control Methods

Basic Suspension Commissioning
------------------------------
We were asking to set up the active control system for a stage,
particularly, the inverted pendulum stage, of the suspension in KAGRA.
Ultimately, the goal is to obtain a controller that can be used
for active damping and positon control.
We'll go through the necessary steps to achieve so using the
``Kontrol`` package.
Information about the suspension will be given along the way as necessary.


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

Transfer function modeling
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
:ref:`Inertial Sensor Calibration`.
Here, instead of defining the model, we can use the predefined
``kontrol.curvefit.ComplexZPK`` class as the model.
We can fit the frequency response 2 ways, with or without an initial guess.
Click the links below to see how the frequency response can be fitted.

.. toctree::
   :maxdepth: 1

   ./tutorials/system_modeling/transfer_function_modeling_without_guess
   ./tutorials/system_modeling/transfer_function_modeling_with_guess

Using kontrol, we obtained a transfer function of the system:

.. math::

   \frac{0.635s^4+0.1785s^3+14.91s^2+1.626s+56.65}{s^6+0.5719s^5+49.55s^4+11.48s^3+396.7s^2+17.01s+55.2}\,

and we've used ``kontrol.TransferFunction.save()`` method to export the
transfer function object for future purposes.

Hint:

- Without the initial guess, the parameter space must be bounded.
  There's no guarantee that the solution coverged to a global optimum.
  We've to use a differnt random number seed and many trials to obtain
  satisfactory results.
- With the initial guess, the fit refines the initial parameters without
  iterations. However, it could require experience to obtain an initial guess.


Controller design
^^^^^^^^^^^^^^^^^
With the transfer function of the system identified,
we can start designing a controller for damping and position control
purposes.
In this section, we will use the plant identified in
:ref:`Transfer function modeling` and create controllers around it.

Damping control
***************
We were asked to design a damping controller for the suspension.
The resonances of the system are annoying since they amplify ground motion.
And, when responding to an impulse input, the oscilaltion takes a long time
to be naturally damped.

The goal is to design a damping controller to suppress the suspension motion
quickly after being hit by an impulse.
We also need an additional 4th-order low-pass filter to reduce the noise
being injected at high frequency and maybe notch filters maintain stability.
Click the link below to see how we can use the ``kontrol.regulator``
module to design the appropriate controllers.

.. toctree::
   :maxdepth: 1

   ../tutorials/controller_design/damping_control

We've used ``kontrol.load_transfer_function()`` to import the transfer
function we've saved before.
Using ``kontrol.regulator.oscillator.pid()`` and
``kontrol.regulator.post_filter.post_low_pass()`` functions, we obtained
a damping controller

.. math::
   K(s) = \frac{1.018\times 10^7s}{s^4+149.8s^3+2.102\times 10^5s + 1.968\times 10^6}\,,

which critically damps the system.

The controller seems to be able to damp the system reasonable well and
we decided to export the Foton string by converting the controller
into a ``kontrol.TransferFunction`` object and use
``kontrol.TransferFunction.foton()`` method to export the Foton string.

.. code:: Python

   zpk([-0],[5.960099+i*0.001106;5.960099+i*-0.001106;5.962312+i*0.001107;5.962312+i*-0.001107],32.5136,"n")


Position control
****************
While the suspension is being actively damped, this is not enough.
For some degrees of freedom, we want be able to control the system to
follow a setpoint.
After all, the suspension hangs the mirror and provides coarse alignment
control.
We were ask to design another controller that provides both position
and damping control.
In addition, we received complaints from others saying that the damping
control inject too much noise at high frequencies.
We were also told that we don't need to damp the higher-frequency modes
so the cut-off frequency of the low-pass can be lowered so we can reduce
injected noise.
Click the link below to see how can use the ``kontrol.regulator`` module
to achieve all the above.

.. toctree::
   :maxdepth: 1
   
   ../tutorials/controller_design/position_control

And we eventually obtained a controller.
The open-loop transfer function has a unit gain frequency of 0.128 Hz and
phase margin of 45 degrees.
The gain at 10 Hz is 2 orders of magnitude than the one we obtained in
:ref:`Damping control`.
It follows that the noise injected is also that much lower.
From simulation, the system is able to trace a unit step input without
excess oscillation.
We're happy with the results and exported the final controller.

.. code:: Python

   zpk([0.012454+i*0.024317;0.012454+i*-0.024317;0.012652+i*0.499616;0.012652+i*-0.499616;0.025355+i*0.999705;0.025355+i*-0.999705],[-0;0.249888+i*0.432819;0.249888+i*-0.432819;0.500013+i*0.866048;0.500013+i*-0.866048;1.887186+i*0.000255;1.887186+i*-0.000255;1.887697+i*0.000256;1.887697+i*-0.000256],0.024269,"n")


And, this concludes the basic suspension commissioning section:
We're able to setup the sensors and actuators to measure the frequency
response of the system.
We also modeled the frequency response of the system and contructed
2 types of controllers for it.

But, we're not satisfied. In the :ref:`Advanced Control Method` section,
we will continue working on  advanced techniques to further improve the
active control performance.


Advanced Control Method
-----------------------

Sensor fusion
^^^^^^^^^^^^^
There're two types of sensors that are used to measure the motion
of the inverted pendulum, relative sensor and inertial sensor.
The two sensors have different noise characteristics, one has better noise
performance at some frequencies and the other one is better at other
frequencies.
We were asked to design a set of complementary filters which can be
use to combine the two sensors so we can "select" which sensor to use
at different frequencies.

Estimating inertial sensor noise using correlation methods
**********************************************************

Sensor noise modeling
*********************

Complementary filter synthesis using H-infinity methods
*******************************************************


General Utilities
-----------------

