import matplotlib.pyplot as plt
import numpy
import numpy as np
import random
import copy
import math

# GA
NP = 100  # 族群數量
low = 0
up = 100
PrC = 0.9
PrM = 0.04
gen = 100  # 迭代數
Gbest = []  # 最佳解
GbestX = []
CarSpeed = 1
ChargingRate = 3.4


def fitness_function(sensor, path, bc):
    num_zero_capacity = 0
    car_position = [bc.x, bc.y]
    for stop in path:
        # 充電車移動到充電站
        distance_to_station = math.sqrt(
            (car_position[0] - sensor[stop].x) ** 2 + (car_position[1] - sensor[stop].y) ** 2)
        time_to_station = distance_to_station / CarSpeed

        # 更新所有 sensor 電量
        for s in sensor:
            s.capacity -= time_to_station * s.consumption_rate
            s.capacity = max(0, s.capacity)

        # 更新充電車位置
        car_position = [sensor[stop].x, sensor[stop].y]

        # 充電
        if (sensor[stop].capacity == 0): num_zero_capacity += 1
        time_to_Charge = (sensor[stop].MaxBattery - sensor[stop].capacity) / ChargingRate

        for s in sensor:
            s.capacity -= time_to_Charge * s.consumption_rate
            s.capacity = max(0, s.capacity)

        sensor[stop].capacity = sensor[stop].MaxBattery
        # print("time = ", time_to_station, "= ", time_to_Charge)

    return num_zero_capacity


def mutation(path):
    if random.random() < 0.2:
        new_path = copy.deepcopy(path[::-1])
    else:
        new_path = copy.deepcopy(path)
        swap_index = random.sample(range(len(path)), 2)
        new_path[swap_index[0]], new_path[swap_index[1]] = path[swap_index[1]], path[swap_index[0]]
    return new_path


def crossover_ero(sensor, chri, chrj):
    RL = [s.capacity / 0.03 for s in sensor]

    adj_list = {}
    for i, x in enumerate(chri):
        adj_list[x] = set()
        before = chri[(i - 1) % len(chri)]
        after = chri[(i + 1) % len(chri)]
        adj_list[x].add(before)
        adj_list[x].add(after)

    for i, x in enumerate(chrj):
        before = chrj[(i - 1) % len(chrj)]
        after = chrj[(i + 1) % len(chrj)]
        adj_list[x].add(before)
        adj_list[x].add(after)

    chro = []
    candidate = list(adj_list.keys())
    current_gene = min(candidate, key=lambda gene: RL[gene])
    chro.append(current_gene)

    while len(chro) < len(chri):
        neighbor = list(adj_list[current_gene])
        adj_list.pop(current_gene)
        for key, value in adj_list.items():
            if current_gene in list(value):
                adj_list[key].remove(current_gene)

        if len(neighbor) == 0:
            candidate = list(adj_list.keys())
            current_gene = min(candidate, key=lambda gene: RL[gene])

        else:
            min_neighbor = min([len(adj_list[gene]) for gene in neighbor])
            candidate = [gene for gene in neighbor if len(adj_list[gene]) == min_neighbor]
            current_gene = min(candidate, key=lambda gene: RL[gene])

        chro.append(current_gene)

    return chro


def ERO(sensor_need_charge, sensor, bc):
    D = len(sensor_need_charge)
    if len(sensor_need_charge) == 0:
        return
    global Gbest, GbestX
    print("Initial")
    print("維度=", D, "族群=", NP)

    X = []  # 初始化基因族群
    for i in range(NP):
        path = copy.deepcopy(sensor_need_charge)
        random.shuffle(path)
        gene = (path[0], fitness_function(copy.deepcopy(sensor), path, bc), path)  # gene = (nexthop, fitness, path)
        X.append(gene)

    X.sort(key=lambda x: x[1])
    for g in range(gen):
        print("迭代數:", g)
        for i in range(NP):
            # 選父代基因
            weight = [t[1] + 1 for t in X]  # 做一個+1的修正以免bug
            [chri, chrj] = random.choices(X, weight, k=2)
            index_chri = X.index(chri)
            index_chrj = X.index(chrj)

            if (random.random() < PrC):
                path = crossover_ero(sensor, list(chri[2]), list(chrj[2]))
                chro = (path[0], fitness_function(copy.deepcopy(sensor), path, bc), path)

                # 按照 fitness 值对元组进行排序，取前两个赋值给 chri, chrj
                sorted_tuples = sorted([chri, chrj, chro], key=lambda x: x[1])[:2]
                chri, chrj = sorted_tuples[0], sorted_tuples[1]

            if (random.random() < PrM):
                path = random.choice([chri[2], chrj[2]])
                path = mutation(path)
                chro = (path[0], fitness_function(copy.deepcopy(sensor), path, bc), path)

                # 按照 fitness 值对元组进行排序，取前两个赋值给 chri, chrj
                sorted_tuples = sorted([chri, chrj, chro], key=lambda x: x[1])[:2]
                chri, chrj = sorted_tuples[0], sorted_tuples[1]

            X[index_chri] = chri
            X[index_chrj] = chrj

        # 选择下一代族群中的最佳基因
        X.sort(key=lambda x: x[1])

        # 纪录最佳解
        Gbest.append(X[0][1])
        GbestX.append(X[0][2])

    print("lastGbest:", Gbest[gen - 1], '\n')
    return Gbest
