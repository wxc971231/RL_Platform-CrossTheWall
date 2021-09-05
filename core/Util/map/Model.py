from core.Util.Function import probabilisticChoiseDict
import collections
import copy
import random

class Model():
    def __init__(self,controller):
        self.controller = controller
        self.transfer = {}          # 学得模型                  {(s,a):{(r,s_):n,...},...} (n是s,a->r,s_ 发生的次数)
        self.transferFromCnt = {}   # 某(s,a)处发生转移的次数    {(s,a):n,...} 
        
    def reset(self):
        self.transfer.clear()
        self.transferFromCnt.clear()
    
    def update(self,s,a,s_,r):
        rs,cs = s.row,s.colum
        rs_,cs_ = s_.row,s_.colum

        try:
            self.transferFromCnt[(rs,cs,a)] += 1
        except KeyError:            # 第一次遇到 s,a 处的转移
            self.transfer[(rs,cs,a)] = collections.OrderedDict()
            self.transfer[(rs,cs,a)][(r,rs_,cs_)] = 1
            self.transferFromCnt[(rs,cs,a)] = 1
            return

        try:
            self.transfer[(rs,cs,a)][(r,rs_,cs_)] += 1
        except KeyError:            # 第一次遇到转移 s,a->s_
            self.transfer[(rs,cs,a)][(r,rs_,cs_)] = 1
        
    def getTransfer(self,s,a):
        rs,cs = s.row,s.colum
        try:
            temp = copy.deepcopy(self.transfer[(rs,cs,a)])
            for (r,rs_,cs_) in temp:
                temp[(r,rs_,cs_)] /= self.transferFromCnt[(rs,cs,a)]
            r,rs_,cs_ = probabilisticChoiseDict(temp)
            s_ = self.controller.map.gridWidget.cubes[rs_][cs_]
            p = self.transfer[(rs,cs,a)][(r,rs_,cs_)]/self.transferFromCnt[(rs,cs,a)]
            return s_,r,p
        except KeyError:
            assert False

    def getRandomTranfer(self):
        rs,cs,a = random.sample(self.transfer.keys(),1)[0]
        r,rs_,cs_ = random.sample(self.transfer[(rs,cs,a)].keys(),1)[0]
        s = self.controller.map.gridWidget.cubes[rs][cs]
        s_ = self.controller.map.gridWidget.cubes[rs_][cs_]

        return s,a,s_,r    

    def getProb(self,s,a,s_,r):
        rs,cs = s.row,s.colum
        rs_,cs_ = s_.row,s_.colum
        try:
            return self.transfer[(rs,cs,a)][(r,rs_,cs_)]/self.transferFromCnt[(rs,cs,a)]
        except KeyError:
            assert False

    def inModel(self,s,a):
        rs,cs = s.row,s.colum
        return (rs,cs,a) in self.transfer
