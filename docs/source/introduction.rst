Introduction
============

Kontrol (also pronounced "control") is a python package for KAGRA control system
related work. It is intented for both offline and real-time (via Ezca and maybe
diaggui and nds2 later) usage. In principle, it should cover all control related topics
ranging from sensor/actuator diagonalization to system identification and
control filter design.

Features
--------
* Complementary filter synthesis using :math:`\mathcal{H}_\infty`.

  * Synthesize optimal complementary filters in a 2-sensor configuration.
  * Only depends on sensor noises.
  * No specifications required.

* Frequency series modeling.

  * Model-based empirical fitting.
  * Model frequency series as zero-pole-gain and transfer function models.
