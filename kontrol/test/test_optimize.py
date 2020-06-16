from kontrol import (
                    quad_sum, complementary_sekiguchi,
                    complementary_modified_sekiguchi,
                    optimize_complementary_filter)
import numpy as np
import matplotlib.pyplot as plt
from control import *

f = np.linspace(1e-1,1e2,1000)  # Frequency axis
noise_low_pass1 = np.ones_like(f)  # LVDT-like noise
noise_low_pass2_tf = tf([(2*np.pi*2)**2],[1,2*np.pi*2/10,(2*np.pi*2)**2])
noise_low_pass2 = abs(noise_low_pass2_tf.horner(2*np.pi*1j*f)[0][0])  # Seismic-like noise
noise_low_pass = quad_sum(noise_low_pass1, noise_low_pass2)
noise_high_pass = 1/f**3.5  # Geophone-like noise
plt.figure()
plt.loglog(f, noise_low_pass, label='Noise to be low-passed')
plt.loglog(f, noise_high_pass, label='Noise to be high-passed')
plt.legend(loc=0)
plt.xlabel("Frequency")

# Using sekiguchi's filter
complementary_filter = complementary_sekiguchi
result = optimize_complementary_filter(filter_=complementary_filter,
                                      bounds=[(2*np.pi*min(f), 2*np.pi*max(f))],
                                      spectra=[noise_low_pass, noise_high_pass],
                                      f=f,
                                      )

plt.figure()

lpf_opt, hpf_opt = complementary_filter(result.x)  # In scipy.optimize.OptimizeResult, x is the attribute of be optimized parameters.
plt.subplot(231)
plt.loglog(f, abs(lpf_opt.horner(2*np.pi*1j*f)[0][0]), label='Complementary low-pass')
plt.loglog(f, abs(hpf_opt.horner(2*np.pi*1j*f)[0][0]), label='Complementary high-pass')
plt.legend(loc=0)
plt.xlabel("Frequency")
plt.title("1: Optimized Sekiguchi filter")
plt.grid(True)
sekiguchi_result = result

# Using the modified Sekiguchi filter with the above result as initial guess (use local minimization)
# This method should return the a suboptimal result using the modified filter.
complementary_filter = complementary_modified_sekiguchi
result = optimize_complementary_filter(filter_=complementary_filter,
#                                         bounds=[(2*np.pi*min(f), 2*np.pi*max(f))]*4,
                                        spectra=[noise_low_pass, noise_high_pass],
                                        f=f,
                                        x0=[sekiguchi_result.x[0]]*4)

lpf_opt, hpf_opt = complementary_filter(result.x)
plt.subplot(232)
plt.loglog(f, abs(lpf_opt.horner(2*np.pi*1j*f)[0][0]), label='Complementary low-pass')
plt.loglog(f, abs(hpf_opt.horner(2*np.pi*1j*f)[0][0]), label='Complementary high-pass')
plt.legend(loc=0)
plt.xlabel("Frequency")
plt.title("2: Locally Optimized modified Sekiguchi filter (Suboptimal)")
plt.grid(True)

# Using the modified Sekiguchi filter with the above result as initial guess but with boundaries (use global minimization)
# With global optimization method, sometimes this will be trapped in a local
# minima/boundary very far away from the true minima (see the last optimizaiton result).
# At other times, it will return the suboptimal (see the second optimization result).
# This is random because the global methods we are using have a stochastic nature.
complementary_filter = complementary_modified_sekiguchi
result = optimize_complementary_filter(filter_=complementary_filter,
                                        bounds=[(2*np.pi*min(f), 2*np.pi*max(f))]*4,
                                        spectra=[noise_low_pass, noise_high_pass],
                                        f=f,
                                        x0=[sekiguchi_result.x[0]]*4)

lpf_opt, hpf_opt = complementary_filter(result.x)
plt.subplot(233)
plt.loglog(f, abs(lpf_opt.horner(2*np.pi*1j*f)[0][0]), label='Complementary low-pass')
plt.loglog(f, abs(hpf_opt.horner(2*np.pi*1j*f)[0][0]), label='Complementary high-pass')
plt.legend(loc=0)
plt.xlabel("Frequency")
plt.title("3: Globally optimized modified Sekiguchi filter (fail/subopt.)")
plt.grid(True)

# Using the modified Sekiguchi filter directly without initial guess
# Most of the time this procedure will trap in local minima or boundary.
result = optimize_complementary_filter(filter_=complementary_modified_sekiguchi,
                                        bounds=[(2*np.pi*min(f), 2*np.pi*max(f))]*4,
                                        spectra=[noise_low_pass, noise_high_pass],
                                        f=f,
                                        x0=None)

lpf_opt, hpf_opt = complementary_filter(result.x)
plt.subplot(234)
plt.loglog(f, abs(lpf_opt.horner(2*np.pi*1j*f)[0][0]), label='Complementary low-pass')
plt.loglog(f, abs(hpf_opt.horner(2*np.pi*1j*f)[0][0]), label='Complementary high-pass')
plt.legend(loc=0)
plt.xlabel("Frequency")
plt.title("4: Globally optimized modified Sekiguchi filter (fail)")
plt.grid(True)

# Using the modified Sekiguchi filter with the sekiguchi filter at 1 Hz
# as initial guess (use local minimization)
# This method should return the an optimal (should be optimal) result using the modified filter.
complementary_filter = complementary_modified_sekiguchi
result = optimize_complementary_filter(filter_=complementary_filter,
                                        # bounds=[(2*np.pi*min(f), 2*np.pi*max(f))]*4,
                                        spectra=[noise_low_pass, noise_high_pass],
                                        f=f,
                                        x0=[1*2*np.pi]*4)

lpf_opt, hpf_opt = complementary_filter(result.x)
plt.subplot(235)
plt.loglog(f, abs(lpf_opt.horner(2*np.pi*1j*f)[0][0]), label='Complementary low-pass')
plt.loglog(f, abs(hpf_opt.horner(2*np.pi*1j*f)[0][0]), label='Complementary high-pass')
plt.legend(loc=0)
plt.xlabel("Frequency")
plt.title("5: Locally Optimized modified Sekiguchi filter (best)")
plt.grid(True)

# Using the modified Sekiguchi filter with the sekiguchi filter at 1 Hz
# as initial guess (use global minimization)
# This method should also return the an optimal (should be optimal) result using the modified filter.
# But this is slower. And, sometimes the optimization will also be trapped.
complementary_filter = complementary_modified_sekiguchi
result = optimize_complementary_filter(filter_=complementary_filter,
                                        bounds=[(2*np.pi*min(f), 2*np.pi*max(f))]*4,
                                        spectra=[noise_low_pass, noise_high_pass],
                                        f=f,
                                        x0=[1*2*np.pi]*4)

lpf_opt, hpf_opt = complementary_filter(result.x)  # In scipy.optimize.OptimizeResult, x is the attribute of be optimized parameters.
plt.subplot(236)
plt.loglog(f, abs(lpf_opt.horner(2*np.pi*1j*f)[0][0]), label='Complementary low-pass')
plt.loglog(f, abs(hpf_opt.horner(2*np.pi*1j*f)[0][0]), label='Complementary high-pass')
plt.legend(loc=0)
plt.xlabel("Frequency")
plt.title("6: Globally Optimized modified Sekiguchi filter (fail/best)")
plt.grid(True)

print("Here is how to print the filter")
print(lpf_opt)
print(hpf_opt)

plt.show()
