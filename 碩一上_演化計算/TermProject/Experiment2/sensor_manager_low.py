import random
import time

# 初始化center_need_charge字典
center_need_charge = {}
sensor_need_charge = []


class Sensor:
    MaxBattery = 128  # 最大電池容量: 108J
    consumption_rate = 0.005  # 每秒消耗的電量: 30mJ 之後須調整為10mJ - 50mJ random
    thresholdLowerBound = MaxBattery * 0.6
    last_update_time = None  # 上次更新的時間
    C2 = 0.02

    def __init__(self, x, y, r, ang, index):
        self.x = x
        self.y = y

        self.capacity = random.randint(int(Sensor.MaxBattery * 0.1), int(Sensor.MaxBattery * 0.8))
        self.last_update_time = time.time()  # 初始化上次更新時間為當前時間
        self.index = index  # sensor的索引
        self.center_index = None  # 中心點的索引
        self.thresholdLowerBound = Sensor.thresholdLowerBound

        # 检查是否需要充电
        if self.capacity < self.thresholdLowerBound and self.index not in sensor_need_charge:
            # 將該sensor所屬的中心點索引加入於center_need_charge字典中
            sensor_need_charge.append(self.index)
        if self.capacity >= self.MaxBattery:
            # 將該sensor移出sensor_need_charge字典中
            if self.center_index in sensor_need_charge:
                sensor_need_charge.remove(self.index)


class PowerStation:
    def __init__(self):
        print("=Set PowerStation=")
        self.x = 0
        self.y = 0
        self.tr_angle = 90
        print(self.x, self.y)


class BatteryCar:
    def __init__(self):
        print("Set Car")
        self.capacity = 4000 * 1000  # capacity: 4000kJ
        self.moving_cost = 50  # moving_cost: 50J/m
        self.x = 0
        self.y = 0
        self.moving = False


ap = PowerStation()
numbPoints = 200  # 設備數量
x = []
y = []
sensor = []


for i in range(numbPoints):
    x.append(random.uniform(-200.0, 200.0))
    y.append(random.uniform(-200.0, 200.0))

for i in range(numbPoints):
    sensor.append(Sensor(x[i], y[i], -1, 0, i))


