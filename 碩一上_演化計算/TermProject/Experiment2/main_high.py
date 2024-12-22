import random
random.seed(1234)

import matplotlib.pyplot as plt
import numpy as np
from sensor_manager_high import sensor, sensor_need_charge, BatteryCar
from GACS import GA


deadGA1, deadGA2, deadGA3, deadGA4 = 0, 0, 0, 0
bcGA1, bcGA2, bcGA3, bcGA4 = BatteryCar(), BatteryCar(), BatteryCar(), BatteryCar()

Glist = GA(sensor_need_charge, sensor, bcGA1, crossover_idx=0)
np.save(f'crossover1_high.npy', np.asarray(Glist))

Glist2 = GA(sensor_need_charge, sensor, bcGA2, crossover_idx=1)
np.save(f'crossover2_high.npy', np.asarray(Glist2))

Glist3 = GA(sensor_need_charge, sensor, bcGA3, crossover_idx=2)
np.save(f'crossover3_high.npy', np.asarray(Glist3))

Glist4 = GA(sensor_need_charge, sensor, bcGA4, crossover_idx=3)
np.save(f'crossover4_high.npy', np.asarray(Glist4))

x = list(range(len(Glist)))
plt.figure()

plt.plot(x, Glist, label='crossover1_high', marker='.')
plt.plot(x, Glist2, label='crossover2_high', marker='.')
plt.plot(x, Glist3, label='crossover3_high', marker='.')
plt.plot(x, Glist4, label='crossover4_high', marker='.')

plt.xlabel('iteration')
plt.ylabel('Dead Node')
plt.legend()
plt.show()
