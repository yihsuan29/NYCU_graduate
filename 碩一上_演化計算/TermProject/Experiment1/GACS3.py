import math
import copy
import random
import matplotlib.pyplot as plt

# GA 參數
NP = 100  # 族群數量
low = 0
up = 100
PrC = 0.9  # 交叉概率
PrM_initial = 0.04  # 初始突變概率
gen = 100  # 迭代數
Gbest = []  # 最佳解的適應值
GbestX = []  # 最佳解的基因路徑
CarSpeed = 1  # 充電車速度
ChargingRate = 3.4  # 充電速率

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
        #print("time = ", time_to_station, "= ", time_to_charge)
        
    return num_zero_capacity

def priority_crossover(sensor, parent1, parent2, K):
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

def random_shuffle_mutation(path, mutation_rate=1.0):

    if random.random() > mutation_rate:
        return path
    
    if len(path) < 2:
        return path
    
    start = random.randint(0, len(path) - 2)
    end = random.randint(start + 1, len(path) - 1)
    
    sub_sequence = path[start:end + 1]
    
    random.shuffle(sub_sequence)
    
    mutated_path = path[:start] + sub_sequence + path[end + 1:]
    
    return mutated_path

# 初始化基因算法參數和初始族群
def GA3(sensor_need_charge, sensor, bc):
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
    
    # 初始化突變概率
    PrM = PrM_initial
    
    for g in range(gen):
        print("迭代數:", g)
        num_mutations = 0
        num_success = 0
        
        # 設定動態的K值
        mean_K = 0.3 * len(sensor)
        sigma_K = 0.1 * len(sensor)
        z = box_muller()
        K = int(mean_K + sigma_K * z)
        K = max(1, min(K, len(sensor)))  # 確保K在[1, len(sensor)]之間
        
        for i in range(NP):
            # 選父代基因
            weight = [1 / (t[1] + 1) for t in X]  # 使用適應度的倒數作為權重，適應度越低，權重越高
            [chri, chrj] = random.choices(X, weights=weight, k=2)
            index_chri = X.index(chri)
            index_chrj = X.index(chrj)
            
            # 交叉操作
            if random.random() < PrC:
                child_path = priority_crossover(sensor, list(chri[2]), list(chrj[2]), K)
                child_fitness = fitness_function(copy.deepcopy(sensor), child_path, bc)
                chro = (child_path[0], child_fitness, child_path)

                # 按照 fitness 值對元組進行排序，取前兩個賦值給 chri, chrj
                sorted_tuples = sorted([chri, chrj, chro], key=lambda x: x[1])[:2]
                chri, chrj = sorted_tuples[0], sorted_tuples[1]

            # 變異操作：使用隨機重排變異（RSM）
            if random.random() < PrM:
                num_mutations += 1
                # 從 chri 和 chrj 中隨機選擇一條路徑進行變異
                parent = random.choice([chri[2], chrj[2]])
                mutated_path = random_shuffle_mutation(list(parent), mutation_rate=1.0)  # 確定變異
                mutated_fitness = fitness_function(copy.deepcopy(sensor), mutated_path, bc)
                chro = (mutated_path[0], mutated_fitness, mutated_path)

                # 判斷是否變異成功
                if mutated_fitness < min(chri[1], chrj[1]):
                    num_success += 1

                # 按照 fitness 值對元組進行排序，取前兩個賦值給 chri, chrj
                sorted_tuples = sorted([chri, chrj, chro], key=lambda x: x[1])[:2]
                chri, chrj = sorted_tuples[0], sorted_tuples[1]
            
            X[index_chri] = chri
            X[index_chrj] = chrj

        # 根據1/5法則調整PrM
        if num_mutations > 0:
            success_rate = num_success / num_mutations
            if success_rate > 0.2:
                PrM *= 1.1  # 增加突變概率
            else:
                PrM *= 0.9  # 減少突變概率
            # 限制PrM在合理範圍內
            PrM = max(0.001, min(PrM, 0.5))
        
        # 選擇下一代族群中的最佳基因
        X.sort(key=lambda x: x[1])
        
        # 紀錄最佳解
        Gbest.append(X[0][1])
        GbestX.append(X[0][2])

    #print("Gbest:", Gbest)
    print("lastGbest:", Gbest[gen - 1])
    #print("GbestX:", GbestX)
    xindex = list(range(1, gen + 1))
    plt.plot(xindex, Gbest, '.')
    plt.xlabel('Generation')
    plt.ylabel('Best Fitness')
    plt.title('Best Fitness over Generations')
    plt.show()
    return Gbest
