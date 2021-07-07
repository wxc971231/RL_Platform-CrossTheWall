from PyQt5 import QtCore, QtWidgets
import threading
import numpy as np
from core.Util import WaveData
from core.Algorithm.RL import BasePolicy
import abc

class BaseModelFreePolicy(BasePolicy,metaclass = abc.ABCMeta):
    updateWaveSignal = QtCore.pyqtSignal()

    def __init__(self,controller):
        super().__init__(controller) 

        self.waveData = WaveData(np.array([],dtype='float64'),np.array([],dtype='float64'))
        self.monitor = controller.monitor   # 实时折线图监视器
        self.planTimes = 20             # 规划次数
        self.episodeNum = 1             # 批量轨迹学习的轨迹数量
        self.diminishingEpsilon = False # 批量训练时是否试探递减

        self.TPLayout = None            # 训练计划面板
        self.MoniLayout = None          # 监视器面板

        # pyqtgraph需要在主线程更新
        self.updateWaveSignal.connect(self.monitor.updateWaves)

    # setter --------------------------------------------------------------------------
    def setDiminishingGamma(self):
        self.diminishingEpsilon = self.checkBox_episodesGamma.isChecked()

    def setEpisodeNum(self,episodeNum):
        self.episodeNum = episodeNum

    def setPlanTimes(self,times):
        self.planTimes = times

    # UI相关 ---------------------------------------------------------------------------
    def setLayoutVisiable(self,visible):
        layout = self.controlLayout()
        for i in range(layout.count()-2):    
            try:
                layout.itemAt(i).widget().setVisible(visible)
            except AttributeError:
                pass
            
        layout = self.trainingPlanLayout()
        for i in range(layout.count()):
            layout.itemAt(i).widget().setVisible(visible)

        layout = self.monitorLayout()
        for i in range(layout.count()):
            layout.itemAt(i).widget().setVisible(visible)

    # 批量episode训练计划面板
    def trainingPlanLayout(self):
        if self.TPLayout == None:
            Layout = QtWidgets.QGridLayout()
            spacerLabel = QtWidgets.QLabel(self.centralwidget)
            spacerLabel.setMinimumHeight(10)
            Layout.addWidget(spacerLabel, 0, 0, 1, 2)

            label_Title = QtWidgets.QLabel(self.centralwidget)
            label_Title.setText('批量轨迹')
            Layout.addWidget(label_Title, 1, 0, 1, 2, QtCore.Qt.AlignHCenter)

            self.label_episodesGamma = QtWidgets.QLabel(self.centralwidget)
            self.label_episodesGamma.setText('试探递减')
            Layout.addWidget(self.label_episodesGamma, 2, 0, 1, 1)
            self.checkBox_episodesGamma = QtWidgets.QCheckBox(self.centralwidget)
            self.checkBox_episodesGamma.setText("")
            self.checkBox_episodesGamma.setChecked(False)
            Layout.addWidget(self.checkBox_episodesGamma, 2, 1, 1, 1)

            self.label_batchEpsilon = QtWidgets.QLabel(self.centralwidget)
            self.label_batchEpsilon.setText("试探概率")
            Layout.addWidget(self.label_batchEpsilon, 3, 0, 1, 1)
            self.spinBox_batchEpsilon = QtWidgets.QDoubleSpinBox(self.centralwidget)
            self.spinBox_batchEpsilon.setMaximum(1.0)
            self.spinBox_batchEpsilon.setMinimum(0.0)
            self.spinBox_batchEpsilon.setValue(self.epsilon)
            self.spinBox_batchEpsilon.setSingleStep(0.01)
            Layout.addWidget(self.spinBox_batchEpsilon, 3, 1, 1, 1)  

            self.label_episodes = QtWidgets.QLabel(self.centralwidget)
            self.label_episodes.setText("轨迹数量")
            Layout.addWidget(self.label_episodes, 4, 0, 1, 1)
            self.spinBox_episodes = QtWidgets.QSpinBox(self.centralwidget)
            self.spinBox_episodes.setMaximum(10000)
            self.spinBox_episodes.setMinimum(1)
            self.spinBox_episodes.setValue(1)
            Layout.addWidget(self.spinBox_episodes, 4, 1, 1, 1)  

            self.pbt_episodes = QtWidgets.QPushButton(self.centralwidget)
            self.pbt_episodes.setText('Start')
            Layout.addWidget(self.pbt_episodes, 5, 0, 1, 2)
            
            self.TPLayout = Layout

        return self.TPLayout

    # 监视器面板
    def monitorLayout(self):
        if self.MoniLayout == None:
            Layout = QtWidgets.QGridLayout()
            spacerLabel = QtWidgets.QLabel(self.centralwidget)
            spacerLabel.setMinimumHeight(10)
            Layout.addWidget(spacerLabel, 0, 0, 1, 1)

            label_Title = QtWidgets.QLabel(self.centralwidget)
            label_Title.setText('监视器')
            Layout.addWidget(label_Title, 1, 0, 1, 1, QtCore.Qt.AlignHCenter)

            self.pbt_monitor = QtWidgets.QPushButton(self.centralwidget)
            self.pbt_monitor.setText('monitor')
            Layout.addWidget(self.pbt_monitor, 2, 0, 1, 1)
        
            self.MoniLayout = Layout

        return self.MoniLayout

    def showMonitor(self):
        if not self.monitor.updating:
            self.monitor.initWaves(self.waveData)
            self.monitor.show()
        else:
            self.monitor.close()

    def clearMonitor(self):
        self.waveData.clear()
        self.monitor.clearWaves()

    # 控制 ------------------------------------------------------------------------------
    def autoToggle(self,mode):
        if self.autoExec:
            if mode == 'auto':
                self.pbt_toggleAuto.setText('auto')
                self.pbt_episodes.setEnabled(True)
            elif mode == 'episodes':
                self.pbt_episodes.setText('episodes')
                self.pbt_toggleAuto.setEnabled(True)
            else:
                assert False

            self.waitAutoExecEnd()
        else:   # 启动子线程自动执行策略
            self.autoExec = True
            if mode == 'auto':
                self.pbt_toggleAuto.setText('stop')
                self.pbt_episodes.setEnabled(False)
                self.autoThread = threading.Thread(target = self.infinityEpisodes)
            elif mode == 'episodes':
                self.pbt_episodes.setText('stop')
                self.pbt_toggleAuto.setEnabled(False)
                self.autoThread = threading.Thread(target = self.episodes)
            else:
                assert False

            self.autoThread.setDaemon(True)
            self.autoThread.start()  

    # 复位策略
    def resetPolicy(self):
        self.waitAutoExecEnd()
        self.initPolicy()       # 初始化为随机策略，动作价值函数都初始化为0
        self.map.gridWidget.update()
        self.monitor.clearMonitor()

    # 获取轨迹收益
    def getEpisodeReturn(self,rewards):
        episodeReturn = 0 
        rewards.reverse()
        for r in rewards:
            episodeReturn = self.gamma*episodeReturn + r

        return episodeReturn
        
    # 批量轨迹学习
    def episodes(self):
        epsilonSaved = self.epsilon                                     # 缓存初始self.epsilon 
        batchEpsilonSaved = float(self.spinBox_batchEpsilon.value())    # 缓存初始试探概率

        self.epsilon = batchEpsilonSaved                                
        delta = (self.diminishingEpsilon)*self.epsilon/self.episodeNum  # 试探概率变化步进

        for i in range(self.episodeNum):
            l,r = self.episode()    # 轨迹length，轨迹return
            if l != -1:
                self.waveData.appendData(r,l)
                self.label_info.setText('采样轨迹{};\n长度{}'.format(self.waveData.dataNum,round(l,3)))
                if self.monitor.updating:
                    self.updateWaveSignal.emit()
            self.epsilon -= delta
            if self.epsilon < 0: self.epsilon = 0
            self.spinBox_batchEpsilon.setValue(self.epsilon)

        self.autoExec = False
        self.pbt_episodes.setText('episodes')
        self.pbt_toggleAuto.setEnabled(True)
        
        self.epsilon = epsilonSaved                             
        self.spinBox_batchEpsilon.setValue(batchEpsilonSaved)
        
    # 无限轨迹学习
    def infinityEpisodes(self):
        while self.autoExec:
            l,r = self.episode()
            if l != -1:
                self.waveData.appendData(r,l)
                self.label_info.setText('采样轨迹{};\n长度{}'.format(self.waveData.dataNum,round(l,3)))
                if self.monitor.updating:
                    self.updateWaveSignal.emit()
                    
        self.pbt_toggleAuto.setText('auto')
        self.pbt_episodes.setEnabled(True)


    # 子类方法 ---------------------------------------------------------------------------
    # (此方法子类必须重写) 在此创建并返回一个包含策略控制控件的Layout
    @abc.abstractmethod
    def controlLayout(self):
        pass

    # (此方法子类必须重写) 策略控制layout嵌入controller主窗口时调用，在此初始化
    @abc.abstractmethod
    def controlLayoutInit(self):
        pass

    # (此方法子类必须重写) 策略控制layout从controller主窗口移除时调用，在此做收尾处理
    @abc.abstractmethod
    def controlLayoutRemoved(self):
        pass
    
    # (此方法子类必须重写) 采样一条轨迹进行学习，返回轨迹长度及收益
    @abc.abstractmethod
    def episode(self):
        length = 0
        rewards = []
        # ...
        return length,self.getEpisodeReturn(rewards)

    