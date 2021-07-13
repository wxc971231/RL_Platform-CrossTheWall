from PyQt5 import QtCore, QtWidgets
import time
from core.Util.Function import greedyChoise,getActionByEpsilonGreedy
from core.Algorithm.RL import BaseModelFreePolicy

class QLearning(BaseModelFreePolicy):
    def __init__(self,controller):
        super().__init__(controller) 

    # 控制UI（执行此策略时嵌入到controller窗口中）
    def controlLayout(self):
        if self.layout == None:
            Layout = QtWidgets.QGridLayout()
            self.label_Title = QtWidgets.QLabel(self.centralwidget)
            self.label_Title.setText('Q-Learning')
            Layout.addWidget(self.label_Title, 0, 0, 1, 2, QtCore.Qt.AlignHCenter)
            self.label_gamma = QtWidgets.QLabel(self.centralwidget)
            self.label_gamma.setText("折扣系数")
            Layout.addWidget(self.label_gamma, 1, 0, 1, 1)
            self.spinBox_gamma = QtWidgets.QDoubleSpinBox(self.centralwidget)
            self.spinBox_gamma.setObjectName("spinBox_gamma")
            self.spinBox_gamma.setMaximum(1.0)
            self.spinBox_gamma.setMinimum(0.0)
            self.spinBox_gamma.setValue(self.gamma)
            self.spinBox_gamma.setSingleStep(0.01)
            Layout.addWidget(self.spinBox_gamma, 1, 1, 1, 1)  

            self.label_alpha = QtWidgets.QLabel(self.centralwidget)
            self.label_alpha.setText("学习率")
            Layout.addWidget(self.label_alpha, 2, 0, 1, 1)
            self.spinBox_alpha = QtWidgets.QDoubleSpinBox(self.centralwidget)
            self.spinBox_alpha.setMaximum(1.0)
            self.spinBox_alpha.setMinimum(0.01)
            self.spinBox_alpha.setValue(self.alpha)
            self.spinBox_alpha.setSingleStep(0.01)
            Layout.addWidget(self.spinBox_alpha, 2, 1, 1, 1)  

            self.label_epsilon = QtWidgets.QLabel(self.centralwidget)
            self.label_epsilon.setText("试探概率")
            Layout.addWidget(self.label_epsilon, 3, 0, 1, 1)
            self.spinBox_epsilon = QtWidgets.QDoubleSpinBox(self.centralwidget)
            self.spinBox_epsilon.setMaximum(1.0)
            self.spinBox_epsilon.setMinimum(0.0)
            self.spinBox_epsilon.setValue(self.epsilon)
            self.spinBox_epsilon.setSingleStep(0.01)
            Layout.addWidget(self.spinBox_epsilon, 3, 1, 1, 1)  

            self.pbt_toggleAuto = QtWidgets.QPushButton(self.centralwidget)
            self.pbt_toggleAuto.setText('auto')
            Layout.addWidget(self.pbt_toggleAuto, 4, 0, 1, 2)
            
            self.pbt_resetPi = QtWidgets.QPushButton(self.centralwidget)
            self.pbt_resetPi.setText('reset')
            Layout.addWidget(self.pbt_resetPi, 5, 0, 1, 2)
            self.label_info = QtWidgets.QLabel(self.centralwidget)
            self.label_info.setText('采样轨迹0; 长度0')
            Layout.addWidget(self.label_info, 6, 0, 1, 2)

            Layout.addLayout(self.trainingPlanLayout(), 7, 0, 1, 2) # 批量轨迹训练面板
            Layout.addLayout(self.monitorLayout(), 8, 0, 1, 2)      # 监视器面板
            
            self.controller.pbt_edit.clicked.connect(self.resetPolicy)
            self.controller.policyReloadSignal.connect(self.resetPolicy)
            self.map.reloadSignal.connect(self.resetPolicy)
            self.pbt_resetPi.clicked.connect(self.resetPolicy)
            self.pbt_monitor.clicked.connect(self.showMonitor)
            self.checkBox_episodesGamma.clicked.connect(self.setDiminishingGamma)
            self.spinBox_episodes.valueChanged.connect(lambda:self.setEpisodeNum(int(self.spinBox_episodes.value())))
            self.pbt_episodes.clicked.connect(lambda:self.autoToggle('episodes'))

            self.pbt_toggleAuto.clicked.connect(lambda:self.autoToggle('auto'))
            self.spinBox_gamma.valueChanged.connect(lambda:self.setGamma(float(self.spinBox_gamma.value())))
            self.spinBox_alpha.valueChanged.connect(lambda:self.setAlpha(float(self.spinBox_alpha.value())))
            self.spinBox_epsilon.valueChanged.connect(lambda:self.setEpsilon(float(self.spinBox_epsilon.value())))
            
            self.layout = Layout

        return self.layout 
        
    def controlLayoutInit(self):
        self.controller.spinBox_UIStep.setValue(10) # 设定UI更新周期（触发槽函数）
        self.initPolicy()  
        self.setLayoutVisiable(True)

    def controlLayoutRemoved(self):
        self.setLayoutVisiable(False)
        self.waitAutoExecEnd()

    def resetPolicy(self):
        self.waitAutoExecEnd()
        self.initPolicy()       # 初始化为随机策略，动作价值函数都初始化为0
        self.map.gridWidget.update()
        self.label_info.setText('采样轨迹0; 长度0')

        self.clearMonitor()         # 清空监视器
      
    def learnFromTuple(self,S,A,R,S_,A_):
        S.Q[A] = S.Q[A] + self.alpha*(R + self.gamma*S_.Q[A_]-S.Q[A])
        
        # 更新策略pi(Q-learning中仅用于UI显示)
        S.updatePolicyByQ()  
        S.value = 0          
        for a in S.action:
            S.value += S.pi[a]*S.Q[a]
        
    def episode(self):
        stepCnt = 0
        length = 0
        rewards = []

        # 初始状态s设为起点
        S = self.map.startCube
        S.agentLocated = True
                
        while self.autoExec:
            # 行动策略：epsilon-greedy选出A
            A = getActionByEpsilonGreedy(self.epsilon,S)

            # 执行A，观测到R和S_
            S_ = S.nextCubeDict[A]
            R = S.reward - (S != self.map.endCube)*self.map.disCostDiscount*S.distance(S_)
            rewards.append(R)
            length += S.distance(S_)

            # 目标策略：greedy选择A_  
            A_ = greedyChoise(S_.Q)         
            
            # 一步Q-Learning更新
            self.learnFromTuple(S,A,R,S_,A_)

            # 在ui显示当前策略
            if self.controller.realTimeUI:
                if self.controller.timeStep > 0:
                    time.sleep(self.controller.timeStep)
                if stepCnt % self.controller.UIStep == 0:
                    self.map.gridWidget.update()
                
            # 轨迹终止条件
            if S == self.map.endCube:
                S.agentLocated = False
                break
            
            S.agentLocated,S_.agentLocated = False,True
            S = S_
            stepCnt += 1
             
        # 手动终止，清除agent位置标记
        if not self.autoExec:
            S.agentLocated = False
            self.map.gridWidget.update()
            return -1,-1

        return length,self.getEpisodeReturn(rewards)


