import matplotlib.pyplot as plt
import numpy as np
import random
import copy
import math

# GA
NP = 300  # 族群數量
low = 0
up = 100
PrC = 0.9
PrM = 0.1
gen = 250  # 迭代數
Gbest = []  # 最佳解
GbestX = []
CarSpeed = 1
ChargingRate = 3.4


def box_muller():
    u1 = random.random()
    u2 = random.random()
    z0 = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
    return z0


def fitness_function(sensor, path, bc):
    num_zero_capacity = 0
    car_position = [bc.x, bc.y]
    for stop in path:
        # 充電車移動到充電站
        distance_to_station = math.sqrt((car_position[0] - sensor[stop].x) ** 2 + (car_position[1] - sensor[stop].y) ** 2)
        time_to_station = distance_to_station / CarSpeed
        
        # 更新所有 sensor 電量
        for s in sensor:
            s.capacity -= time_to_station * s.consumption_rate
            s.capacity = max(0, s.capacity)
            
        # 更新充電車位置
        car_position = [sensor[stop].x, sensor[stop].y]

        # 充電
        if sensor[stop].capacity == 0:
            num_zero_capacity += 1
        time_to_charge = (sensor[stop].MaxBattery - sensor[stop].capacity) / ChargingRate

        for s in sensor:
            s.capacity -= time_to_charge * s.consumption_rate
            s.capacity = max(0, s.capacity)

        sensor[stop].capacity = sensor[stop].MaxBattery
        # print("time = ", time_to_station, "= ", time_to_Charge)
        
    return num_zero_capacity


def crossover1(sensor, chri, chrj, K=0):
    chro = []
    RL = [s.capacity / 0.03 for s in sensor]
    while len(chri) > 0:
        if RL[chri[0]] <= RL[chrj[0]]:
            chosen_gene = chri[0]
        else:
            chosen_gene = chrj[0]
        chro.append(chosen_gene)
        chri.remove(chosen_gene)
        chrj.remove(chosen_gene)
    return chro


def crossover2(sensor, p1, p2, K=0):
    # Uniform Order Based Crossover (UOX)

    # STEP1 decide whether each gene should be changed
    # 1: not change, 0: change
    n = len(p1)
    u = np.random.choice([1, 0], size=n, p=[0.5, 0.5])
    u[0] = 1

    # STEP2
    # for those u[i]=1, child ck inherit the gene from parent pk
    # for those u[i]=0, fill in the gene in order from the other parent
    c1 = [p1[i] if u[i] == 1 else -1 for i in range(n)]
    c2 = [p2[i] if u[i] == 1 else -1 for i in range(n)]

    miss1 = [gene for gene in p2 if gene not in c1]
    miss2 = [gene for gene in p1 if gene not in c2]

    c1 = [gene if gene != -1 else miss1.pop(0) for gene in c1]
    c2 = [gene if gene != -1 else miss2.pop(0) for gene in c2]

    return c1, c2


def crossover3(sensor, parent1, parent2, K=0):
    priority_sorted_parent1 = sorted(parent1, key=lambda gene: sensor[gene].capacity)

    high_priority = priority_sorted_parent1[:K]

    child = []
    added = set()
    for gene in parent1:
        if gene in high_priority:
            child.append(gene)
            added.add(gene)

    for gene in parent2:
        if gene not in added:
            child.append(gene)
            added.add(gene)

    if len(child) < len(sensor):
        remaining_genes = [gene for gene in range(len(sensor)) if gene not in added]
        random.shuffle(remaining_genes)
        child.extend(remaining_genes)

    return child


def crossover4(sensor, chri, chrj, K=0):
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


# 初始化基因算法參數和初始族群
def GA(sensor_need_charge, sensor, bc, crossover_idx=0):
    crossover_method = [crossover1, crossover2, crossover3, crossover4]
    crossover = crossover_method[crossover_idx]

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

        # 設定動態的K值
        mean_K = 0.3 * len(sensor)
        sigma_K = 0.1 * len(sensor)
        z = box_muller()
        K = int(mean_K + sigma_K * z)
        K = max(1, min(K, len(sensor)))  # 確保K在[1, len(sensor)]之間

        for i in range(NP):
            # 選父代基因
            weight = [t[1] + 1 for t in X]     # 做一個+1的修正以免bug
            [chri, chrj] = random.choices(X, weight, k=2)
            index_chri = X.index(chri)
            index_chrj = X.index(chrj)
            
            if random.random() < PrC:
                if crossover_idx == 1:
                    path1, path2 = crossover(sensor, list(chri[2]), list(chrj[2]), K)
                    chro1 = (path1[0], fitness_function(copy.deepcopy(sensor), path1, bc), path1)
                    chro2 = (path2[0], fitness_function(copy.deepcopy(sensor), path2, bc), path2)
                    sorted_tuples = sorted([chri, chrj, chro1, chro2], key=lambda x: x[1])[:2]
                else:
                    path = crossover(sensor, list(chri[2]), list(chrj[2]), K)
                    chro = (path[0], fitness_function(copy.deepcopy(sensor), path, bc), path)
                    sorted_tuples = sorted([chri, chrj, chro], key=lambda x: x[1])[:2]

                chri, chrj = sorted_tuples[0], sorted_tuples[1]

            if random.random() < PrM:
                path = random.choice([chri[2], chrj[2]])
                swap_index = random.sample(range(len(path)), 2)
                path[swap_index[0]], path[swap_index[1]] = path[swap_index[1]], path[swap_index[0]]
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
        print(f"Gbest:{Gbest[-1]}\n")

    ret = copy.deepcopy(Gbest)
    Gbest.clear()
    GbestX.clear()
    return ret
