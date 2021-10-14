from PyQt5.QtCore import QObject,pyqtSignal
from core.Util.map import Pen,GridWidget

class Map(QObject):
    reloadSignal = pyqtSignal() 

    def __init__(self,mapEditor):
        super().__init__() 
        self.defaultPens = ['default','wall','modified']
        self.penDict = {'default':Pen('#C8C8C8','default',[0,0,0,0],True,False,False,0),
                        'wall':Pen('#646464','wall',[0,0,0,0],False,False,False,0),
                        'modified':Pen('#d2ffe3','modified',[0,0,0,0],True,False,False,0)}  # 默认画笔字典

        self.mapEditor = mapEditor
        self.controller = mapEditor.controller

        self.startCubeList = None           # 起点
        self.endCubeList = None             # 终点
        self.disCostDiscount = 1.0          # 路程折扣
        self.stepReward = 0.0               # 每步奖励
        
        self.isVisible = False              # 是否显示地图网格
        self.showReward = True              # 显示状态奖励
        self.showValue = True               # 显示状态价值
        self.showQ = False                  # 显示状态动作价值
        self.policyColor = '#AA0000'        # 策略颜色
        self.showPolicy = False             # 显示策略      
        self.showPolicyOfSelectedCube = False   # 仅显示选中块的策略 
        self.showEpisodeOfSelectedCube = True   # 显示选中块到终点的轨迹 
        self.showColorByValue = False       # 按价值分色显示
        self.showDFS = False                # 显示地图上DFS轨迹
       
        self.saved = False                  # 最新改动是否已保存到配置文件
        self.name = ''                      # 地图配置文件名
        self.path = ''                      # 地图配置文件路径

        self.gridWidget = GridWidget(0,0,self) # 地图网格
    
    def getMapPara(self):
        startCubesPos,endCubesPos = [],[]
        for cube in self.startCubeList:
            startCubesPos.append([cube.row,cube.colum])
        for cube in self.endCubeList:
            endCubesPos.append([cube.row,cube.colum])
        return MapPara([self.gridWidget.row,self.gridWidget.colum],startCubesPos,endCubesPos,self.disCostDiscount,self.stepReward)

    def close(self):
        self.isVisible = False
        self.gridWidget.update()

class MapPara():
    def __init__(self,size,startCubesPos,endCubesPos,disCostDiscount,stepReward):
        self.size = size
        self.startCubePosList = startCubesPos
        self.endCubePosList = endCubesPos
        self.disCostDiscount = disCostDiscount
        self.stepReward = stepReward


        