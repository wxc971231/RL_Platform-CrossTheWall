# 适用于Cross The Wall 任务的地图生成器
from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import random

class CWGenerator(QObject):
    def __init__(self,editor):
        super().__init__() 
        self.editor = editor
        self.map = editor.map
        self.centralwidget = editor.centralwidget
        self.layout = None      # 控制layout

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
            self.spinBox_rowNum.setMaximum(100)
            self.spinBox_rowNum.setMinimum(1)
            self.spinBox_rowNum.setValue(10)
            self.spinBox_rowNum.setSingleStep(1)
            Layout.addWidget(self.spinBox_rowNum, 0, 1, 1, 1)  
            self.label_columNum = QtWidgets.QLabel(self.centralwidget)
            self.label_columNum.setText("地图列数")
            Layout.addWidget(self.label_columNum, 1, 0, 1, 1)
            self.spinBox_columNum = QtWidgets.QSpinBox(self.centralwidget)
            self.spinBox_columNum.setMaximum(100)
            self.spinBox_columNum.setMinimum(1)
            self.spinBox_columNum.setValue(50)
            self.spinBox_columNum.setSingleStep(1)
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
            
            self.pbt_generate.clicked.connect(self.genLimitedMapForCrossingWallTask)
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

    # 生成指定大小的穿墙任务地图
    def genLimitedMapForCrossingWallTask(self):
        self.map.isVisible = True
        
        rowNum = int(self.spinBox_rowNum.value())
        columNum = int(self.spinBox_columNum.value())
        wallSpacingMin = int(self.spinBox_wallSpacingMin.value())
        wallSpacingMax = int(self.spinBox_wallSpacingMax.value())
        passWayNumMax = int(self.spinBox_passWayNumMax.value())

        self.map.gridWidget.initGrid(rowNum,columNum)
        cubes = self.map.gridWidget.cubes

        wallPos = random.randint(wallSpacingMin,wallSpacingMax)

        # 第一列和最后一列随机设置起点和终点
        startCube = cubes[random.randint(0,rowNum-1)][0]
        endCube = cubes[random.randint(0,rowNum-1)][columNum-1]
        startCube.isStart = True
        endCube.isEnd = True
        endCube.reward = 50
        self.map.startCubeList = [startCube,]
        self.map.endCubeList = [endCube,]

        # 第一列和最后一列禁止放置墙壁
        while 0 < wallPos < columNum-1:
            for row in range(rowNum):
                cubes[row][wallPos].updateWithPen(self.map.penDict['wall'])
            holeNum = random.randint(1,passWayNumMax)
            for i in range(holeNum):
                cube = cubes[random.randint(0,rowNum-1)][wallPos]
                cube.updateWithPen(self.map.penDict['default'])
                cube.reward = 5
                cube.penName = 'modified'
            wallPos += random.randint(wallSpacingMin,wallSpacingMax)

        # 设置保存标识
        self.editor.setMapSaved(False)
        
