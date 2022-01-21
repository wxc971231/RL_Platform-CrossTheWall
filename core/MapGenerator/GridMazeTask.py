# 适用于 Grid Maze 任务的地图生成器
from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import random
import numpy as np

class GMGenerator(QObject):
    def __init__(self,editor):
        super().__init__() 
        self.editor = editor
        self.map = editor.map
        self.centralwidget = editor.centralwidget
        self.layout = None      # 控制layout

        self.rowNum = 0
        self.columNum = 0
        
    # 控制layout可见性
    def setLayoutVisiable(self,visible):
        layout = self.controlLayout()
        for i in range(layout.count()):     # 除了上分布spacer其他都设置visible
            layout.itemAt(i).widget().setVisible(visible)

    # 控制UI（执行此策略时嵌入到MapEditor窗口中）
    def controlLayout(self):
        if self.layout == None:
            Layout = QGridLayout()            
            self.label_rowNum = QtWidgets.QLabel(self.centralwidget)
            self.label_rowNum.setText("地图行数")
            Layout.addWidget(self.label_rowNum, 0, 0, 1, 1)
            self.spinBox_rowNum = QtWidgets.QSpinBox(self.centralwidget)
            self.spinBox_rowNum.setMaximum(99)
            self.spinBox_rowNum.setMinimum(5)
            self.spinBox_rowNum.setValue(11)
            self.spinBox_rowNum.setSingleStep(2)
            Layout.addWidget(self.spinBox_rowNum, 0, 1, 1, 1)  
            self.label_columNum = QtWidgets.QLabel(self.centralwidget)
            self.label_columNum.setText("地图列数")
            Layout.addWidget(self.label_columNum, 1, 0, 1, 1)
            self.spinBox_columNum = QtWidgets.QSpinBox(self.centralwidget)
            self.spinBox_columNum.setMaximum(99)
            self.spinBox_columNum.setMinimum(5)
            self.spinBox_columNum.setValue(11)
            self.spinBox_columNum.setSingleStep(2)
            Layout.addWidget(self.spinBox_columNum, 1, 1, 1, 1)  
            
            self.label_wallSpacingMax = QtWidgets.QLabel(self.centralwidget)
            self.label_wallSpacingMax.setText("最大墙间隔")
            Layout.addWidget(self.label_wallSpacingMax, 2, 0, 1, 1)
            self.spinBox_wallSpacingMax = QtWidgets.QSpinBox(self.centralwidget)
            self.spinBox_wallSpacingMax.setValue(10)
            self.spinBox_wallSpacingMax.setSingleStep(1)
            Layout.addWidget(self.spinBox_wallSpacingMax, 2, 1, 1, 1)  
            self.label_wallSpacingMax = QtWidgets.QLabel(self.centralwidget)
            self.label_wallSpacingMax.setText("最小墙间隔")
            Layout.addWidget(self.label_wallSpacingMax, 3, 0, 1, 1)
            self.spinBox_wallSpacingMin = QtWidgets.QSpinBox(self.centralwidget)
            self.spinBox_wallSpacingMin.setValue(5)
            self.spinBox_wallSpacingMin.setSingleStep(1)
            Layout.addWidget(self.spinBox_wallSpacingMin, 3, 1, 1, 1)  
            self.spinBox_wallSpacingMax.setMaximum(50)
            self.spinBox_wallSpacingMin.setMinimum(2)
            self.spinBox_wallSpacingMin.setMaximum(int(self.spinBox_wallSpacingMax.value()))
            self.spinBox_wallSpacingMax.setMinimum(int(self.spinBox_wallSpacingMin.value()))

            self.label_passWayNumMax = QtWidgets.QLabel(self.centralwidget)
            self.label_passWayNumMax.setText("最大通道数")
            Layout.addWidget(self.label_passWayNumMax, 4, 0, 1, 1)
            self.spinBox_passWayNumMax = QtWidgets.QSpinBox(self.centralwidget)
            self.spinBox_passWayNumMax.setMaximum(int(self.spinBox_rowNum.value()))
            self.spinBox_passWayNumMax.setMinimum(1)
            self.spinBox_passWayNumMax.setValue(1)
            self.spinBox_passWayNumMax.setSingleStep(1)
            Layout.addWidget(self.spinBox_passWayNumMax, 4, 1, 1, 1)  

            self.pbt_generate = QtWidgets.QPushButton(self.centralwidget)
            self.pbt_generate.setText('生成地图')
            Layout.addWidget(self.pbt_generate, 5, 0, 1, 2)
            
            self.pbt_generate.clicked.connect(self.genLimitedMapForGridMazeTask)
            self.spinBox_rowNum.valueChanged.connect(self.setMaximum_passWayNumMax)
            self.spinBox_wallSpacingMax.valueChanged.connect(self.setMaximum_WallSpacingMin)
            self.spinBox_wallSpacingMin.valueChanged.connect(self.setMinimum_WallSpacingMax)

            self.layout = Layout

        return self.layout 
        
    def setMaximum_WallSpacingMin(self):
        self.spinBox_wallSpacingMin.setMaximum(int(self.spinBox_wallSpacingMax.value()))
    
    def setMinimum_WallSpacingMax(self):
        self.spinBox_wallSpacingMax.setMinimum(int(self.spinBox_wallSpacingMin.value()))

    def setMaximum_passWayNumMax(self):
        self.spinBox_passWayNumMax.setMaximum(int(self.spinBox_rowNum.value()))

    def addNeighbouringWallCube2TempSet(self,row,colum,tempSet):
        tempRow = [-1,1,0,0]
        tempColum = [0,0,1,-1]
        for i in range(4):
            r,c = row + tempRow[i],colum + tempColum[i]

            if r >= 0 and r <= self.rowNum - 1 and c >= 0 and c <= self.columNum - 1 and (r,c) not in tempSet:        
                tempSet.append((r,c))

    def removeWallIfBothSidesAreVisited(self,visited,wallSet,tempSet):
        tempCopy = tempSet.copy()
        for wallPos in tempCopy:
            divided0,divided1 = wallSet[wallPos][0],wallSet[wallPos][1]
            if visited[divided0] and visited[divided1]:
                tempSet.remove(wallPos)

    # 生成指定大小的穿墙任务地图
    def genLimitedMapForGridMazeTask(self):
        self.map.isVisible = True        

        rowNum,columNum = int(self.spinBox_rowNum.value()),int(self.spinBox_columNum.value())
        self.rowNum,self.columNum = rowNum,columNum

        self.map.gridWidget.initGrid(rowNum,columNum)
        cubes = self.map.gridWidget.cubes

        # 在偶数坐标位置随机生成起点和终点
        sRow,sColum = random.randrange(0,rowNum-1,2),random.randrange(0,columNum-1,2)
        eRow,eColum = random.randrange(0,rowNum-1,2),random.randrange(0,columNum-1,2)
        startCube = cubes[sRow][sColum]
        endCube = cubes[eRow][eColum]
        while endCube == startCube:
            eRow,eColum = random.randrange(0,rowNum-1,2),random.randrange(0,columNum-1,2)
            endCube = cubes[eRow][eColum]
        startCube.isStart = True
        endCube.isEnd = True
        endCube.reward = 50
        self.map.startCubeList = [startCube,]
        self.map.endCubeList = [endCube,]

        # 初始化路径集合和墙壁集合
        visited = np.zeros((rowNum,columNum))   # 已访问标记
        pathSet = []                            # 可通行方格集合
        wallSet = {}                            # 墙壁方格集合
        for r in range(rowNum):
            for c in range(columNum):
                if r%2 == 0 and c%2 == 0:
                    pathSet.append((r,c)) 
                else:
                    cubes[r][c].updateWithPen(self.map.penDict['wall'])
                    if r%2 == 1:
                        wallSet[(r,c)] = [(r-1,c),(r+1,c)]
                    else:
                        wallSet[(r,c)] = [(r,c-1),(r,c+1)]
        
        # prim 算法，相当于构造一个最小生成树
        tempSet = []
        self.addNeighbouringWallCube2TempSet(sRow,sColum,tempSet)
        visited[sRow,sColum] = 1

        while tempSet != []:
            
            # 随机从tempSet选并去掉一个墙
            wallPos = random.sample(tempSet,1)[0]
            cubes[wallPos[0]][wallPos[1]].updateWithPen(self.map.penDict['default'])
            tempSet.remove(wallPos)

            # 此墙分割的两个的区域中，未访问的一边作为新的可通行方格
            divided0,divided1 = wallSet[wallPos][0],wallSet[wallPos][1]
            visited0,visited1 = visited[divided0],visited[divided1]
            newPathPos = divided0 if visited0 == 0 else divided1
            visited[newPathPos] = 1

            # 将新的可通行方格邻接的墙加入tempSet 
            self.addNeighbouringWallCube2TempSet(newPathPos[0],newPathPos[1],tempSet)
            
            # 将tempSet中所有两侧都被访问过的墙去除
            self.removeWallIfBothSidesAreVisited(visited,wallSet,tempSet)

        # 设置保存标识
        self.editor.setMapSaved(False)
        
