from PyQt5 import QtCore, QtWidgets, QtGui

# 存为画笔时弹出的Dialog
class PenDialog(QtWidgets.QMainWindow):
    penSignal = QtCore.pyqtSignal(str,str) 

    def __init__(self,mapEditor):
        super().__init__()    
        self.color = '#C8C8C8'
        self.mapEditor = mapEditor
        self.setupUi()
        
    def setupUi(self):
        self.setObjectName("PenDialog")
        self.resize(200, 100)
        self.setWindowIcon(QtGui.QIcon('src/images/grid.png'))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setMinimumSize(QtCore.QSize(230, 120))
        self.setMaximumSize(QtCore.QSize(230, 120))
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label_name = QtWidgets.QLabel(self.centralwidget)
        self.label_name.setObjectName("label_name")
        self.gridLayout.addWidget(self.label_name, 0, 0, 1, 1)
        self.input_name = QtWidgets.QLineEdit(self.centralwidget)
        self.input_name.setObjectName("input_name")
        self.gridLayout.addWidget(self.input_name, 0, 1, 1, 1)
        self.label_color = QtWidgets.QLabel(self.centralwidget)
        self.label_color.setObjectName("label_color")
        self.gridLayout.addWidget(self.label_color, 1, 0, 1, 1)
        self.pbt_color = QtWidgets.QPushButton(self.centralwidget)
        self.pbt_color.setObjectName("pbt_color")
        self.pbt_color.setStyleSheet('QPushButton{background:%s;}'%self.color)
        self.gridLayout.addWidget(self.pbt_color, 1, 1, 1, 1)
        self.pbt_confirm = QtWidgets.QPushButton(self.centralwidget)
        self.pbt_confirm.setObjectName("pbt_confirm")
        self.gridLayout.addWidget(self.pbt_confirm, 2, 0, 1, 2)
        self.gridLayout.setColumnStretch(1, 4)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        self.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)
        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

        self.pbt_confirm.clicked.connect(self.confirm)
        self.pbt_color.clicked.connect(self.getColor)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("PenDialog", "new pen"))
        self.label_name.setText(_translate("self", "名称:"))
        self.label_color.setText(_translate("self", "选色:"))
        self.pbt_confirm.setText(_translate("self", "确定"))

    def getColor(self): 
        col = QtWidgets.QColorDialog.getColor() 
        if col.isValid(): 
            self.pbt_color.setStyleSheet('QPushButton{background:%s;}'%col.name())
            self.color = col.name()

    def confirm(self):
        penName = self.input_name.text()
        if penName == '':
            self.statusBar().showMessage("请填写画笔名称")
        elif penName in self.mapEditor.map.penDict:
            self.statusBar().showMessage("此画笔名称已存在")
        else:
            self.penSignal.emit(penName,self.color)
            self.close()