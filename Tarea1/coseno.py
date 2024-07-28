import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 2 * np.pi, 1000)
y = np.cos(x)
plt.plot(x, y)
plt.title("Gráfica de la función coseno")
plt.show()