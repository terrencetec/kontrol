"""An example of complementary filter synthesis using H2 method.

Credits: Thomas Dehaeze https://tdehaeze.github.io/dehaeze20_optim_robus_compl_
filte/matlab/index.html
"""
from kontrol.filter import h2complementary
from kontrol import quad_sum
from control import tf
import numpy as np
from numpy import pi
import matplotlib.pyplot as plt

omegac = 100*2*pi; G0 = 1e-5; Ginf = 1e-4;
n1 = tf([Ginf/omegac, G0],[1/omegac, 1])*tf([1], [1/2/np.pi/100, 1])

omegac = 1*2*pi; G0 = 1e-3; Ginf = 1e-8;
n2 = tf([np.sqrt(Ginf)/omegac, np.sqrt(G0)],
        [1/omegac, 1])**2 * tf([1], [1/2/np.pi/4000, 1])**2

## I discovered that if both n1 and n2 are zero at frequency = inf, h2syn
## will not be able to find a solution, so I have to manually whiten one of
## them. In this case, n1 is the one to be filtered at higher frequencies,
## so it makes sense to whiten it instead of n2.

n1*=tf([1/(2*np.pi*1e4), 1],[1])

h1, h2 = h2complementary(n1, n2)
f = np.linspace(1e-1, 1e3, 10000)
h1_abs = abs(h1.horner(2*np.pi*1j*f)[0][0])
h2_abs = abs(h2.horner(2*np.pi*1j*f)[0][0])
n1_abs = abs(n1.horner(2*np.pi*1j*f)[0][0])
n2_abs = abs(n2.horner(2*np.pi*1j*f)[0][0])

n3 = quad_sum(h1_abs*n1_abs, h2_abs*n2_abs)

plt.subplot(121)
plt.loglog(f, n1_abs, label='Noise 1')
plt.loglog(f, n2_abs, label='Noise 2')
plt.loglog(f, n3, label='Fusioned')
plt.legend(loc=0)
plt.grid()
plt.ylabel('Magnitude')
plt.xlabel('Frequency (Hz)')

plt.subplot(122)
plt.loglog(f, h1_abs, label='h1')
plt.loglog(f, h2_abs, label='h2')
plt.legend(loc=0)
plt.grid()
plt.ylabel('Magnitude')
plt.xlabel('Frequency (Hz)')

plt.show()
