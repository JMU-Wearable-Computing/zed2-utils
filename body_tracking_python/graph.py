import matplotlib.pyplot as plt
import csv
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import imageio
import math

with open(sys.argv[1]) as file:
    entries = csv.reader(file, delimiter = ' ')

    x, y, z = [], [], []
    for entry in entries:
        if len(entry) == 0:
            break
        print(entry)
        x.append(float(entry[0]))
        y.append(float(entry[1]))
        z.append(float(entry[2]))


plt.plot(range(0, len(x)), x, 'r-', label='x')
plt.xticks(rotation = 25)
plt.xlabel('sample index')
plt.ylabel('x position (m)')
plt.grid()
plt.legend()
plt.show()
