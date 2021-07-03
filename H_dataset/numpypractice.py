import numpy as np
a = 1 + 2j
b = np.mean(abs(a**2))
# b = np.concatenate((np.real(a), np.imag(a)))
print(b)
