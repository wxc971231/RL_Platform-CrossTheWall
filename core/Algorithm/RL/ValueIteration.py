from PyQt5 import QtCore, QtWidgets
from core.Algorithm.RL import BasePolicy
import threading
import time

class ValueIteration(BasePolicy):
    def __init__(self,controller):
        super().__init__(controller) 

    # 控制UI（执行此策略时嵌入到controller窗口中）
    def controlLayout(self):
        if self.layout == None:
            Layout = QtWidgets.QGridLayout()
            self.label_Title = QtWidgets.QLabel(self.centralwidget)
            self.label_Title.setText('Value Iteration')
            Layout.addWidget(self.label_Title, 0, 0, 1, 2, QtCore.Qt.AlignHCenter)
            self.label_gamma = QtWidgets.QLabel(self.centralwidget)
            self.label_gamma.setText("折扣系数")
            Layout.addWidget(self.label_gamma, 1, 0, 1, 1)
            self.spinBox_gamma = QtWidgets.QDoubleSpinBox(self.centralwidget)
            self.spinBox_gamma.setObjectName("spinBox_gamma")
            self.spinBox_gamma.setMaximum(1.0)
            self.spinBox_gamma.setMinimum(0.0)
            self.spinBox_gamma.setValue(0.9)
            self.spinBox_gamma.setSingleStep(0.01)
            Layout.addWidget(self.spinBox_gamma, 1, 1, 1, 1)  

            self.pbt_toggleAuto = QtWidgets.QPushButton(self.centralwidget)
            self.pbt_toggleAuto.setText('value optimal')
            Layout.addWidget(self.pbt_toggleAuto,2, 0, 1, 2)
            self.pbt_resetPi = QtWidgets.QPushButton(self.centralwidget)
            self.pbt_resetPi.setText('reset')
            Layout.addWidget(self.pbt_resetPi, 3, 0, 1, 2)
            self.label_info = QtWidgets.QLabel(self.centralwidget)
            self.label_info.setText('价值迭代0; 修正0')
            Layout.addWidget(self.label_info, 4, 0, 1, 2)

            self.controller.pbt_edit.clicked.connect(self.resetPolicy)
            self.controller.policyReloadSignal.connect(self.resetPolicy)
            self.map.reloadSignal.connect(self.resetPolicy)
            self.pbt_resetPi.clicked.connect(self.resetPolicy)            
            self.pbt_toggleAuto.clicked.connect(self.autoToggle)
            self.spinBox_gamma.valueChanged.connect(lambda:self.setGamma(float(self.spinBox_gamma.value())))
            
            self.layout = Layout

        return self.layout 
        
    def controlLayoutInit(self):
        self.controller.spinBox_UIStep.setValue(1)  # 设定UI更新周期（触发槽函数）
        self.initPolicy()  
        self.setLayoutVisiable(True)

    def controlLayoutRemoved(self):
        self.setLayoutVisiable(False)
        self.waitAutoExecEnd()

    def autoToggle(self):
        if self.autoExec:
            self.pbt_toggleAuto.setText('value optimal')
            self.waitAutoExecEnd()
        else:   # 启动子线程自动执行策略
            self.autoExec = True
            self.pbt_toggleAuto.setText('policy optimal')
            self.autoThread = threading.Thread(target = self.autoValueIteration)
            self.autoThread.setDaemon(True)
            self.autoThread.start()    
    
    def resetPolicy(self):
        self.waitAutoExecEnd()
        self.initPolicy()
        self.label_info.setText('价值迭代0; 修正0')
        self.map.gridWidget.update()

    # 根据bellman optimal equation更新一次价值
    def updateValue(self):
        gridWidget = self.map.gridWidget
        for row in range(gridWidget.row):
            for colum in range(gridWidget.colum):
                cube = gridWidget.cubes[row][colum] 
                if cube.isPassable:
                    Q = cube.Q
                    
                    for a in cube.action:
                        nc = cube.nextCubeDict[a]
                        if nc != None:
                            disCost = (cube != self.map.endCube)*self.map.disCostDiscount*cube.distance(nc)

                            # Q(s,a) = R(s,a) + gamma*sum{p(s'|s,a)*V(s')}
                            Q[a] = cube.reward - disCost + self.gamma*nc.value  
                            #cube.updatePolicyByQ()

                    # v(s) = max_a(Q(s,a))
                    QSorted = sorted(Q.items(), key=lambda Q:Q[1], reverse=True) # 按值降序得元组列表                    
                    cube.value = QSorted[0][1]
        
        

    # 根据bellman optimal equation迭代优化价值函数收敛到 V*
    def optimalValue(self):
        lastV = self.map.gridWidget.getSumValue()
        self.updateValue()
        newV = self.map.gridWidget.getSumValue()
        self.label_info.setText('价值迭代1; 修正{}'.format(round(newV - lastV,5)))
        self.map.gridWidget.update()

        stepCnt = 2
        while self.autoExec:
            lastV = newV
            self.updateValue()
            newV = self.map.gridWidget.getSumValue()
            self.label_info.setText('价值迭代{}; 修正{}'.format(stepCnt,round(newV - lastV,5)))
            stepCnt += 1

            if self.controller.realTimeUI:
                if self.controller.timeStep > 0:
                    time.sleep(self.controller.timeStep)
                if stepCnt % self.controller.UIStep == 0:
                    self.map.gridWidget.update()
        
    # 先用V*构造Q*，再贪心得到最优策略pi*
    def optimalPolicy(self):
        gridWidget = self.map.gridWidget
        for row in range(gridWidget.row):
            for colum in range(gridWidget.colum):
                cube = gridWidget.cubes[row][colum] 
                if cube.isPassable:

                    # 用V*构造Q*
                    Q = cube.Q
                    for a in cube.action:
                        nc = cube.nextCubeDict[a]
                        if nc != None:
                            disCost = (cube != self.map.endCube)*self.map.disCostDiscount*cube.distance(nc)

                            # Q(s,a) = R(s,a) + gamma*sum{p(s'|s,a)*V(s')}
                            Q[a] = cube.reward - disCost + self.gamma*nc.value  

                    # 在Q*上贪心得到策略pi*，相同价值的动作平分概率
                    cube.updatePolicyByQ()
                    self.pi[row][colum] = cube.pi
        gridWidget.update()

    def autoValueIteration(self):
        self.optimalValue()
        self.optimalPolicy()
        self.autoExec = False
