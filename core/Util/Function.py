# 这里提供一些工具函数
import numpy as np

# 限制值
def valueLimit(value,MAX,MIN):
    if value > MAX: return MAX
    if value < MIN: return MIN
    return value

# 依概率选择(字典形式)
def probabilisticChoiseDict(choiceProbabilitiesDict):
    cList, pList = zip(*choiceProbabilitiesDict.items()) 
    return np.random.choice(cList, p=pList)

# 依概率选择(列表形式)
def probabilisticChoise(choiceList,probabilities):
    return np.random.choice(choiceList, p=probabilities)

# 等概率随机选择
def randomChoice(choiceList):
    return choiceList[np.random.randint(0,len(choiceList))] # 这样写支持选择多维元素

# 价值贪心选择 (等价值的随机选择)
def greedyChoise(choiceValueDict):
    cv = choiceValueDict
    return np.random.choice([c for c in cv if abs(cv[c] - cv[max(cv,key=cv.get)]) < 1e-5]) 

# epsilon-贪心选择动作
def getActionByEpsilonGreedy(epsilon,cube):
    if epsilon > np.random.uniform(0,1):
        action = randomChoice([a for a in cube.action if cube.nextCubeDict[a] != []])
    else:
        action = greedyChoise(cube.Q)
    return action

# 根据策略选择动作
def getActionByPi(cube):
    return probabilisticChoiseDict(cube.pi)

# 根据策略选择动作，但有epsilon概率试探
def getActionByEpsilonPi(epsilon,cube):
    if np.random.binomial(1,epsilon) == 1:
        action = randomChoice([a for a in cube.action if cube.nextCubeDict[a] != []])
    else:
        action = getActionByPi(cube)
    return action

def RGB2Hex(rgb):
    color = '#'
    for i in rgb:
        num = int(i)
        color += str(hex(num))[-2:].replace('x', '0').upper()
    return color

def Hex2RGB(hex):
    r = int(hex[1:3],16)
    g = int(hex[3:5],16)
    b = int(hex[5:7],16)
    rgb = (r,g,b)
    return rgb

def randomcolor():
    colorArr = ['1','2','3','4','5','6','7','8','9','A','B','C','D','E','F']
    color = ""
    for i in range(6):
        color += colorArr[np.random.randint(15)]
    return "#"+color
