from PyQt5 import QtCore, QtWidgets
from core.Algorithm.RL import BasePolicy
import threading
import time

class PolicyIteration(BasePolicy):
    def __init__(self,controller):
        super().__init__(controller) 
        self.controller = controller
        self.improveTimes = 0       # 策略提升次数
        self.evaluationTimes = 0    # 策略评估次数
        self.sumValue = 0           # 当前总状态价值

        self.stepCnt = 0            # 策略评估计数

    # 控制UI（执行此策略时嵌入到controller窗口中）
    def controlLayout(self):
        if self.layout == None:
            Layout = QtWidgets.QGridLayout()
            self.label_Title = QtWidgets.QLabel(self.centralwidget)
            self.label_Title.setText('Policy Iteration')
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

            self.pbt_policyEvaluation = QtWidgets.QPushButton(self.centralwidget)
            self.pbt_policyEvaluation.setText('Evaluation')
            Layout.addWidget(self.pbt_policyEvaluation, 2, 0, 1, 1)

            self.pbt_autoEvaluation = QtWidgets.QPushButton(self.centralwidget)
            self.pbt_autoEvaluation.setText('Auto Evaluation')
            Layout.addWidget(self.pbt_autoEvaluation, 3, 0, 1, 1)

            self.pbt_policyUpdate = QtWidgets.QPushButton(self.centralwidget)
            self.pbt_policyUpdate.setText('Update')
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
            self.pbt_policyUpdate.setSizePolicy(sizePolicy)
            Layout.addWidget(self.pbt_policyUpdate, 2, 1, 2, 1)            
            
            self.pbt_autoIteration = QtWidgets.QPushButton(self.centralwidget)
            self.pbt_autoIteration.setText('Full auto')
            Layout.addWidget(self.pbt_autoIteration, 4, 0, 1, 2)

            self.pbt_resetPi = QtWidgets.QPushButton(self.centralwidget)
            self.pbt_resetPi.setText('reset')
            Layout.addWidget(self.pbt_resetPi, 5, 0, 1, 2)
            self.label_info = QtWidgets.QLabel(self.centralwidget)
            self.label_info.setText('')
            Layout.addWidget(self.label_info, 6, 0, 1, 2)

            self.controller.pbt_edit.clicked.connect(self.resetPolicy)
            self.controller.policyReloadSignal.connect(self.resetPolicy)
            self.map.reloadSignal.connect(self.resetPolicy)
            self.pbt_resetPi.clicked.connect(self.resetPolicy)
            self.pbt_policyEvaluation.clicked.connect(self.policyEvaluationOneStep)
            self.pbt_policyUpdate.clicked.connect(self.policyImprove)
            self.pbt_autoEvaluation.clicked.connect(lambda:self.autoToggle('policy evaluation'))
            self.pbt_autoIteration.clicked.connect(lambda:self.autoToggle('policy iteratioin'))
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

    def autoToggle(self,mode):
        if self.autoExec:
            self.autoExec = False
            self.stepCnt = 0
            self.pbt_autoEvaluation.setEnabled(True)
            self.pbt_autoIteration.setEnabled(True)
            if mode == 'policy iteratioin':
                self.evaluationTimes = 0
                self.improveTimes = 0
        else:   # 启动子线程自动执行策略
            self.autoExec = True
            if mode == 'policy iteratioin':
                self.pbt_autoEvaluation.setEnabled(False)
                self.autoThread = threading.Thread(target = self.autoPolicyIteration)
            elif mode == 'policy evaluation':
                self.pbt_autoIteration.setEnabled(False)
                self.autoThread = threading.Thread(target = self.autoPolicyEvaluation)
            else:
                pass
            self.autoThread.setDaemon(True)
            self.autoThread.start()    

    # 执行一次策略评估
    def policyEvaluationOneStep(self):
        gridWidget = self.map.gridWidget

        # 计算所有方格的新价值
        newValue = []   
        for row in range(gridWidget.row):
            newValue_row = []
            for colum in range(gridWidget.colum):
                cube = gridWidget.cubes[row][colum]

                v = 0
                if cube.isPassable:
                    # V = sum{pi(a|s)*[R(s,a) + gamma*sum{p(s'|s,a)*V(s')}]}
                    for a in cube.action:                            
                        for nc,p in cube.nextCubeDict[a]:
                            if nc != None:
                                disCost = (cube not in self.map.endCubeList)*self.map.disCostDiscount*cube.distance(nc)
                                v = v + self.pi[row][colum][a]*(cube.reward - p*disCost + p*self.gamma*nc.value)
                newValue_row.append(v)
            newValue.append(newValue_row)

        # 更新价值
        for i in range(gridWidget.row):
            for j in range(gridWidget.colum):
                gridWidget.cubes[i][j].value = newValue[i][j]

        if self.controller.realTimeUI:
            if self.controller.timeStep > 0:
                time.sleep(self.controller.timeStep)
            if self.stepCnt % self.controller.UIStep == 0:
                self.map.gridWidget.update()
        self.stepCnt += 1

        sumValue = self.map.gridWidget.getSumValue()
        valueChanged = self.sumValue - sumValue
        self.sumValue = sumValue
        self.evaluationTimes += 1
        self.label_info.setText('提升{}; 评估{};\n修正{}'.format(self.improveTimes,self.evaluationTimes,round(valueChanged,5)))
        
        return valueChanged

    # 无限策略评估
    def autoPolicyEvaluation(self):
        # 如果在自动执行中重新加载地图，可能报越界错误，捕获异常pass掉
        try:
            while self.autoExec:
                self.policyEvaluationOneStep()
        except IndexError:
            pass

    # 执行一次策略提升
    def policyImprove(self):
        gridWidget = self.map.gridWidget
        for row in range(gridWidget.row):
            for colum in range(gridWidget.colum):
                cube = gridWidget.cubes[row][colum] 
                if cube.isPassable:

                    # 计算状态动作价值Q
                    Q = cube.Q
                    for a in cube.action:
                        if cube.nextCubeDict[a] != []:
                            # Q = R(s,a) + gamma*sum{p(s'|s,a)*V(s')}
                            Q[a] = cube.reward
                            for nc,p in cube.nextCubeDict[a]:
                                if nc != None:
                                    disCost = (cube not in self.map.endCubeList)*self.map.disCostDiscount*cube.distance(nc)
                                    Q[a] = Q[a] - p*disCost + p*self.gamma*nc.value  

                    # 在Q上贪心来更新策略pi，相同价值的动作平分概率
                    cube.updatePolicyByQ()
                    self.pi[row][colum] = cube.pi.copy()
        gridWidget.update()

        sumValue = self.map.gridWidget.getSumValue()
        valueChanged = self.sumValue - sumValue
        self.sumValue = sumValue
        self.improveTimes += 1
        self.evaluationTimes = 0
        self.label_info.setText('提升{}; 评估{};\n修正{}'.format(self.improveTimes,self.evaluationTimes,round(valueChanged,5)))
        
        return valueChanged
    

    # 评估当前策略至价值收敛
    def policyEvaluation(self):
        while self.autoExec and abs(self.policyEvaluationOneStep()) > 0.1:
            pass
        return self.map.gridWidget.getSumValue()

    # 自动进行策略迭代
    def autoPolicyIteration(self):
        # 如果在自动执行中重新加载地图，可能报越界错误，捕获异常pass掉
        try:
            lastV = self.policyEvaluation()
            self.policyImprove()
            newV = self.policyEvaluation()

            while self.autoExec and abs(newV-lastV) > 0.1:
                lastV = newV
                self.policyImprove()
                newV = self.policyEvaluation()

            self.autoExec = False
            self.pbt_autoEvaluation.setEnabled(True)
        except IndexError:
            pass

    def resetPolicy(self):
        self.waitAutoExecEnd()
        self.initPolicy()
        self.label_info.setText('')
        self.map.gridWidget.update()

        self.pbt_autoEvaluation.setEnabled(True)
        self.pbt_autoIteration.setEnabled(True)
        self.sumValue = 0
        self.improveTimes = 0
        self.evaluationTimes = 0