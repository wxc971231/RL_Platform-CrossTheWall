from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from core.Algorithm.RL import BasePolicy
import threading
import numpy as np
import time

class Dijkstra(BasePolicy):
    def __init__(self,controller):
        super().__init__(controller) 
    
    # 控制UI（执行此策略时嵌入到controller窗口中）
    def controlLayout(self):
        if self.layout == None:
            Layout = QtWidgets.QGridLayout()
            self.label_Title = QtWidgets.QLabel(self.centralwidget)
            self.label_Title.setText('Dijkstra')
            Layout.addWidget(self.label_Title, 0, 0, 1, 2, QtCore.Qt.AlignHCenter)
    
            self.pbt_toggleAuto = QtWidgets.QPushButton(self.centralwidget)
            self.pbt_toggleAuto.setText('start')
            Layout.addWidget(self.pbt_toggleAuto, 1, 0, 1, 2)
        
            self.pbt_resetPi = QtWidgets.QPushButton(self.centralwidget)
            self.pbt_resetPi.setText('reset')
            Layout.addWidget(self.pbt_resetPi, 2, 0, 1, 2)
            
            self.controller.pbt_edit.clicked.connect(self.resetPolicy)  
            self.controller.policyReloadSignal.connect(self.resetPolicy)
            self.map.reloadSignal.connect(self.resetPolicy)
            self.pbt_resetPi.clicked.connect(self.resetPolicy)
            self.pbt_toggleAuto.clicked.connect(self.autoToggle)

            self.layout = Layout

        return self.layout 
        
    def controlLayoutInit(self):
        self.initPolicy()  
        self.setLayoutVisiable(True)

    def controlLayoutRemoved(self):
        self.setLayoutVisiable(False)
        self.waitAutoExecEnd()

    def autoToggle(self):
        if self.autoExec:
            self.pbt_toggleAuto.setText('start')
            self.waitAutoExecEnd()
        else:   # 启动子线程自动执行策略
            self.autoExec = True
            self.pbt_toggleAuto.setText('break')
            self.autoThread = threading.Thread(target = self.doDij)
            self.autoThread.setDaemon(True)
            self.autoThread.start()    
    
    def resetPolicy(self):
        self.waitAutoExecEnd()
        self.initPolicy()
        self.pbt_toggleAuto.setText('start')
        self.map.gridWidget.update()
        
    def dijkstra(self,mode):
        endCudeList = self.map.endCubeList
        if endCudeList == []:
            return
        
        cubes = self.map.gridWidget.cubes
        gridWidget = self.map.gridWidget

        # 初始化
        visitedSet = []     # 已访问 
        dist = []           # 点和已访问区最近距离
        for r in range(gridWidget.row):
            set_row = []
            dist_row = []
            for c in range(gridWidget.colum):
                set_row.append(not cubes[r][c].isPassable)
                dist_row.append(10000)
            visitedSet.append(set_row)
            dist.append(dist_row)
    
        # 初始化目前已知最短距离(endCube及其所有前驱)
        for endCube in endCudeList:
            dist[endCube.row][endCube.colum] = 0
            for pc in endCube.priorCubeDict:
                if pc.distance(endCube) < dist[pc.row][pc.colum]:
                    for a in pc.action:
                        pc.pi[a] = 0
                    newAction = endCube.priorCubeDict[pc][0]
                    pc.pi[newAction] = 1
            
        # 从endCube开始反向找出各点到它的最短路
        visitCube,visit_r,visit_c = endCudeList[0],endCudeList[0].row,endCudeList[0].colum
        visitedSet[visitCube.row][visitCube.colum] = True
        while visitCube != None and self.autoExec:

            # 显示本轮新加入visitedSet的点
            visitCube.agentLocated = True
            visitedSet[visit_r][visit_c] = True
            gridWidget.update()
            if mode == 'normal':
                time.sleep(self.controller.timeStep)
            
            # 遍历本轮访问点所有前驱，尝试从visitCube中转以缩短路程
            for pc in visitCube.priorCubeDict:
                r,c = pc.row,pc.colum
                if visitedSet[pc.row][pc.colum] == False: 
                    if dist[visit_r][visit_c] + pc.distance(visitCube) < dist[r][c]:
                        dist[r][c] = dist[visit_r][visit_c] + pc.distance(visitCube)

                        # 重设前驱动作    
                        for a in pc.action:
                            pc.pi[a] = 0
                        newAction = visitCube.priorCubeDict[pc][0]
                        pc.pi[newAction] = 1
            visitCube.agentLocated = False    
            
            # 遍历找出当前最短路径点作为下一轮访问点
            visitCube = None
            shortest = 10000
            for r in range(gridWidget.row):
                for c in range(gridWidget.colum):
                    if visitedSet[r][c] == False and dist[r][c] < shortest:
                        shortest = dist[r][c]
                        visitCube = cubes[r][c]
                        visit_r,visit_c = visitCube.row,visitCube.colum        
        
        # 补充所有等路程动作
        for r in range(gridWidget.row):
            for c in range(gridWidget.colum): # 最后一列不要补充，否则不能一步到终点
                cube = cubes[r][c]
                if cube.isPassable and cube not in self.map.endCubeList:
                    n = 0
                    columRange = gridWidget.colum-1 if self.controller.selectedTask == 'CrossTheWall' else gridWidget.colum
                    if c < columRange:   
                        for a in cube.action:
                            cube.pi[a] = 0
                            ncList = cube.nextCubeDict[a]
                            if ncList != []:
                                nc = ncList[0][0]
                                if nc != None and nc != cube and abs(dist[nc.row][nc.colum] + cube.distance(nc) - dist[r][c]) < 1e-3:
                                    cube.pi[a] = 1
                                    n += 1
                    else:
                        for a in cube.action:
                            cube.pi[a] = 0
                            for endCube in endCudeList:
                                if dist[r][c] == cube.distance(endCube):
                                    newAction = endCube.priorCubeDict[cube][0]
                                    cube.pi[newAction] = 1
                                    n += 1
                    for a in cube.action:
                        if cube.pi[a] != 0:
                            cube.pi[a] = 1/n
    
        # 从UI清除最后一个访问点
        gridWidget.update()
        
        # 结束执行子线程
        self.autoExec = False

    def doDij(self):
        self.dijkstra('normal')
        self.pbt_toggleAuto.setText('start')