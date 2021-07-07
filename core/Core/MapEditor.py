# 核心组件 —— 地图编辑器：实现地图的图形化编辑、新建、保存等功能
import operator
import os
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from core.Util.dialog import SizeDialog,PenDialog,SaveFileDialog,LoadMapDialog
from core.Util.file import MapFile
from core.Util.map import Pen,Map
from core.MapGenerator import CWGenerator
 
class MapEditor(QMainWindow):
    def __init__(self,controller):
        super().__init__() 
        self.controller = controller
        self.map = Map(self)                    # map对象
        self.file = MapFile()                   # File对象用于map文件存取
        self.sizeDialog = SizeDialog()          # sizeDialog在创建新地图时弹出，信号传入newMap
        self.saveFileDialog = SaveFileDialog('map')                                         # saveFileDialog在保存地图时弹出
        self.loadMapDialog = LoadMapDialog((os.getcwd()+'/map').replace('\\','/'))          # loadMapDialog在加载地图时弹出
        self.penDialog = PenDialog(self)

        # 建立Ui 
        self.setupUi()

        # 生成器字典
        self.generatorDict = {}
        cwGenerator = CWGenerator(self)
        self.generatorDict['Crossing Wall'] = cwGenerator
        
    def setupUi(self):
        self.setObjectName("EditorWindow")
        self.resize(760, 544)
        self.setWindowIcon(QtGui.QIcon('src/images/grid.png'))
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("map editor centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout.addWidget(self.line, 1, 1, 1, 1)
        self.line_2 = QtWidgets.QFrame(self.centralwidget)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.gridLayout.addWidget(self.line_2, 0, 0, 1, 5)
        self.settingLayout = QtWidgets.QVBoxLayout()
        self.settingLayout.setObjectName("settingLayout")
        self.line_3 = QtWidgets.QFrame(self.centralwidget)
        self.line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.gridLayout.addWidget(self.line_3, 2, 0, 1, 5)
        self.line_4 = QtWidgets.QFrame(self.centralwidget)
        self.line_4.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_4.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_4.setObjectName("line_4")
        self.gridLayout.addWidget(self.line_4, 1, 3, 1, 1)

        # 地图生成器面板
        self.generatorLayout = QtWidgets.QGridLayout()
        self.generatorLayout.setObjectName("generatorLayout")
        self.label_genTitle = QtWidgets.QLabel(self.centralwidget)
        self.label_genTitle.setAlignment(QtCore.Qt.AlignCenter)
        self.label_genTitle.setObjectName("label_genTitle")
        self.generatorLayout.addWidget(self.label_genTitle, 0, 0, 1, 1)
        self.line_5 = QtWidgets.QFrame(self.centralwidget)
        self.line_5.setMinimumSize(QtCore.QSize(100, 0))
        self.line_5.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_5.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_5.setObjectName("line_5")
        self.generatorLayout.addWidget(self.line_5, 1, 0, 1, 1)
        # 这个generatorControlLayout将被替换为不同生成器类中的控制布局
        self.generatorControlLayout = QtWidgets.QGridLayout()                   
        self.generatorControlLayout.setObjectName("generatorControlLayout")
        self.generatorLayout.addLayout(self.generatorControlLayout, 2, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.generatorLayout.addItem(spacerItem, 3, 0, 1, 1)
        self.gridLayout.addLayout(self.generatorLayout, 1, 4, 1, 1)

        # 方格地图面板
        self.map.gridWidget.setMinimumSize(QtCore.QSize(600, 500))
        self.map.gridWidget.setObjectName("gridWidget")
        self.gridLayout.addWidget(self.map.gridWidget, 1, 2, 1, 1)
        
        # 方格设置面板
        self.cubeSettingLayout = QtWidgets.QGridLayout()
        self.cubeSettingLayout.setObjectName("cubeSettingLayout")
        self.label_cubeTitle = QtWidgets.QLabel(self.centralwidget)
        self.label_cubeTitle.setObjectName("label_cubeTitle")
        self.cubeSettingLayout.addWidget(self.label_cubeTitle, 0, 0, 1, 2, QtCore.Qt.AlignHCenter)
        self.label_cubeReward = QtWidgets.QLabel(self.centralwidget)
        self.label_cubeReward.setObjectName("label_cubeReward")
        self.cubeSettingLayout.addWidget(self.label_cubeReward, 1, 0, 1, 1)
        self.spinBox_cubeReward = QtWidgets.QDoubleSpinBox(self.centralwidget)
        self.spinBox_cubeReward.setObjectName("spinBox_cubeReward")
        self.spinBox_cubeReward.setMaximum(1000)
        self.spinBox_cubeReward.setMinimum(-1000)
        self.cubeSettingLayout.addWidget(self.spinBox_cubeReward, 1, 1, 1, 1)
        self.checkBox_cubePass = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_cubePass.setText("")
        self.checkBox_cubePass.setObjectName("checkBox_cubePass")
        self.cubeSettingLayout.addWidget(self.checkBox_cubePass, 2, 1, 1, 1)
        self.label_cubePass = QtWidgets.QLabel(self.centralwidget)
        self.label_cubePass.setObjectName("label_cubePass")
        self.cubeSettingLayout.addWidget(self.label_cubePass, 2, 0, 1, 1)
        self.label_cubeStart = QtWidgets.QLabel(self.centralwidget)
        self.label_cubeStart.setObjectName("label_cubeStart")
        self.cubeSettingLayout.addWidget(self.label_cubeStart, 3, 0, 1, 1)
        self.checkBox_cubeStart = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_cubeStart.setText("")
        self.checkBox_cubeStart.setObjectName("checkBox_cubeStart")
        self.cubeSettingLayout.addWidget(self.checkBox_cubeStart, 3, 1, 1, 1)
        self.label_cubeEnd = QtWidgets.QLabel(self.centralwidget)
        self.label_cubeEnd.setObjectName("label_cubeEnd")
        self.cubeSettingLayout.addWidget(self.label_cubeEnd, 4, 0, 1, 1)
        self.checkBox_cubeEnd = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_cubeEnd.setText("")
        self.checkBox_cubeEnd.setObjectName("checkBox_cubeEnd")
        self.cubeSettingLayout.addWidget(self.checkBox_cubeEnd, 4, 1, 1, 1)
        self.pbt_editCube = QtWidgets.QPushButton(self.centralwidget)
        self.pbt_editCube.setObjectName("pbt_editCube")
        self.cubeSettingLayout.addWidget(self.pbt_editCube, 5, 0, 1, 2)
        self.settingLayout.addLayout(self.cubeSettingLayout)
        self.pbt_saveAsPen = QtWidgets.QPushButton(self.centralwidget)
        self.pbt_saveAsPen.setObjectName("pbt_saveAsPen")
        self.cubeSettingLayout.addWidget(self.pbt_saveAsPen, 6, 0, 1, 2)

        spacerItem = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.settingLayout.addItem(spacerItem)

        # 画笔设置面板
        self.penSettingLayout = QtWidgets.QGridLayout()
        self.penSettingLayout.setObjectName("penSettingLayout")
        self.line_4 = QtWidgets.QFrame(self.centralwidget)
        self.line_4.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_4.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_4.setObjectName("line_4")
        self.penSettingLayout.addWidget(self.line_4, 0, 0, 1, 2)
        self.label_penTitle = QtWidgets.QLabel(self.centralwidget)
        self.label_penTitle.setObjectName("label_penTitle")
        self.penSettingLayout.addWidget(self.label_penTitle, 1, 0, 1, 2, QtCore.Qt.AlignHCenter)
        self.comboBox_penName = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox_penName.setObjectName("comboBox_penName")
        self.penSettingLayout.addWidget(self.comboBox_penName, 2, 1, 1, 1)
        self.label_penName = QtWidgets.QLabel(self.centralwidget)
        self.label_penName.setObjectName("label_penName")
        self.penSettingLayout.addWidget(self.label_penName, 2, 0, 1, 1)
        self.label_penColor = QtWidgets.QLabel(self.centralwidget)
        self.label_penColor.setObjectName("label_penColor")
        self.penSettingLayout.addWidget(self.label_penColor, 3, 0, 1, 1)
        self.pbt_color = QtWidgets.QPushButton(self.centralwidget)
        self.pbt_color.setObjectName("pbt_color")
        self.pbt_color.setStyleSheet('QPushButton{background:#C8C8C8;}')
        self.penSettingLayout.addWidget(self.pbt_color, 3, 1, 1, 1)
        self.settingLayout.addLayout(self.penSettingLayout)
        self.checkBox_penDrawing = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_penDrawing.setText("")
        self.checkBox_penDrawing.setObjectName("checkBox_penDrawing")
        self.penSettingLayout.addWidget(self.checkBox_penDrawing, 4, 1, 1, 1)
        self.label_penDrawing = QtWidgets.QLabel(self.centralwidget)
        self.label_penDrawing.setObjectName("label_penDrawing")
        self.penSettingLayout.addWidget(self.label_penDrawing, 4, 0, 1, 1)
        self.pbt_deletePen = QtWidgets.QPushButton(self.centralwidget)
        self.pbt_deletePen.setObjectName("pbt_deletePen")
        self.penSettingLayout.addWidget(self.pbt_deletePen, 5, 0, 1, 2)

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
        self.globalSettingLayout.addWidget(self.label_disCostDiscount, 2, 0, 1, 1)
        self.spinBox_disCostDiscount = QtWidgets.QDoubleSpinBox(self.centralwidget)
        self.spinBox_disCostDiscount.setObjectName("spinBox_disCostDiscount")
        self.spinBox_disCostDiscount.setMaximum(10)
        self.spinBox_disCostDiscount.setValue(1.00)
        self.spinBox_disCostDiscount.setMinimum(-10)
        self.spinBox_disCostDiscount.setSingleStep(0.01)
        self.globalSettingLayout.addWidget(self.spinBox_disCostDiscount, 2, 1, 1, 1)  
        self.label_showGridWithColor = QtWidgets.QLabel(self.centralwidget)
        self.label_showGridWithColor.setObjectName("label_showGridWithColor")
        self.globalSettingLayout.addWidget(self.label_showGridWithColor, 3, 0, 1, 1)
        self.checkBox_showGridWithColor = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_showGridWithColor.setText("")
        self.checkBox_showGridWithColor.setObjectName("checkBox_showGridWithColor")
        self.checkBox_showGridWithColor.setChecked(True)
        self.globalSettingLayout.addWidget(self.checkBox_showGridWithColor, 3, 1, 1, 1)
        self.pbt_finish = QtWidgets.QPushButton(self.centralwidget)
        self.pbt_finish.setObjectName("pbt_finish")
        self.globalSettingLayout.addWidget(self.pbt_finish, 4, 0, 1, 2)
        self.settingLayout.addLayout(self.globalSettingLayout)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.settingLayout.addItem(spacerItem1)
        self.settingLayout.setStretch(3, 1)
        self.gridLayout.addLayout(self.settingLayout, 1, 0, 1, 1)
        self.gridLayout.setColumnStretch(2, 1)
        self.setCentralWidget(self.centralwidget)

        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 760, 23))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuGenerator = QtWidgets.QMenu(self.menubar)
        self.menuGenerator.setObjectName("menuGenerator")
        self.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.statusBar().showMessage('')
        self.setStatusBar(self.statusbar)
        self.action_add_map = QtWidgets.QAction(self)
        self.action_add_map.setObjectName("action_add_map")
        self.action_load_map = QtWidgets.QAction(self)
        self.action_load_map.setObjectName("action_load_map")
        self.action_save_map = QtWidgets.QAction(self)
        self.action_save_map.setObjectName("action_save_map")
        self.action_save_as = QtWidgets.QAction(self)
        self.action_save_as.setObjectName("action_save_as")
        self.action_generator_CW = QtWidgets.QAction(self)
        self.action_generator_CW.setObjectName("action_generator_CW")
        self.menuFile.addAction(self.action_add_map)
        self.menuFile.addAction(self.action_load_map)
        self.menuFile.addAction(self.action_save_map)
        self.menuFile.addAction(self.action_save_as)
        self.menuGenerator.addAction(self.action_generator_CW)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuGenerator.menuAction())

        # 刷新画笔列表
        self.refreshPenComboBox()
        self.penSelected = self.map.penDict['default']

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

        # 初始化面板显示
        self.setCubeSettingLayoutEnabled(False)
        self.checkBox_penDrawing.setChecked(False)

        # 信号与槽函数连接
        self.action_add_map.triggered.connect(self.sizeDialog.show)             # 新地图，打开尺寸编辑Dialog
        self.action_load_map.triggered.connect(self.loadMapDialog.show)        # 加载地图
        self.pbt_saveAsPen.clicked.connect(self.penDialog.show)                 # 方格属性存为画笔
        self.action_save_map.triggered.connect(self.updateMap)                  # 更新地图
        self.action_save_as.triggered.connect(self.showSaveFileDialog)          # 地图另存为
        self.action_generator_CW.triggered.connect(lambda: self.loadGenerator(self.generatorDict['Crossing Wall']))

        self.checkBox_cubeStart.clicked.connect(self.check_cubeStart)           # 方块设为起点
        self.checkBox_cubeEnd.clicked.connect(self.check_cubeEnd)               # 方块设为终点
        self.checkBox_showGridWithColor.clicked.connect(self.updateGridWithColor) # 分色显示
        self.checkBox_penDrawing.toggled.connect(self.setEditorMode)            # 开始绘制
        self.comboBox_penName.currentIndexChanged.connect(self.selectPen)       # 选择画笔
        self.pbt_editCube.clicked.connect(self.updateCube)                      # 更新方格属性
        self.pbt_color.clicked.connect(self.setPenColor)                        # 选择画笔颜色
        self.pbt_deletePen.clicked.connect(self.deletPen)                       # 删除画笔
        self.map.gridWidget.cubeUpdateSignal.connect(lambda: self.setMapSaved(False))   # 用画笔绘制方格时的更新信号
        self.spinBox_disCostDiscount.valueChanged.connect(self.setDisCostDiscount)
        self.pbt_finish.clicked.connect(self.editFinish)
        self.sizeDialog.sizeSignal.connect(self.newMap)
        self.saveFileDialog.saveMapSignal.connect(self.saveMap)
        self.loadMapDialog.loadMapSignal.connect(self.loadMap)
        self.penDialog.penSignal.connect(self.newPen)
        self.map.gridWidget.cubeSelectedSignal.connect(self.showCubeSetting)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("EditorWindow", "MapEditor - new*"))
        self.label_showGridWithColor.setText(_translate("EditorWindow", "分色显示"))
        self.pbt_finish.setText(_translate("EditorWindow", "绘制完成"))
        self.pbt_saveAsPen.setText(_translate("EditorWindow", "存为画笔"))
        self.label_cubeReward.setText(_translate("EditorWindow", "奖励设置"))
        self.pbt_editCube.setText(_translate("EditorWindow", "修改方格"))
        self.label_cubeTitle.setText(_translate("EditorWindow", "方格设定"))
        self.label_cubePass.setText(_translate("EditorWindow", "允许通行"))
        self.label_cubeStart.setText(_translate("EditorWindow", "设为起点"))
        self.label_cubeEnd.setText(_translate("EditorWindow", "设为终点"))
        self.label_penTitle.setText(_translate("EditorWindow", "画笔设定"))
        self.label_penDrawing.setText(_translate("EditorWindow", "开始绘制"))
        self.label_penName.setText(_translate("EditorWindow", "选择画笔"))
        self.pbt_deletePen.setText(_translate("EditorWindow", "删除画笔"))
        self.menuFile.setTitle(_translate("EditorWindow", "File"))
        self.action_add_map.setText(_translate("EditorWindow", "新建地图"))
        self.action_load_map.setText(_translate("EditorWindow", "加载地图"))
        self.action_save_map.setText(_translate("EditorWindow", "保存地图"))
        self.action_save_as.setText(_translate("EditorWindow", "另存为"))
        self.label_globalTitle.setText(_translate("EditorWindow", "全局设定"))
        self.label_disCostDiscount.setText(_translate("EditorWindow", "路程折扣"))
        self.label_penColor.setText(_translate("EditorWindow", "画笔颜色"))
        self.label_genTitle.setText(_translate("self", "地图生成器"))
        self.menuGenerator.setTitle(_translate("self", "Generator"))
        self.action_generator_CW.setText(_translate("self", "Crossing Wall"))

    # 设置方格编辑面板使能/失能
    def setCubeSettingLayoutEnabled(self,enabled):
        if enabled:
            self.spinBox_cubeReward.setEnabled(True)
            self.checkBox_cubeEnd.setEnabled(True)
            self.checkBox_cubeStart.setEnabled(True)
            self.checkBox_cubePass.setEnabled(True)
            self.pbt_editCube.setEnabled(True)
        else:
            self.spinBox_cubeReward.setEnabled(False)
            self.checkBox_cubeEnd.setEnabled(False)
            self.checkBox_cubeStart.setEnabled(False)
            self.checkBox_cubePass.setEnabled(False)
            self.pbt_editCube.setEnabled(False)
    
    # 设置画笔编辑面板使能/失能
    def setPenSettingLayoutEnabled(self,enabled):
        if enabled:
            self.comboBox_penName.setEnabled(True)
            self.checkBox_penDrawing.setEnabled(True)
            self.pbt_deletePen.setEnabled(True)
        else:
            self.comboBox_penName.setEnabled(False)
            self.checkBox_penDrawing.setEnabled(False)
            self.pbt_deletePen.setEnabled(False)

    # 删除画笔
    def deletPen(self):
        penName = self.comboBox_penName.currentText()
        if penName != '':
            del self.map.penDict[penName]
        self.refreshPenComboBox()
        self.setMapSaved(False)

        # 此画笔绘制的所有方格类型改为 'modified'
        for i in range(self.map.gridWidget.row):
            for j in range(self.map.gridWidget.colum):
                if self.map.gridWidget.cubes[i][j].penName == penName:
                    self.map.gridWidget.cubes[i][j].penName = 'modified'
        self.map.gridWidget.update()

    # 新建画笔
    def newPen(self,name,color):
        slide = [0,0,0,0]
        reward = float(self.spinBox_cubeReward.value())
        isPassable = self.checkBox_cubePass.isChecked()

        pen = Pen(color,name,slide,isPassable,reward)
        self.map.penDict[pen.name] = pen
        # 刷新ui
        self.refreshPenComboBox()
        self.setMapSaved(False)       

    # 刷新画笔列表
    def refreshPenComboBox(self):
        self.comboBox_penName.clear()
        for penName in self.map.penDict:
            self.comboBox_penName.addItem(penName)
        self.comboBox_penName.setCurrentText('default')

    def setDisCostDiscount(self):
        self.map.disCostDiscount = float(self.spinBox_disCostDiscount.value())
        self.setMapSaved(False)

    def setMapSaved(self,saved):
        self.map.saved = saved
        if not saved:
            self.setWindowTitle('MapEditor - ' + self.map.name + '*')
        else:
            self.setWindowTitle('MapEditor - ' + self.map.name)

    def setEditorMode(self):
        # 进入画笔模式
        if self.checkBox_penDrawing.isChecked():
            # 失能方格编辑面板
            self.setCubeSettingLayoutEnabled(False)    
            self.map.gridWidget.isDrawingMode = True        
            
            # 若现有选中处于编辑状态的的块，清除标记
            if(self.map.gridWidget.cubeSelected != None):
                self.map.gridWidget.cubeSelected.selected = False
                self.map.gridWidget.update()
        else:
            self.map.gridWidget.isDrawingMode = False

    def check_cubeStart(self):
        if self.checkBox_cubeStart.isChecked():
            self.checkBox_cubeEnd.setEnabled(False)
        elif self.map.endCube == None:
            self.checkBox_cubeEnd.setEnabled(True)

    def check_cubeEnd(self):
        if self.checkBox_cubeEnd.isChecked():
            self.checkBox_cubeStart.setEnabled(False)
        elif self.map.startCube == None:
            self.checkBox_cubeStart.setEnabled(True)

    def setPenColor(self):
        col = QColorDialog.getColor() 
        if col.isValid(): 
            self.pbt_color.setStyleSheet('QPushButton{background:%s;}'%col.name())
            self.penSelected.color = col.name()
            self.map.gridWidget.update()
        
        self.setMapSaved(False)

    def showSaveFileDialog(self):
        if not self.map.isVisible:
            reply = QMessageBox.information(self,"错误！","未创建或打开地图，禁止保存！",QMessageBox.Yes)
            return 
        self.saveFileDialog.showWidget(self.map.name)

    # 更新地图
    def updateMap(self):
        if self.map.path == '':         # 没存过，弹出保存界面
            self.showSaveFileDialog()
        else:                           # 存过，直接更新
            self.saveMap(self.map.path,self.map.name)

    # 保存界面信号槽函数，把当前map存储到filePath
    def saveMap(self,filePath,fileName):
        if self.map.isVisible:
            self.map.name = fileName
            self.map.path = filePath
            self.file.saveMap(filePath,self.map)
            self.setWindowTitle('MapEditor - ' + self.map.name)
            self.map.saved = True
        else:
            QMessageBox.information(self,"错误！","未创建或打开地图，禁止保存！",QMessageBox.Yes)

    def loadMap(self,filePath):
        status = self.file.loadMap(filePath,self.map)
        if status != '加载成功':
            self.loadMapDialog.textBrowser.setText(status)
        else:
            self.map.name = self.file.fileName
            self.map.path = self.file.filePath
            self.map.isVisible = True
            self.loadMapDialog.close()
            self.refreshPenComboBox()
            self.map.gridWidget.update()
            self.updateGridWithColor()
            self.map.reloadSignal.emit()
            
    def newMap(self,row,colum):
        self.map.gridWidget.gridInit(row,colum)
        self.map.startCube = None
        self.map.endCube = None
        self.map.isVisible = True
        self.map.name = 'new'
        self.map.path = ''
        self.setMapSaved(False)

    def updateCube(self):
        oldCube = self.map.gridWidget.cubeSelected.copy()
        cube = self.map.gridWidget.cubeSelected
        slide = [0,0,0,0]
        reward = float(self.spinBox_cubeReward.value())
        isPassable = self.checkBox_cubePass.isChecked()
        isStart = self.checkBox_cubeStart.isChecked()
        isEnd = self.checkBox_cubeEnd.isChecked()
        cube.update(reward,slide,isPassable,isStart,isEnd)

        if self.map.startCube == None and cube.isStart:
            self.map.startCube = cube
        elif self.map.startCube == cube and not cube.isStart:
             self.map.startCube = None

        if self.map.endCube == None and cube.isEnd:
            self.map.endCube = cube
        elif self.map.endCube == cube and not cube.isEnd:
             self.map.endCube = None

        # 如果修改了关键参数，统一设置为modified类型，使用浅绿色显示
        if not operator.eq(cube.slide,oldCube.slide) or cube.reward != oldCube.reward:
            cube.penName = 'modified'

        self.map.gridWidget.update()
        self.showCubeSetting()
        self.setMapSaved(False)

    def updateGridWithColor(self):
        if self.checkBox_showGridWithColor.isChecked():
            self.map.gridWidget.showWithColor = True
        else:
            self.map.gridWidget.showWithColor = False
        self.map.gridWidget.update()

    # 在方格设定面板显示选中方格的信息
    def showCubeSetting(self):
        cube = self.map.gridWidget.cubeSelected
        if cube != None:
            self.label_cubeTitle.setText('方格信息')
            self.spinBox_cubeReward.setValue(cube.reward)
            self.checkBox_cubeStart.setChecked(cube.isStart)
            self.checkBox_cubeEnd.setChecked(cube.isEnd)
            self.checkBox_cubePass.setChecked(cube.isPassable)
            
            # 如果是墙，禁止编辑
            if not cube.isPassable:
                self.setCubeSettingLayoutEnabled(False)
                self.checkBox_cubePass.setEnabled(True)
                self.pbt_editCube.setEnabled(True)
            else:
                self.setCubeSettingLayoutEnabled(True)

                # 保证地图中最多只能存在一个起点和一个终点
                if (self.map.endCube != None and self.map.endCube != cube) or self.map.startCube == cube:
                    self.checkBox_cubeEnd.setEnabled(False)
                else:
                    self.checkBox_cubeEnd.setEnabled(True)

                if (self.map.startCube != None and self.map.startCube != cube) or self.map.endCube == cube:
                    self.checkBox_cubeStart.setEnabled(False)
                else:
                    self.checkBox_cubeStart.setEnabled(True)

            self.statusBar().showMessage("方格({},{})：type = {}; passable = {}".format(cube.row,cube.colum,cube.penName,str(cube.isPassable)))
        else:
            self.statusBar().showMessage("")
            self.setCubeSettingLayoutEnabled(False)

    def selectPen(self):
        penName = self.comboBox_penName.currentText()
        if penName != '':
            self.pbt_color.setStyleSheet('QPushButton{background:%s;}'%self.map.penDict[penName].color)
            self.penSelected = self.map.penDict[penName]
            self.map.gridWidget.penSelected = self.penSelected

            self.checkBox_penDrawing.setEnabled(True)
            self.pbt_deletePen.setEnabled(False)
            if penName == 'modified':
                self.checkBox_penDrawing.setChecked(False)
                self.checkBox_penDrawing.setEnabled(False)
                self.statusBar().showMessage("modified是手动编辑修改后可通行方格的统一类型，不可用于绘制")
            elif penName == 'wall':
                self.statusBar().showMessage("wall画笔用于绘制不可通行方格，仅增加不可通行属性，其它属性不变")
            elif penName == 'default':
                self.statusBar().showMessage("default画笔用于绘制无奖励的默认方格")
            else:
                info = self.penSelected.slide.copy()
                info.append(float(self.penSelected.reward))
                self.statusBar().showMessage("自定义画笔"+penName+"："+'info = '+str(info))
                self.pbt_deletePen.setEnabled(True)
            
    # 编辑完成转到controller，提示保存
    def editFinish(self):
        if self.map.isVisible and not self.map.saved:
            reply = QMessageBox.information(self,                         #使用infomation信息框
                                    "修改未保存！",
                                    "要把改动保存到地图配置文件吗",
                                    QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                if self.map.path == '':
                    self.showSaveFileDialog() 
                else: 
                    self.saveMap(self.map.path,self.map.name)
                    self.close()
            else:
                self.close()
        else:
            self.close()

        # 重新缓存相邻方格
        self.map.gridWidget.reStoreAllNeighborCube()


    # 关闭事件
    def closeEvent(self,event):
        self.checkBox_penDrawing.setChecked(False)
        self.map.disCostDiscount = float(self.spinBox_disCostDiscount.value())
        self.controller.show()
            
    def showEvent(self,event):
        self.map.showReward = True
        self.map.showPolicy = False
        self.map.showValue = False
        self.map.showColorByValue = False
        self.gridLayout.addWidget(self.map.gridWidget, 1, 2, 1, 1)  # 重新加载方格地图
        self.spinBox_disCostDiscount.setValue(self.map.disCostDiscount)
        self.refreshPenComboBox()

        if self.map.name != '':
            if not self.map.saved:
                self.setWindowTitle('MapEditor - ' + self.map.name+'*')
            else:
                self.setWindowTitle('MapEditor - ' + self.map.name)
        else:
            self.setWindowTitle('MapEditor')


    def loadGenerator(self,generator):
        try:                                                        
            self.generatorLayout.removeItem(generator.controlLayout())   # policyLayout解除管理
        except Exception:
            pass

        self.generatorControlLayout = generator.controlLayout()
        self.generatorLayout.addLayout(self.generatorControlLayout, 2, 0, 1, 1)
        #generator.setLayoutVisiable(True)