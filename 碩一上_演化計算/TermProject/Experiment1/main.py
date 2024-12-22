import numpy as np
import matplotlib.pyplot as plt
import copy
from sensor_manager import sensor, sensor_need_charge, BatteryCar
from GACS import GA
from GACS3 import GA3
from GACS2 import GA2
from ERO_RL import ERO


deadGA, deadGA2, deadGA3, deadERO = 0, 0, 0, 0
bcGA, bcGA2, bcGA3, bcERO = BatteryCar(), BatteryCar(), BatteryCar(), BatteryCar()



Glist = GA(sensor_need_charge, sensor, bcGA)
Glist2 = GA2(sensor_need_charge, sensor, bcGA2)
Glist3 = GA3(sensor_need_charge, sensor, bcGA3)
Glist4 = ERO(sensor_need_charge, sensor, bcERO)

x = list(range(len(Glist)))
x2 = list(range(len(Glist2)))
x3 = list(range(len(Glist3)))
x4 = list(range(len(Glist4)))
plt.figure()

plt.plot(x, Glist, label='GA', marker='.')
plt.plot(x, Glist2, label='GA2', marker='.')
plt.plot(x, Glist3, label='GA3', marker='.')
plt.plot(x, Glist4, label='ERO_RL', marker='.')


plt.xlabel('iteration')
plt.ylabel('Dead Node')
plt.legend()
plt.show()
