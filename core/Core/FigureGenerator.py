# 核心组件 —— 图表生成器：允许用户加载多条测试数据并绘制到同一张折线图上，提供简单的图表编辑和数据处理功能
import os 
import matplotlib.pyplot as plt
import numpy as np
import pyqtgraph as pg
from functools import partial 
from PyQt5 import QtWidgets, QtCore, QtGui
from core.Util.dialog import LoadWaveDialog,SaveFileDialog
from core.Util.file import WaveFile
from core.Util import WaveData
from core.Util.Function import RGB2Hex,Hex2RGB

class FigureGenerator(QtWidgets.QMainWindow):
    def __init__(self,controller):
        super().__init__() 
        self.controller = controller
    
        self.filterL = 18   # 滑动滤波buffer长度
        self.alpha = 200

        self.loadWaveDialog = LoadWaveDialog((os.getcwd()+'/wave').replace('\\','/'))
        self.waveFile = WaveFile()  # 波形文件对象
        self.saveFileDialog = SaveFileDialog('wave')    # 保存波形时弹出的窗口

        self.loadedWave = []        # 已加载波形
        self.waveSelected = None    # 当前选中的波形

        self.setupUi()

    # 波形图面板
    def graphWidget(self):
        pg.setConfigOptions(foreground='#000000',antialias=True)     # pg全局变量设置函数，antialias=True开启曲线抗锯齿
        win = pg.GraphicsLayoutWidget()         # 创建pg layout，可实现数据界面布局自动管理
        win.setBackground((230, 230, 230))      # 背景色

        p1 = win.addPlot(title="轨迹长度")                  # 添加第一个绘图窗口
        p1.setLabel('left', text='长度', color='#000000')   # y轴设置函数
        p1.setLabel('bottom', text='轨迹',color='#000000')  # x轴设置函数
        p1.showGrid(x=True, y=True)                         # 栅格设置函数
        p1.setLogMode(x=False, y=False)                     # False代表线性坐标轴，True代表对数坐标轴
        # p1.addLegend()  # 可选择是否添加legend

        win.nextRow()                                       # layout换行，采用垂直排列，不添加此行则默认水平排列

        p2 = win.addPlot(title="轨迹收益")
        p2.setLabel('bottom', text='轨迹', color='#000000')
        p2.setLabel('left', text='收益',color='#000000')
        p2.showGrid(x=True, y=True)
        p2.setLogMode(x=False, y=False)
        # p2.addLegend()

        return win,p1,p2

    # 工作区面板
    def workSpaceLayout(self,centralwidget):
        gridLayout = QtWidgets.QGridLayout()

        self.line = QtWidgets.QFrame(centralwidget)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        gridLayout.addWidget(self.line, 0, 0, 1, 1)

        self.label_titleLoaded = QtWidgets.QLabel(centralwidget)
        self.label_titleLoaded.setAlignment(QtCore.Qt.AlignCenter)
        self.label_titleLoaded.setObjectName("label_titleLoaded")
        gridLayout.addWidget(self.label_titleLoaded, 1, 0, 1, 1)

        return gridLayout

    # 波形信息面板
    def waveLayout(self,centralwidget):
        gridLayout = QtWidgets.QGridLayout()

        self.line_2 = QtWidgets.QFrame(centralwidget)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        gridLayout.addWidget(self.line_2, 0, 0, 1, 2)

        self.label_titleWave = QtWidgets.QLabel(centralwidget)
        self.label_titleWave.setAlignment(QtCore.Qt.AlignCenter)
        self.label_titleWave.setObjectName("label_titleWave")
        gridLayout.addWidget(self.label_titleWave, 1, 0, 1, 2)

        self.lineEdit_waveName = QtWidgets.QLineEdit(centralwidget)
        self.lineEdit_waveName.setObjectName("lineEdit_waveName")
        gridLayout.addWidget(self.lineEdit_waveName, 2, 0, 1, 2)

        self.label_showWave = QtWidgets.QLabel(centralwidget)
        self.label_showWave.setObjectName("label_showWave")
        gridLayout.addWidget(self.label_showWave, 3, 0, 1, 1)
        self.checkBox_showWave = QtWidgets.QCheckBox(centralwidget)
        self.checkBox_showWave.setText("")
        self.checkBox_showWave.setObjectName("checkBox_showWave")
        gridLayout.addWidget(self.checkBox_showWave, 3, 1, 1, 1)

        self.label_waveColor = QtWidgets.QLabel(centralwidget)
        self.label_waveColor.setObjectName("label_waveColor")
        gridLayout.addWidget(self.label_waveColor, 4, 0, 1, 1)
        self.pbt_waveColor = QtWidgets.QPushButton(centralwidget)
        self.pbt_waveColor.setObjectName("pbt_waveColor")
        gridLayout.addWidget(self.pbt_waveColor, 4, 1, 1, 1)

        self.pbt_saveWave = QtWidgets.QPushButton(self.centralwidget)
        self.pbt_saveWave.setObjectName('pbt_saveWave')
        self.pbt_saveWave.clicked.connect(lambda:self.saveFileDialog.showWidget(self.waveSelected.name))
        gridLayout.addWidget(self.pbt_saveWave, 5, 0, 1, 2)    

        self.pbt_removeWave = QtWidgets.QPushButton(centralwidget)
        self.pbt_removeWave.setObjectName("pbt_removeWave")
        gridLayout.addWidget(self.pbt_removeWave, 6, 0, 1, 2)       

        self.setWaveLayoutEnabled(False)

        return gridLayout

    # 全局控制面板
    def globalLayout(self,centralwidget):
        gridLayout = QtWidgets.QGridLayout()

        self.label_titleGlobal = QtWidgets.QLabel(centralwidget)
        self.label_titleGlobal.setAlignment(QtCore.Qt.AlignCenter)
        self.label_titleGlobal.setObjectName("label_titleGlobal")
        gridLayout.addWidget(self.label_titleGlobal, 0, 0, 1, 2)

        self.label_MALength = QtWidgets.QLabel(centralwidget)
        self.label_MALength.setObjectName("label_MALength")
        gridLayout.addWidget(self.label_MALength, 1, 0, 1, 1)
        self.spinBox_MALength = QtWidgets.QSpinBox(centralwidget)
        self.spinBox_MALength.setObjectName("spinBox_MALength")
        self.spinBox_MALength.setMinimum(1)
        self.spinBox_MALength.setValue(self.filterL)
        gridLayout.addWidget(self.spinBox_MALength, 1, 1, 1, 1)

        self.label_alpha = QtWidgets.QLabel(centralwidget)
        self.label_alpha.setObjectName("label_alpha")
        gridLayout.addWidget(self.label_alpha, 2, 0, 1, 1)
        self.spinBox_alpha = QtWidgets.QSpinBox(centralwidget)
        self.spinBox_alpha.setObjectName("spinBox_alpha")
        self.spinBox_alpha.setMaximum(255)
        self.spinBox_alpha.setValue(self.alpha)
        gridLayout.addWidget(self.spinBox_alpha, 2, 1, 1, 1)
        
        self.pbt_showAll = QtWidgets.QPushButton(centralwidget)
        self.pbt_showAll.setObjectName("pbt_showAll")
        gridLayout.addWidget(self.pbt_showAll, 3, 0, 1, 1)
        self.pbt_clearAll = QtWidgets.QPushButton(centralwidget)
        self.pbt_clearAll.setObjectName("pbt_clearAll")
        gridLayout.addWidget(self.pbt_clearAll, 3, 1, 1, 1)

        self.pbt_loadWave = QtWidgets.QPushButton(centralwidget)
        self.pbt_loadWave.setObjectName("pbt_loadWave")
        gridLayout.addWidget(self.pbt_loadWave, 4, 0, 1, 1)
        self.pbt_removeAll = QtWidgets.QPushButton(centralwidget)
        self.pbt_removeAll.setObjectName("pbt_removeAll")
        gridLayout.addWidget(self.pbt_removeAll, 4, 1, 1, 1)

        self.pbt_ave = QtWidgets.QPushButton(centralwidget)
        self.pbt_ave.setObjectName("pbt_genFigure")
        gridLayout.addWidget(self.pbt_ave, 5, 0, 1, 2)

        self.pbt_genFigure = QtWidgets.QPushButton(centralwidget)
        self.pbt_genFigure.setObjectName("pbt_genFigure")
        gridLayout.addWidget(self.pbt_genFigure, 6, 0, 1, 2)

        return gridLayout

    # 建立UI
    def setupUi(self):
        self.setObjectName("MainWindow")
        self.resize(1029, 750)
        self.setWindowIcon(QtGui.QIcon('src/images/grid.png'))
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("figure centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")

        graphWidget,self.p1,self.p2 = self.graphWidget()
        graphWidget.setObjectName("graphWidget")
        self.horizontalLayout.addWidget(graphWidget)

        # 垂直分隔线
        self.line_3 = QtWidgets.QFrame(self.centralwidget)
        self.line_3.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.horizontalLayout.addWidget(self.line_3)

        # 控制面板
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.globalControlLayout = self.globalLayout(self.centralwidget)
        self.waveControlLayout = self.waveLayout(self.centralwidget)
        self.wavesLayout = self.workSpaceLayout(self.centralwidget)
        
        self.verticalLayout.addLayout(self.globalControlLayout)     
        self.verticalLayout.addItem(QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))
        self.verticalLayout.addLayout(self.waveControlLayout)
        self.verticalLayout.addItem(QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))
        self.verticalLayout.addLayout(self.wavesLayout)
        self.verticalLayout.addItem(QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))

        self.horizontalLayout.addLayout(self.verticalLayout)
        self.horizontalLayout.setStretch(0, 1)
        self.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1029, 23))
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

        self.connectSignalAndSlot()

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "Figure Generator"))
        self.pbt_loadWave.setText(_translate("MainWindow", "加载波形"))
        self.label_MALength.setText(_translate("MainWindow", "滤波长度："))
        self.label_titleLoaded.setText(_translate("MainWindow", "已加载波形"))
        self.label_alpha.setText(_translate("MainWindow", "透明度："))
        self.pbt_saveWave.setText(_translate("MainWindow", "保存波形文件"))
        self.pbt_removeWave.setText(_translate("MainWindow", "从工作区移除"))
        self.label_titleGlobal.setText(_translate("MainWindow", "全局控制"))
        self.label_showWave.setText(_translate("MainWindow", "显示波形："))
        self.pbt_showAll.setText(_translate("MainWindow", "全部显示"))
        self.pbt_clearAll.setText(_translate("MainWindow", "全部隐藏"))
        self.label_waveColor.setText(_translate("MainWindow", "波形颜色："))
        self.label_titleWave.setText(_translate("MainWindow", "波形控制"))
        self.pbt_removeAll.setText(_translate("MainWindow", "全部移除"))
        self.pbt_genFigure.setText(_translate("MainWindow", "制图"))
        self.pbt_ave.setText(_translate("MainWindow", "平均化"))

    def connectSignalAndSlot(self):
        self.spinBox_MALength.valueChanged.connect(self.setFilterL)
        self.spinBox_alpha.valueChanged.connect(self.setAlpha)

        self.pbt_showAll.clicked.connect(lambda:self.setAllWavesVisible(True))
        self.pbt_clearAll.clicked.connect(lambda:self.setAllWavesVisible(False))
        self.pbt_removeAll.clicked.connect(self.removeAllWaves)
        self.pbt_removeAll.clicked.connect(self.loadWaveDialog.treeWidget.selectNoFiles)
        self.pbt_loadWave.clicked.connect(self.loadWaveDialog.showWidget)
        self.loadWaveDialog.loadWaveSignal.connect(self.loadWave)

        self.lineEdit_waveName.textChanged.connect(self.setSelectedWaveName)
        self.pbt_waveColor.clicked.connect(self.setSelectedWaveColor)
        self.pbt_removeWave.clicked.connect(self.removeSelectedWave)
        self.checkBox_showWave.clicked.connect(self.setSelectedWaveVisiable)

        self.pbt_ave.clicked.connect(self.aveWave)
        self.pbt_genFigure.clicked.connect(self.genLineChart)

        self.saveFileDialog.saveWaveSignal.connect(self.saveWave)

    # 清空波形信息面板
    def clearWaveLayout(self):
        self.pbt_waveColor.setStyleSheet('QPushButton{background:#BBBBBB;}')
        self.lineEdit_waveName.setText('')
        self.checkBox_showWave.setChecked(False)

    # 波形信息面板使能/失能
    def setWaveLayoutEnabled(self,enabled):
        self.pbt_waveColor.setEnabled(enabled)
        self.lineEdit_waveName.setEnabled(enabled)
        self.checkBox_showWave.setEnabled(enabled)
        self.pbt_removeWave.setEnabled(enabled)

    # 设定滑动滤波buffer长度
    def setFilterL(self):
        self.filterL = int(self.spinBox_MALength.value())
        self.updateAllWaves()
    
    # 设定原始数据透明度
    def setAlpha(self):
        self.alpha = int(self.spinBox_alpha.value())
        self.updateAllWaves()

    # ========================================================================
    # 显示/隐藏所有波形
    def setAllWavesVisible(self,visible):
        for wave in self.loadedWave:
            wave.isVisible = visible
        self.checkBox_showWave.setChecked(visible)
        self.updateAllWaves()

    # 显示/隐藏选中波形
    def setSelectedWaveVisiable(self):
        self.waveSelected.isVisible = self.checkBox_showWave.isChecked()
        self.updateAllWaves()

    # 加载波形到工作区
    def loadWave(self,wavePathList):
        self.loadWaveDialog.textBrowser.setText('')
        self.removeAllWaves()

        statusText,waveData = '',None
        for path in wavePathList:
            status,waveData = self.waveFile.loadWave(path)
            statusText += status+'\n\n'
            if status[-8:] != 'Success!':
                if path in self.loadWaveDialog.treeWidget.wavePathList:
                    self.loadWaveDialog.treeWidget.wavePathList.remove(path)
            else:
                if not waveData in self.loadedWave:
                    waveData.isVisible = True
                    waveData.color = tuple(np.random.choice(100, 3, replace=False)+60) # 从60~160间随机取3个数作为颜色
                    self.loadedWave.append(waveData)
            #else:
            #    self.loadWaveDialog.textBrowser.setText('此波形已存在于工作区')

            '''
            WD = wd(waveData.returnArray,waveData.lengthArray)
            WD.name = waveData.name 
            WD.path = waveData.path
            self.waveFile.saveWave(WD)
            '''

        if waveData != None:
            self.showWaveInfo(waveData)
        self.updateAllWaves()
        self.updateWorkSpace()

        self.loadWaveDialog.textBrowser.setText(statusText)
        self.loadWaveDialog.treeWidget.refreshCurrentFileTree()

    # 把选中的波形从工作区移除
    def removeSelectedWave(self):
        index = self.loadedWave.index(self.waveSelected)
        del self.loadedWave[index]
        self.waveSelected = None
        self.clearWaveLayout()
        self.setWaveLayoutEnabled(False)
        self.updateAllWaves()
        self.updateWorkSpace()
        
    # 把所有波形从工作区移除
    def removeAllWaves(self):
        self.loadedWave.clear()
        self.waveSelected = None
        self.clearWaveLayout()
        self.setWaveLayoutEnabled(False)
        self.updateAllWaves()
        self.updateWorkSpace()

    # 选中波形显示其信息
    def showWaveInfo(self,wave):
        self.setWaveLayoutEnabled(True)
        self.waveSelected = wave
        self.lineEdit_waveName.setText(wave.name)
        self.checkBox_showWave.setChecked(wave.isVisible)
        self.pbt_waveColor.setStyleSheet('QPushButton{background:%s;}'%RGB2Hex(wave.color))

    # 设置选中波形颜色
    def setSelectedWaveColor(self):
        col = QtWidgets.QColorDialog.getColor() 
        if col.isValid(): 
            self.waveSelected.color = Hex2RGB(col.name())
            self.pbt_waveColor.setStyleSheet('QPushButton{background:%s;}'%col.name())
        self.updateWorkSpace()
        self.updateAllWaves()
    
    # 设置选中波形的名字
    def setSelectedWaveName(self):
        if self.loadedWave != []:
            try:
                self.waveSelected.name = str(self.lineEdit_waveName.text())
                self.updateWorkSpace()
            except Exception:
                pass

    # 清空工作区
    def clearWorkSpace(self):
        i = 0
        while True:
            try:
                self.wavesLayout.itemAt(2+i).widget().deleteLater()
                i += 1
            except Exception:
                break

    # 刷新工作区
    def updateWorkSpace(self):
        self.clearWorkSpace()

        for i in range(len(self.loadedWave)):
            wave = self.loadedWave[i]
            pbt_wave = QtWidgets.QPushButton(self.centralwidget)
            pbt_wave.setText(wave.name)
            pbt_wave.setStyleSheet('QPushButton{background:%s;}'%RGB2Hex(wave.color))
            pbt_wave.clicked.connect(partial(self.showWaveInfo,self.loadedWave[i]))
            self.wavesLayout.addWidget(pbt_wave, 2+i, 0, 1, 1)

    # 刷新波形显示
    def updateAllWaves(self):
        try:
            self.p1.clear()
            self.p2.clear()
            for wave in self.loadedWave:
                if wave.isVisible:
                    fl = np.convolve(wave.lengthArray, np.ones((self.filterL,))/self.filterL, mode='valid') # 一维卷积实现滑动均值滤波
                    fr = np.convolve(wave.returnArray, np.ones((self.filterL,))/self.filterL, mode='valid')  
                    x = np.arange(0.5*self.filterL,0.5*self.filterL+fl.shape[0])                            # 滤波后数据，显示时跳过数据不完全重叠的边际部分

                    self.p1.plot(wave.lengthArray,pen=wave.color+(255-self.alpha,))                             # 原始数据，透明显示
                    self.p2.plot(wave.returnArray,pen=wave.color+(255-self.alpha,))                             # 原始数据，透明显示
                    self.p1.plot(x,fl,pen=wave.color)   
                    self.p2.plot(x,fr,pen=wave.color)   
        except Exception as e:
            self.statusBar().showMessage('图表生成器错误：'+str(e),2000)
            print('图表生成器错误：',e)
    
    # 生成折线图
    def genLineChart(self):
        # 这两行代码解决 plt 中文显示的问题
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False

        plt.rcParams['font.size'] = 14

        fig = plt.figure(figsize=(9,12))
        a1 = fig.add_subplot(2,1,1,label='a1')
        a2 = fig.add_subplot(2,1,2,label='a2')
        
        a1.set_xlabel('轨迹')
        a1.set_ylabel('长度')
        a2.set_xlabel('轨迹')
        a2.set_ylabel('收益')
        
        # 输入纵坐标轴数据与横坐标轴数据
        for wave in self.loadedWave:
            if wave.isVisible:
                fl = np.convolve(wave.lengthArray, np.ones((self.filterL,))/self.filterL, mode='valid') # 一维卷积实现滑动均值滤波
                fr = np.convolve(wave.returnArray, np.ones((self.filterL,))/self.filterL, mode='valid')  
                x = np.arange(0.5*self.filterL,0.5*self.filterL+fl.shape[0])                            # 滤波后数据，显示时跳过数据不完全重叠的边际部分

                a1.plot(wave.lengthArray, '.-', markersize='0',color=RGB2Hex(wave.color),alpha=1-self.alpha/255,linewidth=1)
                a1.plot(x,fl, '.-',label=wave.name,markersize='0',color=RGB2Hex(wave.color),linewidth=1)

                a2.plot(wave.returnArray, '.-', markersize='0',color=RGB2Hex(wave.color),alpha=1-self.alpha/255,linewidth=1)
                a2.plot(x,fr, '.-',label=wave.name,markersize='0',color=RGB2Hex(wave.color),linewidth=1)                

        a1.legend(fontsize=10) # 显示图例，即每条线对应 label 中的内容
        a2.legend(fontsize=10)

        plt.show() # 显示图形

        #self.genLineChart2()
        #self.genBarGraph()

    # 生成均值折线图
    def genLineChart2(self):
        # 这两行代码解决 plt 中文显示的问题
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False

        plt.rcParams['font.size'] = 14

        fig = plt.figure(figsize=(9,12))
        a1 = fig.add_subplot(2,1,1,label='a1')
        a2 = fig.add_subplot(2,1,2,label='a2')
        
        a1.set_xticks(range(1,6))
        a1.set_xlabel('收集次数n')
        a1.set_ylabel('平均长度')
        a2.set_xticks(range(1,6))
        a2.set_xlabel('收集次数n')
        a2.set_ylabel('平均收益')
        
        x = []
        aveLen = []
        aveRet = []

        # 输入纵坐标轴数据与横坐标轴数据
        for wave in self.loadedWave:
            if wave.isVisible:
                aveLen.append(np.average(wave.lengthArray))
                aveRet.append(np.average(wave.returnArray))
                x.append(float(wave.name[wave.name.rfind('=')+1:]))

        a1.plot(x,aveLen, '.-',markersize='10',color='k',linewidth=1)
        a2.plot(x,aveRet, '.-',markersize='10',color='k',linewidth=1)                

        plt.show() # 显示图形

    # 生成均值柱状图
    def genBarGraph(self):
        # 这两行代码解决 plt 中文显示的问题
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False

        fig = plt.figure(figsize=(9,12))
        a1 = fig.add_subplot(2,1,1,label='a1')
        a2 = fig.add_subplot(2,1,2,label='a2')

        algo = []
        aveLen = []
        aveRet = []
        
        for wave in self.loadedWave:
            if wave.isVisible:
                aveLen.append(np.average(wave.lengthArray))
                aveRet.append(np.average(wave.returnArray))
                algo.append(wave.name)

        x_pos = range(len(algo)) # [0, 1, 2, 3, 4, 5, 6]

        #绘制柱状图
        rect = a1.bar(x = x_pos,
                    height = aveLen,
                    color = "lightblue")
        
        #通过rect对象，为每一个柱子添加顶部数值
        for rec in rect:
            x=rec.get_x()
            height = rec.get_height()
            a1.text(x+0.15,height*1+3.0,str(round(height,2)),fontsize = 14)
            
        #绘制柱状图
        rect = a2.bar(x = x_pos,
                    height = aveRet,
                    color = "lightblue")
        
        #通过rect对象，为每一个柱子添加顶部数值
        for rec in rect:
            x=rec.get_x()
            height = rec.get_height()
            a2.text(x+0.15,height*0.98-3.0,str(round(height,2)),fontsize = 14)

        a1.bar(x_pos, aveLen, align='center', alpha=0.5)
        a1.set_xticks(x_pos)
        a1.set_xticklabels(algo,fontsize = 14)
        a1.set_ylabel('平均长度',fontsize = 14)

        a2.bar(x_pos, aveRet, align='center', alpha=0.5)
        a2.set_xticks(x_pos)
        a2.set_xticklabels(algo,fontsize = 14)
        a2.set_ylabel('平均奖励',fontsize = 14)

        plt.title('')
        plt.show() # 显示图形

    # 平均化所有当前显示的波形
    def aveWave(self):
        minLen = 1e6
        num = 0
        for wave in self.loadedWave:
            if wave.isVisible:
                num += 1
                if wave.returnArray.shape[0] < minLen:
                    minLen = wave.returnArray.shape[0]

        if num == 0:
            return
        
        ave = WaveData(np.zeros(minLen),np.zeros(minLen))
        for wave in self.loadedWave:
            if wave.isVisible:
                ave.returnArray += wave.returnArray[:minLen]
                ave.lengthArray += wave.lengthArray[:minLen]
        ave.returnArray /= num
        ave.lengthArray /= num

        ave.name = 'new average wave'
        ave.isVisible = True
        ave.color = tuple(np.random.choice(100, 3, replace=False)+30) # 从30~130间随机取3个数作为颜色
        self.loadedWave.append(ave)
        self.showWaveInfo(ave)
        self.updateAllWaves()
        self.updateWorkSpace()
        self.loadWaveDialog.close()

    # 保存界面信号槽函数，把当前wave存储到filePath
    def saveWave(self,filePath,fileName):
        self.waveSelected.name = fileName
        self.waveSelected.path = filePath
        self.waveFile.saveWave(self.waveSelected)

    # 生成SVM二分类图，用于ecoc方法
    def plotSVC(self,dataSet,labelSet,score,model,size=(6,6)):
        print(dataSet)
        print(labelSet)

        self.fig = plt.figure(figsize=size)

        # 数据点
        ax = plt.gca()
        ax.scatter(dataSet[:,0],dataSet[:,1],c=labelSet,s=50,alpha=0.5,cmap="rainbow",zorder=10,edgecolors='k')

        # 建立网格
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        x = np.linspace(xlim[0],xlim[1],50)         # (30,)
        y = np.linspace(ylim[0],ylim[1],50)         # (30,)
        YY,XX = np.meshgrid(y,x)                    # (30,30) (30,30)
        xy = np.vstack([XX.ravel(), YY.ravel()]).T  # (900,2)
        Z = model.decision_function(xy).reshape(XX.shape)    # (30,30)

        # 设定坐标轴为不显示
        #ax.set_xticks(())
        #ax.set_yticks(())

        # 绘制等高线
        CS = ax.contour(XX, YY, Z,colors="black",levels=[-1,0,1],alpha=0.8,linestyles=["--","-","--"],zorder=10)  # 三条等高线
        #CS = ax.contour(X, Y, Z,alpha=0.5)
        ax.clabel(CS, inline=1, fontsize=10)

        # 填充等高线不同区域的颜色
        ax.pcolormesh(XX, YY, Z > 0, shading='auto',zorder=0,cmap=plt.cm.Paired)

        # 为每张图添加分类的分数   
        ax.text(0.95, 0.06,                   # 文字位置
                ('%.2f' % score).lstrip('0'), # 精度
                size=15,
                zorder=7,
                bbox=dict(boxstyle='round', alpha=0.8, facecolor='white'), # 添加一个白色的格子作为底色
                transform=ax.transAxes,                                    # 确定文字所对应的坐标轴，就是ax子图的坐标轴本身
                horizontalalignment='right') #位于坐标轴的什么方向

        plt.gca().invert_yaxis()
        plt.show()


    