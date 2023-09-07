Tutorials
=========
This tutorial is mainly divided into two parts,
:ref:`Basic Suspension Commissioning` and :ref:`Advanced Control Methods`.
There's an extra section called :ref:`General Utilites` and there you will
find miscellaneous tools that are generally useful.

In the first part, the commissioning of the active control system for
a stage of a virtual suspension with 3 degrees of freedom is demonstrated.
This covers topics including: sensor
calibration, sensing matrices, system modeling, and controller design.
By the end of the first part, users should be able
to commission suspensions to achieve basic damping and position control
with appropriate filtering.

The second part of the tutorial covers
specialized frontier control topics for seismic isolation that
are not considered standard.
This section is not compulsory for suspension commissioning.
The content in this section is everchanging and being updated
as new methods are being developed and coded into Kontrol.

Each subsection solves a small problem and contributes to a small step
towards solving the bigger problem, e.g. suspension commissioning and
control optimization.
You will find a general description giving context for
the small problem in each subsection.
And you will find a link to the Jupyter notebook containing
the solution for the problem.

Each Jupyter notebook is structured similarly as follows.
All notebooks begins with  preparing and visualizing the mock measurements
that we will be processing.
In reality, the data will be measured instead of generated.
With the measurement data obtained, we will proceed to demonstrate
the use of the ``Kontrol`` package to solve the underlying problems.
At last, we will export the results in some way for further usages, e.g.
for further processes or implementation.
This way, the notebooks can be thought as a process in a data pipeline.

The style of this tutorial is inspired from the actual commissioning
of a KAGRA suspension.
As in, these are all the necessary steps that we need to go through
when setting up the active isolation systems.
Therefore, the notebooks can be easily modified for actual usage
simply by replacing the data.


Content

#. :ref:`Basic Suspension Commissioning`

   #. :ref:`Sensors and actuators`

      #. :ref:`Linear sensor calibration`

      #. :ref:`Inertial sensor calibration`

      #. :ref:`Sensing matrices`

      #. :ref:`Actuation matrices`
   
   #. :ref:`System modeling`

      #. :ref:`Transfer function modeling`

   #. :ref:`Controller design`

      #. :ref:`Damping control`

      #. :ref:`Position control`

#. :ref:`Advanced Control Methods`

   #. :ref:`H-infinity sensor fusion`

      #. :ref:`Estimating inertial sensor noise`

      #. :ref:`Sensor noise modeling`

      #. :ref:`Complementary filter synthesis`

   #. :ref:`H-infinity sensor correction`

      #. :ref:`Seismic noise spectrum modification and modeling`
               
      #. :ref:`Sensor correction filter synthesis`

      #. :ref:`Sensor fusion and optimal controller (just words)`

#. :ref:`General Utilities`


Kontrol has more than what's covered in the tutorials.
Be sure to check out the :ref:`Kontrol API`
section for detailed documentation.


Basic Suspension Commissioning
------------------------------
We were asking to set up the active control system for a stage,
particularly, the inverted pendulum stage, of the suspension in KAGRA.
Ultimately, the goal is to obtain a controller that can be used
for active damping and positon control.
We'll go through the necessary steps to achieve so using the
``Kontrol`` package.
Information about the suspension will be given along the way as necessary.

This section closely follows Chapter 6 in Ref. [1]_.
Check the reference out if you wish to understand what the
functions/methods are actually doing in the background.


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

To install the calibration filter to the KAGRA digital system,
we have obtained a Foton string of the calibration filter
using the ``kontrol.TransferFunction`` class:

.. code:: Python

   zpk([0.705852+i*0.707336;0.705852+i*-0.707336],[-0;-0],0.667203,"n")

With this filter, we can start measuring velocity with the geophone.
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
   -0.333 & -0.333 &  0.666\\
   0.577 & -0.577 & 0.\\
   0.333 &  0.333 &  0.333
   \end{pmatrix}\,,

such that :math:`\vec{x} \approx \mathbf{A}\vec{y}`.
With high hopes we installed this matrix into the digital system,
hoping to measure the crisp distinguishable 0.06, 0.1, 0.2 Hz resonances
in the :math:`\vec{x}=(x_1, x_2, x_3)` degrees of freedom measurement.
However, you inspect the readouts and discovered cross-coupling between
the three degrees of freedom, i.e. sensing matrix is not perfect.

The goal is to refine the sensing matrix to
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
   -0.346 & -0.301 &  0.676\\
   0.569 & -0.585 & -0.00830\\
   0.313 &  0.334 &  0.353
   \end{pmatrix}\,,

that aligns the sensors to the control basis.

To obtain or install the matrix to the digital system,
we can define a ``kontrol.ezca.Ezca`` instance and
use the ``get_matrix()`` or ``put_matrix()`` methods.


*Caveats*

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

Tips:

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
   
   ./tutorials/controller_design/position_control

And we eventually obtained a controller.
The open-loop transfer function has a unit gain frequency of 0.128 Hz and
phase margin of 45 degrees.
The gain at 10 Hz is 2 orders of magnitude lower than the one we obtained in
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

But, we're not satisfied. In the :ref:`Advanced Control Methods` section,
we will continue working on  advanced techniques to further improve the
active control performance.


Advanced Control Methods
------------------------

**H-infinity method**

We were asked to improve the seismic isolation performance.
The system that we set up using the methods above don't help mitigating seismic
noise since we were only using relative sensors.
We cannot achieve active seismic isolation without utilizing inertial sensors.

There are several things that we can do to achieve active isolation and
in some sense optimize it.
Chapter 7 and 8 in Ref. [1]_ describe several concepts in seismic isolation:
sensor fusion, sensor correction, and feedback control,
and propose an H-infinity method to optimize these subsystems in a
seismic isolation system.


H-infinity sensor fusion
^^^^^^^^^^^^^^^^^^^^^^^^
There're two types of sensors that are used to measure the motion
of the inverted pendulum, relative sensor and inertial sensor.
The two sensors have different noise characteristics, one has better noise
performance at some frequencies and the other one is better at other
frequencies.
We were asked to design a set of complementary filters which can be
used to combine the two sensors into a "super sensor" that has the
advantages of both sensors.

``Kontrol`` provides an H-infinity approach to optimize complementary filters.
To use this, we'll need 2 things.

1. Spectrums of the sensor noises.
2. Transfer functions that have magnitude responses matching the spectrums
   of the noises.

In this section, we'll demonstrate how we can use Kontrol to optimize
complementary filters using the H-infinity method.
The first two subsections show how we can obtain the necessary materials
mentioned above and the last subsection shows how we can obtain
the optimal complementary filters given those materials.

We also assume that the relative sensor and the inertial sensor are
aligned and inter-calibrated so they read the same signal.
**This is extremely important**.


*Caveats*

This section solves the sensor fusion problem using the H-infinity method.
The case presented is a hypothetical scenario as we only take the intrinsic
sensor noises of the relative and inertial sensors into account, whereas
there're more noises involved in reality.
Doing so allows the demonstration to be simplified without much complications.
So, please keep in mind that this section only serves the purpose of laying
down the necessary procedures to use the method.
Therefore, if you wish to use this method, do take into account all necessary
noise sources in the sensors.

In some systems, the relative sensors are "corrected" via a control scheme
called "sensor correction" and it is the corrected relative sensor that
is combined with the inertial sensor.
The corrected sensor has a noise profile depending on the sensor correction
filter that we will be optimizing in the next section
:ref:`H-infinity sensor correction`.
But because the sensor correction and other problems can be treated
as a sensor fusion problem, it is beneficial to show how a
sensor fusion problem is solved before going into other problems.
This is why we begin with a hypotheical sensor fusion scenario.

The correct procedure is:

#. Firstly optimize a sensor correction filter.

#. Evalute the effective noise presence in the corrected relative readout.

#. Model and use that to optimize the complementary filters instead.


Estimating inertial sensor noise
********************************
Sensor noise of an inertial sensor cannot be measured individually
because there's always some signal that is present in the readout.
However, if we have multiple sensors measuring a common signal,
we can use the 3-channel correlation method to estimate all individual
sensor noises of the 3 sensors.

We placed 3 inertial sensors on the ground and aligned them so they
measure the ground motion in the same direction.
Click the link below to see how we can use the
``kontrol.spectral.three_channel_correlation()`` function to
estimate the sensor noises from the spectrums.

.. toctree::
   :maxdepth: 1

   ./tutorials/sensor_fusion/three_channel_correlation_method

And, we were able to generate an estimation of the inertial sensor noise
spectrum.
And we've exported the noise spectrums for future usages.


Sensor noise modeling
*********************
Now that the sensor noises are identified, we can construct transfer function
models for them.
The ``kontrol.curvefit.TransferFunctionFit`` class that we used earlier
for modeling frequency response data can be used for this purpose.
But, there's a wrapper function that is
better fitted for our purpose as it's not nearly as tedious.
See the notebook below to see how we can use
the ``kontrol.curvefit.spectrum_fit()`` function to model spectrums as the
magnitude responses of transfer functions.

.. toctree::
   :maxdepth: 1

   ./tutorials/sensor_fusion/sensor_noise_modeling

In the tutorial, we have fitted empirical models to the noise data
as an optional intermediate step.
With the empirical models obtained, we can rescale the frequency axis to
logspace with fewer data points, which helped speeding up the final modeling.
It also allows us to flatten the spectrums at both ends, which is necessary
for the H-infinity method.
In the end, we've obtained 2 ``kontrol.TransferFunction`` objects
which have magnitude responses matching the relative and inertial sensor noise
spectrums.
We've also exported those transfer function models for future usages.

Tips:

- ``kontrol.curvefit.spectrum_fit()`` requires user to specify the number
  of zeros and poles, or the order of the transfer function.
  To obtain a reasonable number, a general rule of thumb is to run it
  multiple times with increasing order until there's pole-zero cancellation
  or when excess poles and zeros leak out of the frequency band of interest.


Complementary filter synthesis
******************************
With the transfer function models of the noise spectrums obtained,
we can finally create complementary filters using the
``kontrol.ComplementaryFilter`` class.
The transfer function models we obtained are specified as
``kontrol.ComplementaryFilter.noise1`` and
``kontrol.ComplementaryFilter.noise2`` attributes.
And, to make the optimization meaningful, we need to specify
the inverse of the target attenuation of the noises as
``kontrol.ComplementaryFilter.weight1`` and
``kontrol.ComplementaryFilter.weight2`` attributes.
Conveniently, we don't need to do extra work because the noise models
themselves can be used.
Click the link below to see what it means exactly.

.. toctree::
   :maxdepth: 1

   ./tutorials/sensor_fusion/complementary_filter_synthesis

And, we've obtained 2 complementary filters which solve the sensor fusion
problem in such a way the super sensor noise are minimum at
all frequencies with respect to the lower boundary.
We've also exported the Foton string using the
``kontrol.TransferFunction.foton()`` method so we can implement the filters
into the digital control system.
We've also encountered some practical issues that might occur and
they are listed below as tips.

Tips

- Complementary filters generated by the
  ``kontrol.ComplementaryFilter.hinfsynthesis()`` method may contain
  meaningless coefficients. It's important to get rid of them as they
  will show as astronomically high-frequecy zeros/poles,
  that cannot be implemented in a digital system.
- Because of the way H-infinty method (or rather, most methods) works,
  the noise models we specified have flat ends. This means the filters
  do no have the necessary features to properly roll-off the noises beyond
  the frequency band of interest. We can add prefilters to fix the problem
  but this may require some tweaking.
- Sometimes the synthesis method can produce filters that make no sense.
  Interchanging the relative and inertial sensor noises (and weights) may
  solve the issue.


H-infinity sensor correction
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Relative sensors are seismic noise-coupled so they inject seismic noise
to the isolation platform under feedback control.
We have a seismometer on the ground that measures the ground motion
close to the isolation platform and we can use that to reduce the
seismic noise coupling in the relative sensors.
This is simply done by subtracting the seismometer readout from the
relative readout, thereby "correcting" the relative sensors.
However, doing so injects seismometer noise to the relative readout.
Therefore, we have to design a "sensor correction filter" to filter
excessive noise while retaining seismic signal for sensor correction.

In :ref:`H-infinity sensor fusion`, we have used
the ``kontrol.ComplementaryFilter`` class to optimize complementary filters
and we've successfully obtain a pair of complementary filters that can be
implemented.
It turns out that the sensor correction problem can be solved using the
very same class and methods.
Instead of complementary low-pass and high-pass filters, we'd be obtaining
a seismic transmissivity and a sensor correction filter, which are also
complementary.

The required procedure to optimize a sensor correction filter is very similar
to that already presented in section :ref:`H-infinity sensor fusion` so we
will not repeat what's already demonstrated.
Instead, we assume that we have already obtained

#. The transfer function model with magnitude response matching
   the noise spectrum of the relative sensor.

#. The same for the seismometer.

We will also need the seismic noise model but it turned out to be more
involved so we will demonstrate what needs to be done.
There's another notible difference between the sensor correction and the
sensor fusion problem.
The noise performance of the super sensor in a sensor fusion problem is
completely dependent on the filtered sensor noises.
In sensor correction, the corrected relative sensor is dependent on the
filtered seismometer noise and filtered the seismic noise but is also
dependent on the unfiltered intrinsic relative sensor noise.
The intrinsic relative sensor noise acts as an ambient noise and we shall
see how this can be utilized in the optimization.


Seismic noise spectrum modification and modeling
************************************************
We read Chapter 8.3.3 in Ref. [1]_ and realized we need to modify the seismic
noise spectrum before modeling it.
Otherwise the sensor correction filter might actually amplify the
seismometer noise and the seismic noise, instead of attenuating them.
Click the link below to see how we can obtain a proper seismic noise model
for the optimization purpose.

.. toctree::
   :maxdepth: 1

   ./tutorials/sensor_correction/seismic_noise_spectrum_modification_and_modeling

And we've obtained a seismic noise model that has a flat spectrum above
the secondary microseism.
The reasons behind this are rather involved and the explanation can be found
in the references.
But in simple words, the main reasons we had to do this are because

#. Make the sensor correction filter a high-pass filter.
#. So the sensor correction filter won't amplify any seismometer and seismic
   noise below the relative sensor noise level.

Again, this model is not a representation for the seismic noise.
It is created for the sole purpose of H-infinity optimization.


Sensor correction filter synthesis
**********************************
With all the necessary components obtained, we can use
``kontrol.ComplementaryFilter`` again to optimize, not complementary filters,
but the sensor correction filter.
Instead of specifying two sensor noise models to the ``ComplementaryFilter``
instance, we specify the seismic noise model and the seismometer noise model.
The prescense of the relative sensor noise changes how we specify the
target attenuation (weights) as the lower boundary of the 
corrected sensor noise depends on it.
Click the link below to see how we cope with that and optimize
a sensor correction filter.

.. toctree::
   :maxdepth: 1

   ./tutorials/sensor_correction/sensor_correction_filter_synthesis

Using the ``kontrol.ComplementaryFilter.hinfsynthesis()`` method,
we were able to obtain a sensor correction filter.
We have also computed the expected noise spectrum of the corrected relative
sensor.
It has suppressed seismic coupling, particularly around the secondary
microseism.
However, seismometer noise is injected at lower frequencies, which is expected.
To justify the tradeoff, we compared the noise RMS of the seismic noise
(uncorrected relative sensor) and the corrected relative sensor.
And, we found that we've indeed reduced the noise RMS of the relative sensor
with the sensor correction scheme and the H-infinity optimal filter.


Sensor fusion and optimal controller (just words)
*************************************************
For here, to finally complete the job, the next step would be to model the
noise of the corrected relative sensor and use what we've learnt in
:ref:`H-infinity sensor fusion` to optimize the sensor fusion of
the corrected relative sensor and the inertial sensor.
We'll just leave it here so we don't repeat.

The controller that we designed in the :ref:`Controller design` section
utilizes concepts like critical damping and phase margins to design a
controller to achieve position and damping control.
However, this is not optimal for active seismic noise isolation.
In principle, we want a controller that has higher gain where
the seismic disturbnce is high, and lower gain where control noise becomes
dominated.
This turns out to be also a sensor fusion problem as disturbance and noise
couplings are also complementary.
The controller can be easily optimized for active isolation using
a ``kontrol.ComplementaryFilter`` instance.
The optimized result would be the sensitivity function and the
complementary sensitivity function, which can be used
to derive the optimal controller.
Chapter 8.2.3 and 8.3.6 in Ref. [1]_ provides examples of how feedback
controllers can be optimized for seismic isolation so check it out if
you're interested.


General Utilities
-----------------

Coming soon.

**References**

.. [1]
   Terrence Tak Lun Tsang. Optimizing Active Vibration Isolation Systems in
   Ground-Based Interferometric Gravitational-Wave Detectors.
   https://gwdoc.icrr.u-tokyo.ac.jp/cgi-bin/DocDB/ShowDocument?docid=14296
