from PyQt5 import QtCore, QtWidgets
from core.Algorithm.RL import BasePolicy
import threading

# **此类需重写**
class MCES(BasePolicy):
    def __init__(self,controller):
        super().__init__(controller) 
        self.episode = []       # 当前采样轨迹(S,A,R序列)
        self.showDFS = False    # 显示深度优先搜索轨迹

    # 控制UI（执行此策略时嵌入到controller窗口中）
    def controlLayout(self):
        if self.layout == None:
            Layout = QtWidgets.QGridLayout()
            spacerItem = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            Layout.addItem(spacerItem)
            self.line = QtWidgets.QFrame(self.centralwidget)
            self.line.setFrameShape(QtWidgets.QFrame.HLine)
            self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
            Layout.addWidget(self.line, 0, 0, 1, 2)
            self.label_Title = QtWidgets.QLabel(self.centralwidget)
            self.label_Title.setText('MonteCarlo ES')
            Layout.addWidget(self.label_Title, 1, 0, 1, 2, QtCore.Qt.AlignHCenter)
            self.label_gamma = QtWidgets.QLabel(self.centralwidget)
            self.label_gamma.setText("折扣系数")
            Layout.addWidget(self.label_gamma, 2, 0, 1, 1)
            self.spinBox_gamma = QtWidgets.QDoubleSpinBox(self.centralwidget)
            self.spinBox_gamma.setMaximum(1.0)
            self.spinBox_gamma.setMinimum(0.0)
            self.spinBox_gamma.setValue(0.9)
            self.spinBox_gamma.setSingleStep(0.01)
            Layout.addWidget(self.spinBox_gamma, 2, 1, 1, 1)  
            self.label_alpha = QtWidgets.QLabel(self.centralwidget)
            self.label_alpha.setText("学习率")
            Layout.addWidget(self.label_alpha, 3, 0, 1, 1)
            self.spinBox_alpha = QtWidgets.QDoubleSpinBox(self.centralwidget)
            self.spinBox_alpha.setMaximum(1.0)
            self.spinBox_alpha.setMinimum(0.01)
            self.spinBox_alpha.setValue(0.1)
            self.spinBox_alpha.setSingleStep(0.01)
            Layout.addWidget(self.spinBox_alpha, 3, 1, 1, 1)  

            self.label_epsilon = QtWidgets.QLabel(self.centralwidget)
            self.label_epsilon.setText("试探概率")
            Layout.addWidget(self.label_epsilon, 4, 0, 1, 1)
            self.spinBox_epsilon = QtWidgets.QDoubleSpinBox(self.centralwidget)
            self.spinBox_epsilon.setMaximum(1.0)
            self.spinBox_epsilon.setMinimum(0.0)
            self.spinBox_epsilon.setValue(0.1)
            self.spinBox_epsilon.setSingleStep(0.01)
            Layout.addWidget(self.spinBox_epsilon, 4, 1, 1, 1)  

            self.label_firstVisited = QtWidgets.QLabel(self.centralwidget)
            self.label_firstVisited.setText("首次访问型")
            Layout.addWidget(self.label_firstVisited, 5, 0, 1, 1)
            self.checkBox_firstVisited = QtWidgets.QCheckBox(self.centralwidget)
            self.checkBox_firstVisited.setText("")
            self.checkBox_firstVisited.setChecked(True)
            Layout.addWidget(self.checkBox_firstVisited, 5, 1, 1, 1)
            self.label_everyVisited = QtWidgets.QLabel(self.centralwidget)
            self.label_everyVisited.setText("每次访问型")
            Layout.addWidget(self.label_everyVisited, 6, 0, 1, 1)
            self.checkBox_everyVisited = QtWidgets.QCheckBox(self.centralwidget)
            self.checkBox_everyVisited.setText("")
            self.checkBox_everyVisited.setChecked(False)
            Layout.addWidget(self.checkBox_everyVisited, 6, 1, 1, 1)
            self.pbt_toggleAuto = QtWidgets.QPushButton(self.centralwidget)
            self.pbt_toggleAuto.setText('Start')
            Layout.addWidget(self.pbt_toggleAuto, 7, 0, 1, 1)
            self.spinBox_autoTime = QtWidgets.QDoubleSpinBox(self.centralwidget)
            self.spinBox_autoTime.setObjectName("spinBox_autoTime")
            self.spinBox_autoTime.setMinimum(0)
            self.spinBox_autoTime.setMaximum(10)
            self.spinBox_autoTime.setValue(0.1)
            self.spinBox_autoTime.setSingleStep(0.01)
            Layout.addWidget(self.spinBox_autoTime, 7, 1, 1, 1)
            self.pbt_resetPi = QtWidgets.QPushButton(self.centralwidget)
            self.pbt_resetPi.setText('reset')
            Layout.addWidget(self.pbt_resetPi, 8, 0, 1, 2)
            self.label_info = QtWidgets.QLabel(self.centralwidget)
            self.label_info.setText('已采样轨迹0; 修正0')
            Layout.addWidget(self.label_info, 9, 0, 1, 2)
            self.label_incompleteEpisodeNum = QtWidgets.QLabel(self.centralwidget)
            self.label_incompleteEpisodeNum.setText('不完整轨迹0')
            Layout.addWidget(self.label_incompleteEpisodeNum, 10, 0, 1, 2)
            self.checkBox_debug = QtWidgets.QCheckBox(self.centralwidget)
            self.checkBox_debug.setText("DFS debug")
            self.checkBox_debug.setChecked(False)
            Layout.addWidget(self.checkBox_debug, 11, 0, 1, 2)

            self.controller.pbt_edit.clicked.connect(self.resetPolicy)
            self.controller.policyReloadSignal.connect(self.resetPolicy)
            self.map.reloadSignal.connect(self.resetPolicy)
            self.pbt_resetPi.clicked.connect(self.resetPolicy)
            self.spinBox_autoTime.valueChanged.connect(lambda:self.setAutoTimeStep(float(self.spinBox_autoTime.value())))
            self.spinBox_gamma.valueChanged.connect(lambda:self.setGamma(float(self.spinBox_gamma.value())))
            self.spinBox_alpha.valueChanged.connect(lambda:self.setAlpha(float(self.spinBox_alpha.value())))
            self.spinBox_epsilon.valueChanged.connect(lambda:self.setEpsilon(float(self.spinBox_epsilon.value())))
            self.checkBox_everyVisited.clicked.connect(self.checkBox_firstVisited.toggle)
            self.checkBox_firstVisited.clicked.connect(self.checkBox_everyVisited.toggle)
            self.checkBox_debug.clicked.connect(self.debugDFS)
            self.pbt_toggleAuto.clicked.connect(self.autoToggle)

            self.layout = Layout

        return self.layout

    def controlLayoutInit(self):
        self.initPolicy()  
        self.setLayoutVisiable(True)

    def controlLayoutRemoved(self):
        self.setLayoutVisiable(False)
        self.waitAutoExecEnd()

    def debugDFS(self):
        self.map.showDFS = self.checkBox_debug.isChecked()
        if not self.map.showDFS:
            for r in range(self.map.gridWidget.row):
                for c in range(self.map.gridWidget.colum):
                    self.map.gridWidget.cubes[r][c].showDFS = False

    def autoToggle(self):
        if self.autoExec:
            self.pbt_toggleAuto.setText('Start')
            self.waitAutoExecEnd()
        else:   # 启动子线程自动执行策略
            self.autoExec = True
            self.pbt_toggleAuto.setText('Pause')
            self.autoThread = threading.Thread(target = self.autoMCES)
            self.autoThread.setDaemon(True)
            self.autoThread.start()    

    def resetPolicy(self):
        self.waitAutoExecEnd()
        self.initPolicy()
        self.label_info.setText('已采样轨迹0; 修正0')
        self.label_incompleteEpisodeNum.setText('不完整轨迹0')
        self.map.gridWidget.update()

    # 采样一条轨迹
    def getEpisode(self):
        '''
        self.episode.clear()

        # MCES使用试探性出发假设，随机一个(s,a)作为起点
        height = self.map.gridWidget.row
        width = self.map.gridWidget.colum
        # 随机选择一个起点
        row = randomPick(list(range(height)),height*[1/height])
        colum = randomPick(list(range(width)),width*[1/width])
        agentLoaction = self.map.gridWidget.cubes[row][colum]
        agentLoaction.agentLocated = True
        self.map.gridWidget.update()
        time.sleep(self.controller.timeStep)
        # 随机选一个动作
        nextCubes = self.map.gridWidget.nextCubeDict(row,colum)
        action = randomPick([0,1,2,3],[0.25,0.25,0.25,0.25])
        while nextCubes[action] == None:
            action = randomPick([0,1,2,3],[0.25,0.25,0.25,0.25])

        self.episode.append(agentLoaction)          # S_t
        self.episode.append(action)                 # A_t
        self.episode.append(agentLoaction.reward+self.map.disCostDiscount)   # R_t+1
        agentLoaction.agentLocated = False
        agentLoaction = nextCubes[action]
        agentLoaction.agentLocated = True
        
        self.map.gridWidget.update()
        time.sleep(self.controller.timeStep)
        #self.completeEpisode = self.connectedCheck(agentLoaction)
        self.completeEpisode = self.map.gridWidget.connectedCheck(agentLoaction,self.map.endCube,self.pi)

        while self.autoExec and agentLoaction != self.map.endCube and self.completeEpisode:            
            row = agentLoaction.row
            colum = agentLoaction.colum
            nextCubes = self.map.gridWidget.nextCubeDict(row,colum)

            doExploration = randomPick([True,False],[self.epsilon,1-self.epsilon])
            if doExploration:
                action = randomPick([0,1,2,3],[0.25,0.25,0.25,0.25])
                while nextCubes[action] == None:
                    action = randomPick([0,1,2,3],[0.25,0.25,0.25,0.25])
            else:
                action = randomPick([0,1,2,3],self.pi[row][colum])
            
            self.episode.append(agentLoaction)          # S_t
            self.episode.append(action)                 # A_t
            self.episode.append(agentLoaction.reward+self.map.disCostDiscount)   # R_t+1
            agentLoaction.agentLocated = False
            agentLoaction = nextCubes[action]
            agentLoaction.agentLocated = True
            
            self.completeEpisode = self.map.gridWidget.connectedCheck(agentLoaction,self.map.endCube,self.pi)
            
            self.map.gridWidget.update()
            time.sleep(self.controller.timeStep)
        
        self.episode.append(agentLoaction)                                  # S_T-1 (map.endCube)
        self.episode.append(randomPick([0,1,2,3],[0.25,0.25,0.25,0.25]))    # A_T-1 (随机动作)              
        self.episode.append(agentLoaction.reward)                           # R_T   
        agentLoaction.agentLocated = False                          
        '''
        pass
    
    def updateValue(self):
        if self.episode[-3] == self.map.endCube:
            length = len(self.episode)
            G = 0
            step = 0
            while step < length:
                R = self.episode[length-1-step]
                A = self.episode[length-2-step]
                S = self.episode[length-3-step]
                Q = S.Q

                # 判断是不是首次访问
                isFirstVisit = True
                for i in range(0,step,3):
                    if S == self.episode[i] and A == self.episode[i+1]:
                        isFirstVisit = False                

                # G = gamma*G + R_{t+1}
                G = self.gamma*G + R

                if (self.checkBox_firstVisited.isChecked() and isFirstVisit) or not self.checkBox_firstVisited.isChecked():
                    # Q(s,a) = average{Q(s,a)} （不稳定递推形式）
                    Q[A] = Q[A] + self.alpha*(G-Q[A])
                    
                    '''
                    # pi(s) = argmax_a{Q(s,a)}
                    QSorted = sorted(Q.items(), key=lambda Q:Q[1], reverse=True) # 按值降序得元组列表
                    N = 1
                    for j in range(3):
                        if abs(QSorted[1+j][1] - QSorted[0][1]) < 1e-4:
                            N = N+1
                    self.pi[S.row][S.colum] = [0,0,0,0]
                    for j in range(N):
                        self.pi[S.row][S.colum][QSorted[j][0]] = 1/N
                    '''
                step += 3

            for r in range(self.map.gridWidget.row):
                for c in range(self.map.gridWidget.colum):
                    cube = self.map.gridWidget.cubes[r][c]
                    cube.value = 0
                    for i in range(4):
                        cube.value += self.pi[r][c][i]*cube.Q[i]

            self.map.gridWidget.update()

    def autoMCES(self):
        if self.map.endCube == None:
            reply = QtWidgets.QMessageBox.information(self,"错误","当前地图没有设定终点,无法执行策略",QtWidgets.QMessageBox.Yes)
        else:
            episodeNum = 1
            incompleteNum = 1
            lastV = self.map.gridWidget.getSumValue()
            while self.autoExec:

                # 以epsilon-贪心策略反复采样直到找出完整episode
                self.completeEpisode = True
                self.getEpisode()
                while not self.completeEpisode and self.autoExec:
                    self.label_incompleteEpisodeNum.setText('不完整轨迹{}'.format(incompleteNum))
                    incompleteNum += 1
                    self.completeEpisode = True
                    self.getEpisode()

                # 更新策略
                self.updateValue()
                newV = self.map.gridWidget.getSumValue()
                self.label_info.setText('已采样轨迹{}; 修正{}'.format(episodeNum,round(newV - lastV,5)))
                lastV = newV
                episodeNum += 1
            