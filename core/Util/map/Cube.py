from PyQt5.QtGui import QColor,QFont,QPen,QBrush
from PyQt5.QtCore import Qt,QRect
import numpy as np
import operator
from core.Util.Function import valueLimit

# 地图方格对象
class Cube():
    def __init__(self,x,y,row,colum,l,map,selectedTask):
        self.x = x              # 左上角坐标
        self.y = y
        self.l = l              # 边长
        self.row = row          # 行位置
        self.colum = colum      # 列位置
        self.map = map          # 父对象map的引用，便于访问父对象数据
        self.selectedTask = selectedTask

        self.centerX = x+0.5*l  # 中心坐标
        self.centerY = y+0.5*l
        self.penName = 'default'# 默认画笔名
        self.brush = QBrush(QColor(self.map.penDict['default'].color),Qt.SolidPattern)  # 默认刷子，用于绘制
        self.slide = [0,0,0,0]  # 上下左右滑动
        self.isPassable = True  # 允许通行
        self.isStart = False    # 是起点
        self.isEnd = False      # 是终点
        self.selected = False   # 正在编辑
        self.reward = 0.0       # 奖励
        self.value = 0.0        # 状态价值
        self.Q = {}             # 状态动作价值
        self.pi = {}            # 策略
        self.setActions(self.selectedTask)

        self.agentLocated = False # agent正位于此处
        self.visited = False    # 访问过标记，显示方格开始轨迹时使用

        self.nextCubeDict = {}  # 执行动作后转移到的方格 {a:[(s_,p),...],...}
        self.priorCubeDict = {} # 可达此方格的方格列表  {_s:(_a,p),...}

    def resize(self,x,y,l):
        self.x = x
        self.y = y
        self.l = l
        self.centerX = x+0.5*l  # 中心坐标
        self.centerY = y+0.5*l

    def setActions(self,task):
        if task == 'CrossTheWall':
            self.action = list(range(self.map.gridWidget.row-1,-self.map.gridWidget.row,-1))  # 动作列表(可选速度值)
        else: 
            self.action = [0,1,2,3] # 动作列表        

    # 缓存所有相邻可达方格
    def storeNeighborCube(self):
        if self.isPassable:
            # 终点直接回起点，随便保留一个动作即可
            if self.map.endCubeList != None and self in self.map.endCubeList:
                self.action = [0]

            for a in self.action:
                transfer = self.map.gridWidget.nextCubeAndProbList(self.row,self.colum,a)


                
                
                # 下一步
                if not a in self.nextCubeDict:
                    self.nextCubeDict[a] = transfer
 
                # 上一步
                for nc,p in transfer:
                    if nc != None and not self in nc.priorCubeDict:
                        nc.priorCubeDict[self] = (a,p)

    def resetPolicy(self):
        self.value = 0.0        # 状态价值
        self.Q = {}             # 状态动作价值
        self.pi = {}            # 策略

        # 允许顶着墙走导致agent不动(即允许nc == self)
        N = len([a for a in self.nextCubeDict if self.nextCubeDict[a] != []])
        for a in self.nextCubeDict:
            if self.nextCubeDict[a] != []:
                self.pi[a] = 1/N
                self.Q[a] = 0
            else:
                self.pi[a] = 0
                self.Q[a] = -10000

        self.agentLocated = False 

    # 在Q上贪心来更新策略
    def updatePolicyByQ(self):
        Q = self.Q
        QSorted = sorted(Q.items(), key=lambda Q:Q[1], reverse=True) # 按值降序得元组列表
        
        N = len([item for item in QSorted if abs(QSorted[0][1]-item[1]) <= 1e-4])

        for i in range(len(self.action)):
            if i < N:
                self.pi[QSorted[i][0]] = 1/N
            else:
                self.pi[QSorted[i][0]] = 0

    # 编辑方格
    def update(self,reward,slide,isPassable,isStart,isEnd):
        changed = self.reward != reward or \
                    not operator.eq(self.slide,slide) or \
                    self.isPassable != isPassable or \
                    self.isStart != isStart or \
                    self.isEnd != isEnd
            
        self.reward = reward
        self.slide = slide
        self.isPassable = isPassable
        self.isStart = isStart
        self.isEnd = isEnd

        if not self in self.map.startCubeList and isStart:
            self.map.startCubeList.append(self)
        elif self in self.map.startCubeList and not isStart:
            self.map.startCubeList.remove(self)

        if not self in self.map.endCubeList and isEnd:
            self.map.endCubeList.append(self)
        elif self in self.map.endCubeList and not isEnd:
            self.map.endCubeList.remove(self)

        return changed

    # 绘制方格
    def updateWithPen(self,pen):
        changed = self.penName != pen.name
        self.penName = pen.name
        changed = self.update(pen.reward,pen.slide,pen.isPassable,pen.isStart,pen.isEnd) or changed
        return changed

    # 本方格到cube的欧氏距离
    def distance(self,cube):
        disMatrix = self.map.gridWidget.distanceArray
        '''
        if disMatrix[self.row*columNum+self.colum][cube.row*columNum+cube.colum] != math.sqrt((self.row-cube.row)*(self.row-cube.row) + (self.colum-cube.colum)*(self.colum-cube.colum)):
            raise False
        '''
        if self.isEnd:  # 终点状态直接转移到起点，不计算距离
            return 0
        else:
            return disMatrix[self.row,self.colum][cube.row,cube.colum]
        #return abs(self.row-cube.row) + abs(self.colum-cube.colum)

    def draw(self,painter):
        painter.setPen(QPen(Qt.black, 1, Qt.SolidLine))  
        penColor = self.map.penDict[self.penName].color

        # 设置颜色
        self.brush.setStyle(Qt.SolidPattern)
        if self.isStart:                                
            self.brush.setColor(QColor('#ff3700'))      # 起点红色网格填充
            self.brush.setStyle(Qt.DiagCrossPattern)
        elif self.isEnd:
            self.brush.setColor(QColor('#0037ff'))      # 终点蓝色网格填充
            self.brush.setStyle(Qt.DiagCrossPattern) 
        else:                                           # 其他块
            # 按价值函数显示
            if self.map.showColorByValue: 
                if self.penName == 'wall':
                    self.brush.setColor(QColor(self.map.penDict['wall'].color))
                else:      
                    if self.value <= 0:
                        R = valueLimit(-255*self.value/self.map.gridWidget.maxValue,255,0)
                        self.brush.setColor(QColor(R,0,0))
                    else:
                        G = valueLimit(255*self.value/self.map.gridWidget.maxValue,255,0)
                        self.brush.setColor(QColor(0,G,0))
            # 非分色显示：仅区分墙
            elif not self.map.gridWidget.showWithColor: 
                penName = 'default' if self.penName != 'wall' else 'wall'                     
                self.brush.setColor(QColor(self.map.penDict[penName].color))
            # 分色显示：方格颜色默认为其画笔颜色
            else:                                                   
                self.brush.setColor(QColor(penColor))               

        # 如果在方块编辑模式下选中，颜色设为浅红
        if not self.map.gridWidget.isDrawingMode and self.selected:
            self.brush.setColor(QColor('#FAC8C8'))

        # 绘制
        painter.setBrush(self.brush)
        painter.drawRect(self.x, self.y, self.l, self.l)

        # 叠加文本信息
        if self.isPassable:
            painter.setPen(QColor(100,100,100))
            # 奖励值
            if self.map.showReward:
                painter.setFont(QFont('微软雅黑', 0.15*self.l))
                painter.drawText(self.x+0.05*self.l,self.y+0.2*self.l,str(self.reward))

            # 状态价值
            if self.map.showValue:
                painter.setFont(QFont('微软雅黑', 0.2*self.l))
                painter.drawText(QRect(self.x,self.y,self.l,self.l),Qt.AlignCenter,str(round(self.value,2)))

            # 显示agent位置
            if self.agentLocated:
                painter.setBrush(QColor(230, 230, 0))
                painter.drawEllipse(self.x+0.25*self.l, self.y+0.25*self.l, 0.5*self.l, 0.5*self.l)

    # 返回一个方格副本
    def copy(self):
        cube = Cube(self.x,self.y,self.row,self.colum,self.l,self.map,self.selectedTask)
        cube.penName = self.penName
        cube.slide = self.slide
        cube.isPassable = self.isPassable
        cube.isStart = self.isStart
        cube.isEnd = self.isEnd
        cube.reward = self.reward   
        cube.selected = False
        cube.value = self.value
        cube.Q = self.Q
        return cube