import os
from PyQt5 import QtCore, QtWidgets, QtGui

# 保存地图时弹出的Dialog
class SaveFileDialog(QtWidgets.QMainWindow):
    saveMapSignal = QtCore.pyqtSignal(str,str) 
    saveWaveSignal = QtCore.pyqtSignal(str,str) 

    def __init__(self,fileType):
        super().__init__()    
        self.fileType = fileType
        self.folderPath = (os.getcwd()+'/'+fileType).replace('\\','/')
        self.setupUi()
        
    def setupUi(self):
        self.setObjectName("SaveFileDialog")
        self.resize(500, 120)
        self.setWindowIcon(QtGui.QIcon('src/images/grid.png'))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setMinimumSize(QtCore.QSize(500, 120))
        #self.setMaximumSize(QtCore.QSize(300, 120))
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label_fileName = QtWidgets.QLabel(self.centralwidget)
        self.label_fileName.setObjectName("label_fileName")
        self.gridLayout.addWidget(self.label_fileName, 1, 0, 1, 1)
        self.input_fileName = QtWidgets.QLineEdit(self.centralwidget)
        self.input_fileName.setObjectName("input_fileName")
        self.gridLayout.addWidget(self.input_fileName, 1, 1, 1, 1)
        self.pbt_getPath = QtWidgets.QPushButton(self.centralwidget)
        self.pbt_getPath.setObjectName("pbt_getPath")
        self.gridLayout.addWidget(self.pbt_getPath, 0, 0, 1, 2)
        self.pbt_save = QtWidgets.QPushButton(self.centralwidget)
        self.pbt_save.setObjectName("pbt_save")
        self.gridLayout.addWidget(self.pbt_save, 2, 0, 1, 2)
        self.gridLayout.setColumnStretch(1,0)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        self.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)
        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

        self.pbt_save.clicked.connect(self.saveMap)
        self.pbt_getPath.clicked.connect(self.getPath)

        self.statusBar().showMessage(str(self.folderPath))

    def showWidget(self,fileName=''):
        self.input_fileName.setText(fileName)
        self.statusBar().showMessage(self.folderPath)
        self.show()

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("SaveFileDialog", "save " + self.fileType))
        self.label_fileName.setText(_translate("self", "文件名:"))
        self.pbt_getPath.setText(_translate("self", "选择文件夹"))
        self.pbt_save.setText(_translate("self", "保存"))

    def getPath(self): 
        newFloderPath = QtWidgets.QFileDialog.getExistingDirectory(self,"选取文件夹",self.folderPath) # 起始路径
        if newFloderPath != '':
            self.folderPath = newFloderPath.replace('\\','/')
            self.statusBar().showMessage(str(self.folderPath))

    def saveMap(self):
        fileName = self.input_fileName.text()
        if fileName == '':
            self.statusBar().showMessage("请填写文件名")
        else:
            if self.fileType == 'map':
                filePath = self.folderPath+'/'+fileName+'.txt'
            elif self.fileType == 'wave':
                filePath = self.folderPath+'/'+fileName+'.wd'
            else:
                assert False

            # 如果有同名文件，进行提示
            if os.access(filePath, os.F_OK):
                reply = QtWidgets.QMessageBox.information(self,                         #使用infomation信息框
                                    "覆盖{}？".format(self.fileType),
                                    "此{}已存在，继续保存会覆盖原{}！".format(self.fileType,self.fileType),
                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                if reply == QtWidgets.QMessageBox.Yes:
                    self.sendSignal(filePath,fileName)
            else:
                self.sendSignal(filePath,fileName)
            self.close()
    
    def sendSignal(self,filePath,fileName):
        if self.fileType == 'map':
            self.saveMapSignal.emit(filePath,fileName)
        elif self.fileType == 'wave':
            self.saveWaveSignal.emit(filePath,fileName)
        else:
            assert False
