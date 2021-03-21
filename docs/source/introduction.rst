Introduction
============

Kontrol (also pronounced "control") is a python package for KAGRA control system
related work. It is intented for both offline and real-time (via Ezca and maybe
diaggui and nds2 later) usage. In principle, it should cover all control related topics
ranging from sensor/actuator diagonalization to system identification and
control filter design.

Major Features
--------------
* Complementary filter synthesis using :math:`\mathcal{H}_\infty`.
  * Synthesize optimal complementary filters in a 2-sensor configuration.
  * Only depends on sensor noises.
  * No specifications required.

Other Features
--------------
* filter: Complementary filter definitions and optimization.
* model: Sensor noise models, fitting, noise to zpk regression.
* utils: quadrature sum, 2-norm, rms
* controlutils: transfer function matrix to MIMO tf, zpk
  transfer function definition.
* visutils: VIS utility functions, actuator diagonalization, sensor correction
  gain finding
* sensact: rediagonalization of actuation/sensing matrices given coupling
  matrix.
