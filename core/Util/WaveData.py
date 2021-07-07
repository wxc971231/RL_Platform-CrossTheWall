# 波形数据对象
import numpy as np 

class WaveData():
    def __init__(self,returnArray,lengthArray):
        self.color = (0,255,0)
        self.name = ''
        self.path = ''
        self.dataNum = 0
        self.returnArray = returnArray  # 轨迹收益列表
        self.lengthArray = lengthArray  # 轨迹长度列表
        self.isVisible = True

    def clear(self):
        self.dataNum = 0
        self.returnArray = np.array([],dtype='float64')
        self.lengthArray = np.array([],dtype='float64')       

    def appendData(self,r,l):
        self.dataNum = self.dataNum + 1
        self.returnArray = np.hstack((self.returnArray,r))
        self.lengthArray = np.hstack((self.lengthArray,l))

    def __eq__(self,other):
        if other == None:
            return False
        return self.path == other.path
