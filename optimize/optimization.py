""" 
@author: zoutai
@file: optimization.py 
@time: 2018/04/22 
@description: 
"""

import random
import time

import math

people = [('Seymour', 'BOS'),
          ('Franny', 'DAL'),
          ('Zooey', 'CAK'),
          ('Walt', 'MIA'),
          ('Buddy', 'ORD'),
          ('Les', 'OMA')]

# newyork的Laguardia机场
destination = 'LGA'

# 第一步，以出发地-目的地为key，以具体的航班信息为value，做字典映射
flights = {}
for line in open('schedule.txt'):
    origin, dest, departTime, arriveTime, price = line.strip().split(',')
    flights.setdefault((origin, dest), [])
    # 多趟航班，使用append
    flights[(origin, dest)].append((departTime, arriveTime, int(price)))


# 返回时间的分钟表示
def getminutes(t):
    x = time.strptime(t, '%H:%M')
    return x[3] * 60 + x[4]


def printschedule(r):
    for d in range(len(r) // 2):
        name = people[d][0]
        origin = people[d][1]
        go = flights[(origin, dest)][r[d * 2]]
        back = flights[(dest, origin)][r[d * 2 + 1]]
        print('%10s%10s，%5s-%5s，%3s，%5s-%5s，%3s'
              % (name, origin, go[0], go[1], go[2], back[0], back[1], back[2]))


s = [1, 4, 3, 2, 7, 3, 6, 3, 2, 4, 5, 3]
printschedule(s)


# 成本函数=等待时间+机票+出租车
def schedulecost(sol):
    totalcost = 0
    earliestDep = 24 * 60
    latestArrive = 0

    for d in range(len(sol) // 2):
        name = people[d][0]
        origin = people[d][1]
        go = flights[(origin, dest)][int(sol[d * 2])]
        back = flights[(dest, origin)][sol[int(d * 2 + 1)]]
        totalcost += go[2] + back[2]

        if latestArrive < getminutes(go[1]):
            latestArrive = getminutes(go[1])
        if earliestDep > getminutes(back[0]):
            earliestDep = getminutes(back[0])

    totalWait = 0
    for d in range(len(sol) // 2):
        go = flights[(origin, dest)][sol[d * 2]]
        back = flights[(origin, dest)][sol[d * 2 + 1]]
        totalWait += (latestArrive - getminutes(go[1]))
        totalWait += (getminutes(back[0]) - earliestDep)

    # 出租车50/天
    if latestArrive < earliestDep:
        totalcost += 50

    return totalcost + totalWait


print("默认初始化值：",schedulecost(s))

domain = [(0, 9)] * (len(people) * 2)


# 1、随机法
def randomoptimize(domain, costf):
    best = 999999999
    # bestRs = None
    iterNum = 1000
    for i in range(iterNum):
        r = [random.randint(domain[i][0], domain[i][1]) for i in range(len(domain))]
        cost = costf(r)
        if cost < best:
            best = cost
            # bestRs = best
    return r, best

r, best = randomoptimize(domain,schedulecost)
print("随机法：",best)

# 2、爬山法
# 对于每一个未知数，搜索维度方向上的邻近节点，取最小值，直到最小值不变，退出
def hillClimb(domain,costf):
    # 创建随机解-初始化
    sol = [random.randint(domain[i][0],domain[i][1]) for i in range(len(domain))]

    # 循环
    while 1:
        # 创建邻接-表：二维的，即左右两个
        neighbors = []
        # 这里面的邻接区并不完全对，应该再加上一个维度循环，即单独固定一个变量变化
        for j in range(len(domain)):
            if sol[j]>domain[j][0]:
                neighbors.append(sol[0:j]+[sol[j]-1]+sol[j+1:])
            if sol[j]<domain[j][1]:
                neighbors.append(sol[0:j]+[sol[j]+1]+sol[j+1:])

        # 比较当前值和邻接值
        current = costf(sol)
        best = current
        for j in range(len(neighbors)):
            cost = costf(neighbors[j])
            if best>cost:
                best=cost
                sol = neighbors[j]

        # 整个邻接区都没有更好的，则终止循环
        if best==current:
            break;

    return sol,best
sol,best = hillClimb(domain,schedulecost)
print("爬山法：",best)


# 3、模拟退火
# 原理相对于爬山法，为了避免陷入局部最小值，在初期的时候，对于不符合的结果，暂时不排除

# T:初始温度，cool:冷却因子，step方向步长
def annealingoptimize(domain,costf,T=10000,cool=0.95,step=1):
    # 初始化随机值
    vec = [random.randint(domain[i][0],domain[i][1]) for i in range(len(domain))]
    while T > 0.1:
        # 随机选择一个方向
        i = random.randint(0,len(domain)-1)
        director = random.randint(-step,step)
        vecb = vec[:]
        vecb[i]+=director # 偏移

        # 防止出界
        if vecb[i]<domain[i][0]:
            vecb[i]=domain[i][0]
        elif vecb[i]>domain[i][1]:
            vecb[i]=domain[i][1]

        costCur = costf(vec)
        costB = costf(vecb)


        if (costB<costCur or random.random()<pow(math.e,-(costB-costCur)/T)):
            vec = vecb # 即便costB>costCur,也不用保留之前的vec，因为，温度下降后，会再返回到当前值

        # 降低温度
        T = T * cool
    return vec,costf(vec)

sol,best = annealingoptimize(domain,schedulecost)
print("模拟退火算法：",best)

# 4、遗传算法
def geneticoptimize(domain,costf,popsize=50,step=1,mutprob=0.2,elite=0.2,mixiter=100):
    # 变异
    def mutate(vec):
        i = random.randint(0,len(domain)-1)
        # 随机数什么用？
        if random.random()<0.5 and vec[i]>domain[i][0]:
            return vec[:i]+[vec[i]-step]+vec[i+1:]
        elif vec[i]<domain[i][1]:
            return vec[:i]+[vec[i]+step]+vec[i+1:]

    # 重组
    def crossover(vec1,vec2):
        i = random.randint(1,len(domain)-2)
        return vec1[:i]+vec2[i:]

    # 初始化种群
    pop = []
    for i in range(popsize):
        vec = [random.randint(domain[j][0],domain[j][1]) for j in range(len(domain))]
        pop.append(vec)

    toplite = int(popsize * elite)

    for i in range(mixiter):

        # 排序，进行物种进化选择
        scores = [(costf(v),v) for v in pop]
        scores.sort()
        ranked = [v for (s,v) in scores]

        pop = ranked[:toplite]
        while len(pop)<popsize:
            if random.random()<mutprob:
                c = random.randint(0,toplite)
                pop.append(mutate(ranked[c]))
            else:
                c1 = random.randint(0,toplite)
                c2 = random.randint(0,toplite)
                pop.append(crossover(ranked[c1],ranked[c2]))
        print(scores[0][0])
    return scores[0][1],scores[0][0]

sol, best = geneticoptimize(domain, schedulecost)
print("遗传算法：",best)
