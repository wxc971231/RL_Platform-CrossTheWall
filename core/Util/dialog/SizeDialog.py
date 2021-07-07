from PyQt5 import QtCore, QtWidgets, QtGui

# 新建地图时弹出的尺寸选择Dialog
class SizeDialog(QtWidgets.QMainWindow):
    sizeSignal = QtCore.pyqtSignal(int,int) 

    def __init__(self):
        super().__init__()    
        self.setupUi()

    def setupUi(self):
        self.setObjectName("SizeDialog")
        self.resize(200, 100)
        self.setWindowIcon(QtGui.QIcon('src/images/grid.png'))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setMinimumSize(QtCore.QSize(230, 100))
        self.setMaximumSize(QtCore.QSize(230, 100))
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label_row = QtWidgets.QLabel(self.centralwidget)
        self.label_row.setObjectName("label_row")
        self.gridLayout.addWidget(self.label_row, 0, 0, 1, 1)
        self.spinBox_row = QtWidgets.QSpinBox(self.centralwidget)
        self.spinBox_row.setObjectName("spinBox_row")
        self.gridLayout.addWidget(self.spinBox_row, 0, 1, 1, 1)
        self.label_colum = QtWidgets.QLabel(self.centralwidget)
        self.label_colum.setObjectName("label_colum")
        self.gridLayout.addWidget(self.label_colum, 1, 0, 1, 1)
        self.spinBox_colum = QtWidgets.QSpinBox(self.centralwidget)
        self.spinBox_colum.setObjectName("spinBox_colum")
        self.gridLayout.addWidget(self.spinBox_colum, 1, 1, 1, 1)
        self.pbt_confirm = QtWidgets.QPushButton(self.centralwidget)
        self.pbt_confirm.setObjectName("pbt_confirm")
        self.gridLayout.addWidget(self.pbt_confirm, 2, 0, 1, 2)
        self.gridLayout.setColumnStretch(0, 1)
        self.gridLayout.setColumnStretch(1, 4)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        self.setCentralWidget(self.centralwidget)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

        self.spinBox_colum.setValue(30)
        self.spinBox_row.setValue(20)
        self.pbt_confirm.clicked.connect(self.confirm)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("SizeDialog", "map size"))
        self.label_row.setText(_translate("self", "行数:"))
        self.label_colum.setText(_translate("self", "列数:"))
        self.pbt_confirm.setText(_translate("self", "确定"))

    def confirm(self):
        self.sizeSignal.emit(self.spinBox_row.value(),self.spinBox_colum.value())
        self.close()