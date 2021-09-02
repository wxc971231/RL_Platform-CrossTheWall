from PyQt5 import QtCore, QtWidgets, QtGui
from core.Util.Function import RGB2Hex

# 存为画笔时弹出的Dialog
class PenDialog(QtWidgets.QMainWindow):
    newPenSignal = QtCore.pyqtSignal(str,str,float,str) 
    editPenSignal = QtCore.pyqtSignal(str,str,float,str) 

    def __init__(self,mapEditor):
        super().__init__()    
        self.mapEditor = mapEditor
        self.color = '#C8C8C8'         
        self.mode = 'new' # ['new','edit']
        self.attributes = ['起点','终点','墙壁','普通']
        self.setupUi()
        
    def setupUi(self):
        self.setObjectName("PenDialog")
        self.resize(230, 100)
        self.setWindowIcon(QtGui.QIcon('src/images/grid.png'))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setMaximumWidth(230)
        self.setMinimumWidth(230)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label_name = QtWidgets.QLabel(self.centralwidget)
        self.label_name.setText("名称：")
        self.gridLayout.addWidget(self.label_name, 0, 0, 1, 1)
        self.input_name = QtWidgets.QLineEdit(self.centralwidget)
        self.input_name.setObjectName("input_name")
        self.gridLayout.addWidget(self.input_name, 0, 1, 1, 1)

        self.label_reward = QtWidgets.QLabel(self.centralwidget)
        self.label_reward.setText("奖励：")
        self.gridLayout.addWidget(self.label_reward, 1, 0, 1, 1)
        self.spinBox_cubeReward = QtWidgets.QDoubleSpinBox(self.centralwidget)
        self.spinBox_cubeReward.setObjectName("spinBox_cubeReward")
        self.spinBox_cubeReward.setMaximum(1000)
        self.spinBox_cubeReward.setMinimum(-1000)
        self.gridLayout.addWidget(self.spinBox_cubeReward, 1, 1, 1, 1)

        self.label_color = QtWidgets.QLabel(self.centralwidget)
        self.label_color.setText("选色：")
        self.gridLayout.addWidget(self.label_color, 2, 0, 1, 1)
        self.pbt_color = QtWidgets.QPushButton(self.centralwidget)
        self.pbt_color.setObjectName("pbt_color")
        self.gridLayout.addWidget(self.pbt_color, 2, 1, 1, 1)
        self.pbt_confirm = QtWidgets.QPushButton(self.centralwidget)

        self.comboBox_attribute = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox_attribute.addItems(self.attributes)
        
        self.gridLayout.addWidget(self.comboBox_attribute, 3, 1, 1, 1)
        self.label_attribute = QtWidgets.QLabel(self.centralwidget)
        self.label_attribute.setText('属性：')
        self.gridLayout.addWidget(self.label_attribute, 3, 0, 1, 1)        

        self.pbt_confirm.setText("确定")
        self.gridLayout.addWidget(self.pbt_confirm, 4, 0, 1, 2)
        self.gridLayout.setColumnStretch(1, 4)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        self.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)
    
        self.pbt_confirm.clicked.connect(self.confirm)
        self.pbt_color.clicked.connect(self.getColor)

    def getColor(self): 
        col = QtWidgets.QColorDialog.getColor() 
        if col.isValid(): 
            self.pbt_color.setStyleSheet('QPushButton{background:%s;}'%col.name())
            self.color = col.name()

    def confirm(self):
        penName = self.input_name.text()
        reward = float(self.spinBox_cubeReward.value())
        attribute = self.comboBox_attribute.currentText()
        if penName == '':
            self.statusBar().showMessage("请填写画笔名称")
        elif penName in self.mapEditor.map.penDict and self.mode == 'new':
            self.statusBar().showMessage("此画笔名称已存在")
        else:
            if self.mode == 'new':
                self.newPenSignal.emit(penName,self.color,reward,attribute)
            elif self.mode == 'edit':
                self.editPenSignal.emit(penName,self.color,reward,attribute)
            else:
                assert False
            self.close()

    # 根据选中的方块设定画笔参数
    def showWidgetByCube(self):
        cubeSelected = self.mapEditor.map.gridWidget.cubeSelected
        color = cubeSelected.map.penDict[cubeSelected.penName].color
        reward = cubeSelected.reward
    
        if not cubeSelected.isPassable:
            attribute = '墙壁'
        elif cubeSelected.isStart:
            attribute = '起点'
        elif cubeSelected.isEnd:
            attribute = '终点'
        else:
            attribute = '普通'

        self.setWindowTitle('New Pen')
        self.mode = 'new'
        self.spinBox_cubeReward.setValue(reward)
        self.pbt_color.setStyleSheet('QPushButton{background:%s;}'%color)
        self.comboBox_attribute.setCurrentText(attribute)
        self.statusBar().showMessage('')
        self.show()

    # 根据选中的画笔设定画笔参数
    def showWidgetByPen(self,pen):
        if not pen.isPassable:
            attribute = '墙壁'
        elif pen.isStart:
            attribute = '起点'
        elif pen.isEnd:
            attribute = '终点'
        else:
            attribute = '普通'

        self.setWindowTitle('Edit Pen')
        self.mode = 'edit'
        self.color = pen.color
        self.input_name.setText(pen.name)
        self.spinBox_cubeReward.setValue(pen.reward)
        self.pbt_color.setStyleSheet('QPushButton{background:%s;}'%pen.color)
        self.comboBox_attribute.setCurrentText(attribute)
        self.statusBar().showMessage('')

        self.show()