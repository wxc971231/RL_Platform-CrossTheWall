# 核心组件 —— 控制器：提供算法测试的图形化工作区，内置多种强化学习算法，允许用户加载算法和地图进行测试。
import os
from functools import partial  
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from core.Core import MapEditor
from core.Core import Monitor
from core.Core import FigureGenerator
from core.Util.dialog import LoadMapDialog
from core.Algorithm.RL import PolicyIteration,ValueIteration,MCES,MCPolicyIteration,Sarsa,DynaQPrior,DynaQ,QLearning
from core.Algorithm.Others import Dijkstra

class Controller(QMainWindow):
    policyReloadSignal = pyqtSignal()
    
    def __init__(self):
        super().__init__() 

        # loadMapDialog在加载地图时弹出
        self.loadMapDialog = LoadMapDialog((os.getcwd()+'/map').replace('\\','/'))
        self.loadMapDialog.loadMapSignal.connect(self.loadMap)

        self.figureGenerator = FigureGenerator(self)    # 图表生成器
        self.mapEditor = MapEditor(self)    # 地图编辑器
        self.map = self.mapEditor.map       # map对象
        self.monitor = Monitor(self)        # 波形监视器
        
        self.penList = []                   # 画笔列表
        self.timeStep = 0.01                # 计算周期

        self.realTimeUI = True              # 实时更新UI
        self.UIStep = 10                    # UI更新周期（以计算周期为单位）

        # 建立Ui 
        self.setupUi()

        # 策略列表
        self.policyControlLayout = None # 选择策略的控制面板（需要嵌入controller UI）
        self.policySelected = None      # 当前选择的策略
        self.policyDict = {'modelBased':{},'modelFree':{},'others':{}}
        policyIteration = PolicyIteration(self)
        valueIteration = ValueIteration(self)
        mcPolicyIteration = MCPolicyIteration(self)
        mces = MCES(self)
        sarsa = Sarsa(self)
        dynaQPrior = DynaQPrior(self)
        dynaQ = DynaQ(self)
        qlearning = QLearning(self)
        dijkstra = Dijkstra(self)
        self.policyDict['modelBased']['policyIteration'] = policyIteration
        self.policyDict['modelBased']['valueIteration'] = valueIteration
        self.policyDict['modelFree']['mcPolicyIteration']   = mcPolicyIteration
        self.policyDict['modelFree']['MCES']  = mces
        self.policyDict['modelFree']['Sarsa']  = sarsa
        self.policyDict['modelFree']['DynaQPrior']  = dynaQPrior
        self.policyDict['modelFree']['DynaQ']  = dynaQ
        self.policyDict['modelFree']['QLearning'] = qlearning
        self.policyDict['others']['dijkstra'] = dijkstra

        self.connectSignalAndSlot()

    def setupUi(self):
        self.setObjectName("EditorWindow")
        self.resize(760, 544)
        self.setWindowIcon(QtGui.QIcon('src/images/grid.png'))
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("controller centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")

        # 左竖线
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout.addWidget(self.line, 1, 1, 1, 1)

        # 右竖线
        self.line_5 = QtWidgets.QFrame(self.centralwidget)
        self.line_5.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_5.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_5.setObjectName("line_5")
        self.gridLayout.addWidget(self.line_5, 1, 3, 1, 1)

        # 上横线
        self.line_2 = QtWidgets.QFrame(self.centralwidget)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.gridLayout.addWidget(self.line_2, 0, 0, 1, 5)

        # 下横线
        self.line_3 = QtWidgets.QFrame(self.centralwidget)
        self.line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.gridLayout.addWidget(self.line_3, 2, 0, 1, 5)

        # 方格地图面板
        self.map.gridWidget.setMinimumSize(QtCore.QSize(600, 500))
        self.map.gridWidget.setObjectName("gridWidget")
        self.gridLayout.addWidget(self.map.gridWidget, 1, 2, 1, 1)

        # 策略面板
        self.policyLayout = QtWidgets.QGridLayout()
        self.policyLayout.setObjectName("policyLayout")
        self.label_policyTitle = QtWidgets.QLabel(self.centralwidget)
        self.label_policyTitle.setObjectName("label_policyTitle")
        self.policyLayout.addWidget(self.label_policyTitle, 0, 0, 1, 2, QtCore.Qt.AlignHCenter)

        self.label_valueColor = QtWidgets.QLabel(self.centralwidget)
        self.label_valueColor.setObjectName("label_valueColor")
        self.label_valueColor.setMargin(1)
        self.policyLayout.addWidget(self.label_valueColor, 1, 0, 1, 1)
        self.checkBox_valueColor = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_valueColor.setText("")
        self.checkBox_valueColor.setObjectName("checkBox_valueColor")
        self.checkBox_valueColor.setEnabled(True)
        self.policyLayout.addWidget(self.checkBox_valueColor, 1, 1, 1, 1)

        self.label_updateUI = QtWidgets.QLabel(self.centralwidget)
        self.label_updateUI.setObjectName("label_updateUI")
        self.label_updateUI.setMargin(1)
        self.policyLayout.addWidget(self.label_updateUI, 2, 0, 1, 1)
        self.checkBox_updateUI = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_updateUI.setText("")
        self.checkBox_updateUI.setChecked(True)
        self.checkBox_updateUI.setObjectName("checkBox_updateUI")
        self.checkBox_updateUI.setEnabled(True)
        self.policyLayout.addWidget(self.checkBox_updateUI, 2, 1, 1, 1)

        self.label_maxReward = QtWidgets.QLabel(self.centralwidget)
        self.label_maxReward.setObjectName("label_maxReward")
        self.policyLayout.addWidget(self.label_maxReward, 3, 0, 1, 1)
        self.spinBox_maxReward = QtWidgets.QDoubleSpinBox(self.centralwidget)
        self.spinBox_maxReward.setObjectName("spinBox_maxReward")
        self.spinBox_maxReward.setMinimum(0)
        self.spinBox_maxReward.setMaximum(1000)
        self.spinBox_maxReward.setValue(5.00)
        self.policyLayout.addWidget(self.spinBox_maxReward, 3, 1, 1, 1)

        self.label_timeStep = QtWidgets.QLabel(self.centralwidget)
        self.label_timeStep.setObjectName("label_timeStep")
        self.label_timeStep.setMargin(1)
        self.policyLayout.addWidget(self.label_timeStep, 4, 0, 1, 1)
        self.spinBox_timeStep = QtWidgets.QDoubleSpinBox(self.centralwidget)
        self.spinBox_timeStep.setMinimum(0.0)
        self.spinBox_timeStep.setMaximum(10)
        self.spinBox_timeStep.setValue(0.1)
        self.spinBox_timeStep.setDecimals(2)
        self.spinBox_timeStep.setSingleStep(0.01)
        self.policyLayout.addWidget(self.spinBox_timeStep, 4, 1, 1, 1)

        self.label_UIStep = QtWidgets.QLabel(self.centralwidget)
        self.label_UIStep.setObjectName("label_UIStep")
        self.label_UIStep.setMargin(1)
        self.policyLayout.addWidget(self.label_UIStep, 5, 0, 1, 1)
        self.spinBox_UIStep = QtWidgets.QSpinBox(self.centralwidget)
        self.spinBox_UIStep.setMinimum(1)
        self.spinBox_UIStep.setMaximum(1000000)
        self.spinBox_UIStep.setValue(10)
        self.policyLayout.addWidget(self.spinBox_UIStep, 5, 1, 1, 1)

        spacerItem4 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.policyLayout.addItem(spacerItem4)

        self.line_6 = QtWidgets.QFrame(self.centralwidget)
        self.line_6.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_6.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_6.setMinimumWidth(150)
        self.policyLayout.addWidget(self.line_6, 6, 0, 1, 2)

        # 这个policyControlLayout将被替换为不同策略的控制布局
        self.policyControlLayout = QtWidgets.QGridLayout()                   
        self.policyControlLayout.setObjectName("policyControlLayout")
        self.policyLayout.addLayout(self.policyControlLayout, 7, 0, 1, 2)

        self.policySpacerItem = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        self.policyLayout.addItem(self.policySpacerItem)

        self.gridLayout.addLayout(self.policyLayout,1, 4, 1, 1)

        # 方格设置面板
        self.settingLayout = QtWidgets.QVBoxLayout()
        self.settingLayout.setObjectName("settingLayout")
        self.cubeSettingLayout = QtWidgets.QGridLayout()
        self.cubeSettingLayout.setObjectName("cubeSettingLayout")
        self.label_cubeTitle = QtWidgets.QLabel(self.centralwidget)
        self.label_cubeTitle.setObjectName("label_cubeTitle")
        #self.label_cubeTitle.setMinimumWidth(90)
        self.cubeSettingLayout.addWidget(self.label_cubeTitle, 0, 0, 1, 2, QtCore.Qt.AlignHCenter)
        self.label_cubeReward = QtWidgets.QLabel(self.centralwidget)
        self.label_cubeReward.setObjectName("label_cubeReward")
        self.label_cubeReward.setMargin(1)
        self.cubeSettingLayout.addWidget(self.label_cubeReward, 1, 0, 1, 2)
        self.label_cubePass = QtWidgets.QLabel(self.centralwidget)
        self.label_cubePass.setObjectName("label_cubePass")
        self.label_cubePass.setMargin(1)
        self.cubeSettingLayout.addWidget(self.label_cubePass, 2, 0, 1, 1)
        self.checkBox_cubePass = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_cubePass.setText("")
        self.checkBox_cubePass.setObjectName("checkBox_cubePass")
        self.checkBox_cubePass.setEnabled(False)
        self.cubeSettingLayout.addWidget(self.checkBox_cubePass, 2, 1, 1, 1)
        self.settingLayout.addLayout(self.cubeSettingLayout)

        # 分隔
        spacerItem = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.settingLayout.addItem(spacerItem)
        
        # 画笔面板
        self.penSettingLayout = QtWidgets.QGridLayout()
        self.penSettingLayout.setObjectName("penSettingLayout")
        self.line_4 = QtWidgets.QFrame(self.centralwidget)
        self.line_4.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_4.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_4.setObjectName("line_4")
        self.penSettingLayout.addWidget(self.line_4, 0, 0, 1, 1)
        self.label_penTitle = QtWidgets.QLabel(self.centralwidget)
        self.label_penTitle.setObjectName("label_penTitle")
        self.penSettingLayout.addWidget(self.label_penTitle, 1, 0, 1, 1, QtCore.Qt.AlignHCenter)
        self.settingLayout.addLayout(self.penSettingLayout)

        # 分隔
        spacerItem2 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.settingLayout.addItem(spacerItem2)

        # 全局设置面板
        self.globalSettingLayout = QtWidgets.QGridLayout()
        self.globalSettingLayout.setObjectName("globalSettingLayout")
        self.line_5 = QtWidgets.QFrame(self.centralwidget)
        self.line_5.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_5.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_5.setObjectName("line_5")
        self.globalSettingLayout.addWidget(self.line_5, 0, 0, 1, 2)
        self.label_globalTitle = QtWidgets.QLabel(self.centralwidget)
        self.label_globalTitle.setObjectName("label_globalTitle")
        self.globalSettingLayout.addWidget(self.label_globalTitle, 1, 0, 1, 2, QtCore.Qt.AlignHCenter)
        self.label_disCostDiscount = QtWidgets.QLabel(self.centralwidget)
        self.label_disCostDiscount.setObjectName("label_disCostDiscount")
        self.label_disCostDiscount.setMargin(1)
        self.globalSettingLayout.addWidget(self.label_disCostDiscount, 2, 0, 1, 2)
        self.label_showGridWithColor = QtWidgets.QLabel(self.centralwidget)
        self.label_showGridWithColor.setObjectName("label_showGridWithColor")
        self.globalSettingLayout.addWidget(self.label_showGridWithColor, 3, 0, 1, 1)
        self.checkBox_showGridWithColor = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_showGridWithColor.setText("")
        self.checkBox_showGridWithColor.setObjectName("checkBox_showGridWithColor")
        self.checkBox_showGridWithColor.setChecked(True)
        self.globalSettingLayout.addWidget(self.checkBox_showGridWithColor, 3, 1, 1, 1)

        self.label_showReward= QtWidgets.QLabel(self.centralwidget)
        self.label_showReward.setObjectName("label_showReward")
        self.globalSettingLayout.addWidget(self.label_showReward, 4, 0, 1, 1)
        self.checkBox_showReward = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_showReward.setText("")
        self.checkBox_showReward.setObjectName("checkBox_showReward")
        self.checkBox_showReward.setChecked(True)
        self.globalSettingLayout.addWidget(self.checkBox_showReward, 4, 1, 1, 1)

        self.label_showValue = QtWidgets.QLabel(self.centralwidget)
        self.label_showValue.setObjectName("label_showValue")
        self.globalSettingLayout.addWidget(self.label_showValue, 5, 0, 1, 1)
        self.checkBox_showValue = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_showValue.setText("")
        self.checkBox_showValue.setChecked(True)
        self.globalSettingLayout.addWidget(self.checkBox_showValue, 5, 1, 1, 1)

        self.label_showQ = QtWidgets.QLabel(self.centralwidget)
        self.label_showQ.setObjectName("label_showQ")
        self.globalSettingLayout.addWidget(self.label_showQ, 6, 0, 1, 1)
        self.checkBox_showQ = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_showQ.setText("")
        self.checkBox_showQ.setChecked(False)
        self.globalSettingLayout.addWidget(self.checkBox_showQ, 6, 1, 1, 1)

        self.label_showPolicy = QtWidgets.QLabel(self.centralwidget)
        self.label_showPolicy.setObjectName("label_showPolicy")
        self.globalSettingLayout.addWidget(self.label_showPolicy, 7, 0, 1, 1)
        self.checkBox_showPolicy = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_showPolicy.setText("")
        self.checkBox_showPolicy.setChecked(False)
        self.globalSettingLayout.addWidget(self.checkBox_showPolicy, 7, 1, 1, 1)

        self.label_showCubePolicy = QtWidgets.QLabel(self.centralwidget)
        self.label_showCubePolicy.setObjectName("label_showCubePolicy")
        self.globalSettingLayout.addWidget(self.label_showCubePolicy, 8, 0, 1, 1)
        self.checkBox_showCubePolicy = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_showCubePolicy.setText("")
        self.checkBox_showCubePolicy.setChecked(False)
        self.globalSettingLayout.addWidget(self.checkBox_showCubePolicy, 8, 1, 1, 1)

        self.label_showCubePolicyOneStep = QtWidgets.QLabel(self.centralwidget)
        self.label_showCubePolicyOneStep.setObjectName("label_showCubePolicyOneStep")
        self.globalSettingLayout.addWidget(self.label_showCubePolicyOneStep, 9, 0, 1, 1)
        self.checkBox_showCubePolicyOneStep = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_showCubePolicyOneStep.setText("")
        self.checkBox_showCubePolicyOneStep.setChecked(False)
        self.globalSettingLayout.addWidget(self.checkBox_showCubePolicyOneStep, 9, 1, 1, 1)
        
        self.pbt_policyColor = QtWidgets.QPushButton(self.centralwidget)
        self.pbt_policyColor.setObjectName("pbt_policyColor")
        self.pbt_policyColor.setStyleSheet('QPushButton{background:#AA0000;}')
        self.globalSettingLayout.addWidget(self.pbt_policyColor, 10, 0, 1, 2)

        self.pbt_edit = QtWidgets.QPushButton(self.centralwidget)
        self.pbt_edit.setObjectName("pbt_edit")
        self.globalSettingLayout.addWidget(self.pbt_edit, 11, 0, 1, 2)
        self.settingLayout.addLayout(self.globalSettingLayout)

        # 下分割和其他设置
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.settingLayout.addItem(spacerItem1)
        self.settingLayout.setStretch(3, 1)
        self.gridLayout.addLayout(self.settingLayout, 1, 0, 1, 1)
        
        self.gridLayout.setColumnStretch(2, 1)
        self.setCentralWidget(self.centralwidget)

        # 状态栏
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)
        self.statusBar().showMessage('')

        # 菜单栏
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 760, 23))
        self.menubar.setObjectName("menubar")

        # 菜单map栏
        self.action_load_map = QtWidgets.QAction(self)
        self.action_load_map.setObjectName("action_load_map")
        self.action_edit_map = QtWidgets.QAction(self)
        self.action_edit_map.setObjectName("action_edit_map")
        self.menuMap = QtWidgets.QMenu(self.menubar)
        self.menuMap.setObjectName("menuMap")
        self.menuMap.addAction(self.action_load_map)
        self.menuMap.addAction(self.action_edit_map)        
        self.menubar.addAction(self.menuMap.menuAction())
        
        # 菜单policy栏
        self.action_policy_iteration = QtWidgets.QAction(self)
        self.action_policy_iteration.setObjectName("action_policy_iteration")
        self.action_value_iteration = QtWidgets.QAction(self)
        self.action_value_iteration.setObjectName("action_value_iteration")
        self.action_MCES = QtWidgets.QAction(self)
        self.action_MCES.setObjectName("action_MCES")
        self.action_MCES.setEnabled(False)
        self.action_mc_policy_iteration = QtWidgets.QAction(self)
        self.action_mc_policy_iteration.setObjectName("action_mc_policy_iteration")
        self.action_mc_policy_iteration.setEnabled(False)
        self.action_dijkstra = QtWidgets.QAction(self)
        self.action_dijkstra.setObjectName("action_dijkstra")
        self.action_sarsa = QtWidgets.QAction(self)
        self.action_sarsa.setObjectName("action_sarsa")
        self.action_dyna_q_prior = QtWidgets.QAction(self)
        self.action_dyna_q_prior.setObjectName("action_dyna_q_prior")
        self.action_dyna_q = QtWidgets.QAction(self)
        self.action_dyna_q.setObjectName("action_dyna_q")
        self.action_q_learning = QtWidgets.QAction(self)
        self.action_q_learning.setObjectName("action_q_learning")
        
        self.menuPolicy = QtWidgets.QMenu(self.menubar)
        self.menuPolicy.setObjectName("menuPolicy")
        self.menuModelBased = QtWidgets.QMenu(self.menubar)
        self.menuModelBased.setObjectName('menuModelBased')
        self.menuModelFree = QtWidgets.QMenu(self.menubar)
        self.menuModelFree.setObjectName('menuModelFree')
        self.menuOthers = QtWidgets.QMenu(self.menubar)
        self.menuOthers.setObjectName('menuOthers')
        self.menuQLearning = QtWidgets.QMenu(self.menubar)
        self.menuQLearning.setObjectName('menuQLearning')

        self.menuPolicy.addMenu(self.menuModelBased)
        self.menuPolicy.addMenu(self.menuModelFree)
        self.menuPolicy.addMenu(self.menuOthers)
        self.menuModelFree.addMenu(self.menuQLearning)

        self.menuModelBased.addAction(self.action_policy_iteration)
        self.menuModelBased.addAction(self.action_value_iteration)
        self.menuModelFree.addAction(self.action_sarsa)
        self.menuModelFree.addAction(self.action_mc_policy_iteration)
        self.menuModelFree.addAction(self.action_MCES)
        self.menuQLearning.addAction(self.action_q_learning)
        self.menuQLearning.addAction(self.action_dyna_q)
        self.menuQLearning.addAction(self.action_dyna_q_prior)
        self.menuOthers.addAction(self.action_dijkstra)
        
        self.menubar.addAction(self.menuPolicy.menuAction())

        # 菜单figure栏
        self.action_line_chart = QtWidgets.QAction(self)
        self.action_line_chart.setObjectName("action_line_chart")

        self.menuFigure = QtWidgets.QMenu(self.menubar)
        self.menuFigure.setObjectName("menuFigure")

        self.menuFigure.addAction(self.action_line_chart)
        self.menubar.addAction(self.menuFigure.menuAction())

        self.setMenuBar(self.menubar)


        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("EditorWindow", "Grid World"))

        self.menuMap.setTitle(_translate("EditorWindow", "Map"))
        self.menuPolicy.setTitle(_translate("EditorWindow", "Policy"))
        self.menuQLearning.setTitle(_translate("EditorWindow", "Q-Learning"))
        self.action_load_map.setText(_translate("EditorWindow", "加载地图"))
        self.action_edit_map.setText(_translate("EditorWindow", "地图编辑器"))
        self.action_policy_iteration.setText(_translate("EditorWindow", "Policy Iteration"))
        self.action_value_iteration.setText(_translate("EditorWindow", "Value Iteration"))
        self.action_mc_policy_iteration.setText(_translate("EditorWindow", "MC Policy Iteration"))
        self.action_MCES.setText(_translate("EditorWindow", "MonteCarlo ES"))
        self.action_dijkstra.setText(_translate("EditorWindow", "dijkstra"))
        self.action_sarsa.setText(_translate("EditorWindow", "Sarsa"))
        self.action_dyna_q_prior.setText(_translate("EditorWindow", "Dyna-Q(prior)"))
        self.action_dyna_q.setText(_translate("EditorWindow", "Dyna-Q"))
        self.action_q_learning.setText(_translate("EditorWindow", "Q-Learning"))

        self.menuModelBased.setTitle(_translate("EditorWindow", "Model Based"))
        self.menuModelFree.setTitle(_translate("EditorWindow", "Model Free"))
        self.menuOthers.setTitle(_translate("EditorWindow", "Others"))

        self.label_cubeTitle.setText(_translate("EditorWindow", "方格设定"))
        self.label_cubeReward.setText(_translate("EditorWindow", "奖励设置："))
        self.label_cubePass.setText(_translate("EditorWindow", "允许通行"))

        self.label_penTitle.setText(_translate("EditorWindow", "画笔设定"))
        
        self.label_globalTitle.setText(_translate("EditorWindow", "全局设定"))
        self.label_disCostDiscount.setText(_translate("EditorWindow", "路程折扣："))
        self.label_showGridWithColor.setText(_translate("EditorWindow", "分色显示"))
        self.label_showReward.setText(_translate("EditorWindow", "显示奖励"))
        self.label_showValue.setText(_translate("EditorWindow", "显示价值"))
        self.label_showQ.setText(_translate("EditorWindow", "显示Q"))
        self.pbt_policyColor.setText(_translate("EditorWindow", "策略颜色"))
        self.label_showPolicy.setText(_translate("EditorWindow", "显示策略"))
        self.label_showCubePolicy.setText(_translate("EditorWindow", "按块显示"))
        self.label_showCubePolicyOneStep.setText(_translate("EditorWindow", "    单步"))
        self.pbt_edit.setText(_translate("EditorWindow", "编辑地图"))

        self.label_policyTitle.setText(_translate("EditorWindow", "策略控制"))
        self.label_valueColor.setText(_translate("EditorWindow", "价值分色"))
        self.label_updateUI.setText(_translate("EditorWindow", "实时UI"))
        self.label_maxReward.setText(_translate("EditorWindow", "最大价值"))
        self.label_timeStep.setText(_translate("EditorWindow", "计算周期"))
        self.label_UIStep.setText(_translate("EditorWindow", "UI周期"))
        
        self.action_line_chart.setText(_translate("EditorWindow", "折线图"))
        self.menuFigure.setTitle(_translate("EditorWindow", "Figure"))

    def connectSignalAndSlot(self):
        # 信号与槽函数连接
        self.action_load_map.triggered.connect(self.loadMapDialog.show)        # 加载地图
        self.checkBox_showGridWithColor.clicked.connect(self.updateGridWithColor) # 分色显示
        self.checkBox_showReward.clicked.connect(self.showReward)               # 显示奖励
        self.checkBox_showValue.clicked.connect(self.showValue)                 # 显示价值
        self.checkBox_showPolicy.clicked.connect(self.showPolicy)               # 显示策略
        self.checkBox_showCubePolicy.clicked.connect(self.showCubePolicy)       # 策略按块显示
        self.checkBox_showCubePolicyOneStep.clicked.connect(self.showCubePolicyOneStep)
        self.checkBox_showQ.clicked.connect(self.showQ)                         # 显示动作状态价值
        self.pbt_policyColor.clicked.connect(self.setPolicyColor)
        self.checkBox_valueColor.clicked.connect(self.updateGridColorByValue)
        self.checkBox_updateUI.clicked.connect(self.updateUIRealTime)
        self.action_edit_map.triggered.connect(self.showMapEditor)
        self.pbt_edit.clicked.connect(self.showMapEditor)
        self.map.gridWidget.cubeSelectedSignal.connect(self.showCubeSetting)
        self.spinBox_maxReward.valueChanged.connect(lambda:self.setMaxValue(float(self.spinBox_maxReward.value())))
        self.spinBox_timeStep.valueChanged.connect(lambda:self.setTimeStep(float(self.spinBox_timeStep.value())))
        self.spinBox_UIStep.valueChanged.connect(lambda:self.setUIStep(int(self.spinBox_UIStep.value())))
        
        self.action_policy_iteration.triggered.connect(lambda: self.loadPolicy(self.policyDict['modelBased']['policyIteration']))
        self.action_value_iteration.triggered.connect(lambda: self.loadPolicy(self.policyDict['modelBased']['valueIteration']))
        self.action_mc_policy_iteration.triggered.connect(lambda: self.loadPolicy(self.policyDict['modelFree']['mcPolicyIteration']))
        self.action_MCES.triggered.connect(lambda: self.loadPolicy(self.policyDict['modelFree']['MCES']))
        self.action_dijkstra.triggered.connect(lambda: self.loadPolicy(self.policyDict['others']['dijkstra']))
        self.action_sarsa.triggered.connect(lambda: self.loadPolicy(self.policyDict['modelFree']['Sarsa']))
        self.action_dyna_q_prior.triggered.connect(lambda: self.loadPolicy(self.policyDict['modelFree']['DynaQPrior']))
        self.action_dyna_q.triggered.connect(lambda: self.loadPolicy(self.policyDict['modelFree']['DynaQ']))
        self.action_q_learning.triggered.connect(lambda: self.loadPolicy(self.policyDict['modelFree']['QLearning']))

        self.action_line_chart.triggered.connect(self.figureGenerator.show)

    def setTimeStep(self,timeStep):
        self.timeStep = timeStep

    def setUIStep(self,UIStep):
        self.UIStep = UIStep

    def setMaxValue(self,maxValue):
        if maxValue == 0:
            maxValue = 0.01
        self.map.gridWidget.maxValue = maxValue
        if self.map.showColorByValue:
            self.map.gridWidget.update()

    def showReward(self):
        self.map.showReward = self.checkBox_showReward.isChecked()
        self.map.gridWidget.update()

    def showValue(self):
        self.map.showValue = self.checkBox_showValue.isChecked()
        self.map.gridWidget.update()

    def showPolicy(self):
        self.map.showPolicy = self.checkBox_showPolicy.isChecked()
        self.map.gridWidget.update()

    def showCubePolicy(self):
        self.map.showPolicyOfSelectedCube = self.checkBox_showCubePolicy.isChecked()
        self.map.gridWidget.update()

    def showCubePolicyOneStep(self):
        self.map.showEpisodeOfSelectedCube = not self.checkBox_showCubePolicyOneStep.isChecked()
        self.map.gridWidget.update()

    def showQ(self):
        self.map.showQ = self.checkBox_showQ.isChecked()
        self.map.gridWidget.update()        

    def updateGridWithColor(self):
        self.map.gridWidget.showWithColor = self.checkBox_showGridWithColor.isChecked()
        self.map.gridWidget.update()

    def updateGridColorByValue(self):
        self.map.showColorByValue = self.checkBox_valueColor.isChecked()
        self.map.gridWidget.update()

    def updateUIRealTime(self):
        self.realTimeUI = self.checkBox_updateUI.isChecked()
        self.spinBox_UIStep.setEnabled(self.realTimeUI)

    def refreshPenList(self):
        for i in range(len(self.penList)):
            self.penSettingLayout.itemAt(2+i).widget().deleteLater()
        self.penList.clear()

        i = 0
        for penName in self.mapEditor.map.penDict:
            pbt_pen = QtWidgets.QPushButton(self.centralwidget)
            pbt_pen.setText(penName)
            pbt_pen.setStyleSheet('QPushButton{background:%s;}'%self.mapEditor.map.penDict[penName].color)
            pbt_pen.clicked.connect(partial(self.showPenSetting,self.mapEditor.map.penDict[penName]))
            self.penSettingLayout.addWidget(pbt_pen, 2+i, 0, 1, 1)
            self.penList.append(pbt_pen)
            i = i+1

    def setPolicyColor(self):
        col = QColorDialog.getColor() 
        if col.isValid(): 
            self.pbt_policyColor.setStyleSheet('QPushButton{background:%s;}'%col.name())
            self.map.policyColor = col.name()
            self.map.gridWidget.update()

    def showCubeSetting(self):
        cube = self.map.gridWidget.cubeSelected
        if cube != None:
            self.label_cubeTitle.setText('方格信息')
            self.label_cubeReward.setText('奖励设置：'+str(cube.reward))
            self.checkBox_cubePass.setChecked(cube.isPassable)
            self.statusBar().showMessage("方格({},{})：type = {}; passable = {}; value = {}".format(cube.row,cube.colum,cube.penName,str(cube.isPassable),cube.value))
        else:
            self.statusBar().showMessage("")

    def showPenSetting(self,pen):
        self.label_cubeTitle.setText('画笔详情')
        self.label_cubeReward.setText('奖励设置：'+str(pen.reward))
        self.checkBox_cubePass.setChecked(pen.isPassable)
    
        if pen.name == 'modified':
            self.statusBar().showMessage("modified是手动编辑修改后可通行方格的统一类型，不可用于绘制")
        elif pen.name == 'wall':
            self.statusBar().showMessage("wall画笔用于绘制不可通行方格，仅增加不可通行属性，其它属性不变")
        elif pen.name == 'default':
            self.statusBar().showMessage("default画笔用于绘制无奖励无滑动的默认方格")
        else:
            info = pen.slide.copy()
            info.append(float(pen.reward))
            self.statusBar().showMessage("自定义画笔"+pen.name+"："+'info = '+str(info))

    def loadMap(self,filePath):
        # 结束可能正在执行的自动control任务
        if self.policySelected != None:
            self.policySelected.waitAutoExecEnd()
        # 加载新地图
        status = self.mapEditor.file.loadMap(filePath,self.mapEditor.map)
        if status != '加载成功':
            self.loadMapDialog.textBrowser.setText(status)
        else:
            self.map.name = self.mapEditor.file.fileName
            self.map.path = self.mapEditor.file.filePath
            self.map.isVisible = True
            self.loadMapDialog.close()
            self.map.gridWidget.update()
            self.updateGridWithColor()
            self.refreshPenList()
            self.setWindowTitle('Corss The Wall - ' + self.map.name)
            self.label_disCostDiscount.setText('路程折扣：'+str(round(self.map.disCostDiscount,2)))
            self.map.reloadSignal.emit()

    def showMapEditor(self):
        self.mapEditor.show()
        self.close()

    def showEvent(self,event):
        self.map.showReward = True
        self.map.showColorByValue = False
        self.map.showPolicy = False
        self.map.showValue = True
        self.checkBox_showPolicy.setChecked(False)
        self.checkBox_showValue.setChecked(True)
        self.checkBox_showReward.setChecked(True)
        self.checkBox_valueColor.setChecked(False)
        self.label_disCostDiscount.setText('路程折扣：'+str(round(self.map.disCostDiscount,2)))
        self.setWindowTitle('Corss The Wall - ' + self.map.name)
        self.gridLayout.addWidget(self.map.gridWidget, 1, 2, 1, 1)
        self.refreshPenList()
        
    def loadPolicy(self,policy):
        if self.map.isVisible:
            self.policyReloadSignal.emit()

            # 移除原先的policy控制面板
            try:                                                        
                self.policyLayout.removeItem(self.policySelected.controlLayout())   # policyLayout解除管理
                self.policySelected.controlLayoutRemoved()                          # 旧策略控制面板移除处理
            except Exception:
                pass

            # 嵌入新policy面板
            self.policyControlLayout = policy.controlLayout()               
            self.policyLayout.addLayout(self.policyControlLayout, 7, 0, 1, 2)
            policy.controlLayoutInit()                                              # 新策略面板初始化处理
            self.policySelected = policy
        else:
            reply = QMessageBox.information(self,"未选择地图！","打开地图前，禁止使用策略面板！",QMessageBox.Yes)
