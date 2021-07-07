# 核心组件 —— 监视器：实现算法测试数据收集和实时显示，并提供数据保存功能
from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import QtCore, QtGui, QtWidgets
from core.Util.dialog import SaveFileDialog
from core.Util.file import WaveFile
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

class Monitor(QMainWindow):
    def __init__(self,controller):
        super().__init__() 
        self.controller = controller
        self.updating = False   # 正在更新
        self.filterL = 18       # 滑动均值滤波长度
        self.saveFileDialog = SaveFileDialog('wave')    # 保存波形时弹出的窗口
        self.waveData = None        # 波形数据对象
        self.waveFile = WaveFile()  # 波形文件对象
        self.setupUi()

    def setupUi(self):
        self.setWindowTitle('Wave Monitor')
        self.resize(500, 900)
        self.setWindowIcon(QtGui.QIcon('src/images/grid.png'))
        
        self.centralwidget = QtWidgets.QWidget(self)
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.graph_layout = QtWidgets.QVBoxLayout()
        self.verticalLayout.addLayout(self.graph_layout)
        
        widget,self.p1,self.p2 = self.set_graph_ui()
        self.graph_layout.addWidget(widget)

        self.pbt_saveWave = QtWidgets.QPushButton(self.centralwidget)
        self.pbt_saveWave.setText('保存折线图数据')
        self.pbt_saveWave.clicked.connect(lambda:self.saveFileDialog.showWidget(self.waveData.name))
        self.verticalLayout.addWidget(self.pbt_saveWave)

        self.setCentralWidget(self.centralwidget)

        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 834, 23))
        self.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.setStatusBar(self.statusbar)

        self.saveFileDialog.saveWaveSignal.connect(self.saveWave)

    # 建立波形图
    def set_graph_ui(self):
        pg.setConfigOptions(foreground='#DDDDDD',antialias=True)     # pg全局变量设置函数，antialias=True开启曲线抗锯齿
        win = pg.GraphicsLayoutWidget()                     # 创建pg layout，可实现数据界面布局自动管理

        p1 = win.addPlot(title="轨迹长度")                  # 添加第一个绘图窗口
        p1.setLabel('left', text='长度', color='#ffffff')   # y轴设置函数
        p1.setLabel('bottom', text='轨迹',color='#ffffff')  # x轴设置函数
        p1.showGrid(x=True, y=True)                         # 栅格设置函数
        p1.setLogMode(x=False, y=False)                     # False代表线性坐标轴，True代表对数坐标轴
        # p1.addLegend()  # 可选择是否添加legend

        win.nextRow()                                       # layout换行，采用垂直排列，不添加此行则默认水平排列

        p2 = win.addPlot(title="轨迹收益")
        p2.setLabel('bottom', text='轨迹', color='#ffffff')
        p2.setLabel('left', text='收益',color='#ffffff')
        p2.showGrid(x=True, y=True)
        p2.setLogMode(x=False, y=False)
        # p2.addLegend()

        return win,p1,p2

    def updateWaveLength(self,lengths):
        try:
            self.p1.clear()
            fl = np.convolve(lengths, np.ones((self.filterL,))/self.filterL, mode='valid')  # 一维卷积实现滑动均值滤波
            self.p1.plot(lengths,pen=(0,255,0,50))                                          # 原始数据，透明显示
            self.p1.plot(x=np.arange(0.5*self.filterL,0.5*self.filterL+fl.shape[0]),y=fl,pen=(0,255,0)) # 滤波后数据，显示时跳过数据不完全重叠的边际部分
        except Exception:
            pass

    def updateWaveReward(self,returns):
        try:
            self.p2.clear()
            fr = np.convolve(returns, np.ones((self.filterL,))/self.filterL, mode='valid')  # 一维卷积实现滑动均值滤波
            self.p2.plot(returns,pen=(0,255,0,50))                                          # 原始数据，透明显示
            self.p2.plot(x=np.arange(0.5*self.filterL,0.5*self.filterL+fr.shape[0]),y=fr,pen=(0,255,0)) # 滤波后数据，显示时跳过数据不完全重叠的边际部分
        except Exception:
            pass
    
    def clearWaves(self):
        self.p1.clear()
        self.p2.clear()

    # 在刚打开监视器时，初始化波形
    def initWaves(self,waveData):
        self.waveData = waveData
        self.clearWaves()
        if waveData.dataNum != 0:
            self.updateWaveLength(waveData.lengthArray)
            self.updateWaveReward(waveData.returnArray)

    # 监视器处于打开状态，实时更新波形
    def updateWaves(self):     
        if self.isVisible():   
            self.updateWaveLength(self.waveData.lengthArray)
            self.updateWaveReward(self.waveData.returnArray)

    def showEvent(self, event):
        self.updating = True

        # 由于实时刷新速度限制，波形实时显示时计算周期最小值设为0.001
        self.controller.spinBox_timeStep.setDecimals(3)
        self.controller.spinBox_timeStep.setSingleStep(0.001)
        self.controller.spinBox_timeStep.setMinimum(0.001)
        if self.controller.timeStep < 0.001:
            self.controller.timeStep = 0.001
            self.controller.spinBox_timeStep.setValue(0.001)

    def closeEvent(self,event):
        self.updating = False

        # 关闭波形显示时计算周期最小值还原到0
        self.controller.spinBox_timeStep.setSingleStep(0.01)
        self.controller.spinBox_timeStep.setDecimals(2)
        self.controller.spinBox_timeStep.setMinimum(0)
        
    # 保存界面信号槽函数，把当前wave存储到filePath
    def saveWave(self,filePath,fileName):
        self.waveData.name = fileName
        self.waveData.path = filePath
        self.waveFile.saveWave(self.waveData)