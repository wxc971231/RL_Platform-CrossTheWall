# 加载地图时弹出的文件选择Dialog，包含地图选择和波形选择两个子类
from PyQt5 import QtCore, QtWidgets, QtGui
from core.CustomWidgets import MapTreeWidget,WaveTreeWidget
from core.Util import QABCMeta
import abc

class LoadFileDialog(QtWidgets.QMainWindow,metaclass = QABCMeta):
    def __init__(self,fileType,folderPath):
        super().__init__()
        self.fileType = fileType
        self.folderPath = folderPath
        self.setupUi()   

    # 切换文件夹
    def getPath(self):
        newFloderPath = QtWidgets.QFileDialog.getExistingDirectory(self,"选取文件夹",self.treeWidget.folderPath) # 起始路径
        if newFloderPath != '':
            self.treeWidget.folderPath = newFloderPath.replace('\\','/')
            self.treeWidget.refreshFileTree(self.treeWidget.folderPath)
            self.statusBar().showMessage(str(self.treeWidget.folderPath))
    
    # 选中item
    def chooseItem(self,mode):
        try:
            isFile,nodePath = self.treeWidget.nodeSelected()
        except TypeError:
            isFile,nodePath = False,''

        if nodePath == '无访问权限' or nodePath == '已到磁盘根目录':
            self.textBrowser.setText(nodePath)
        else:
            self.statusBar().showMessage(nodePath) 

        if isFile and mode == 'doubleClick':
            self.loadFile()

        return isFile,nodePath

    def showEvent(self,event):
        self.textBrowser.setText('')
        self.treeWidget.refreshFileTree(self.treeWidget.folderPath)
        self.statusBar().showMessage(str(self.treeWidget.folderPath))

    @abc.abstractmethod
    def setupUi(self):
        pass

    @abc.abstractmethod
    def loadFile(self):
        pass
    
# 加载地图时弹出的文件选择Dialog
class LoadMapDialog(LoadFileDialog):
    loadMapSignal = QtCore.pyqtSignal(str)
    
    def __init__(self,folderPath):
        super().__init__('map',folderPath)

    def setupUi(self):
        self.resize(759, 628)
        self.setWindowTitle("load " + self.fileType)
        self.setWindowIcon(QtGui.QIcon('src/images/grid.png'))
        self.centralwidget = QtWidgets.QWidget(self)
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.pbt_load = QtWidgets.QPushButton(self.centralwidget)
        self.pbt_load.setText("加载")
        self.pbt_load.setEnabled(True)
        self.gridLayout.addWidget(self.pbt_load, 5, 1, 1, 1)
        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.gridLayout.addWidget(self.textBrowser, 0, 1, 5, 1)
        self.pbt_getPath = QtWidgets.QPushButton(self.centralwidget)
        self.pbt_getPath.setText("选择文件夹")
        self.gridLayout.addWidget(self.pbt_getPath, 0, 0, 1, 1)
        self.treeWidget = MapTreeWidget(self.centralwidget,self.folderPath)
        self.gridLayout.addWidget(self.treeWidget, 1, 0, 5, 1)
        self.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.setStatusBar(self.statusbar)
        self.gridLayout.setColumnStretch(1, 1)

        QtCore.QMetaObject.connectSlotsByName(self)

        self.pbt_getPath.clicked.connect(self.getPath)
        self.pbt_load.clicked.connect(self.loadFile)
        self.treeWidget.clicked.connect(lambda:self.chooseItem('singleClick'))
        self.treeWidget.doubleClicked.connect(lambda:self.chooseItem('doubleClick'))

    def chooseItem(self,mode):
        isFile,nodePath = super().chooseItem(mode)
        # 接收读取的内容，并显示到多行文本框中
        if isFile and nodePath[-4:] == '.txt':
            with open(nodePath,'r') as f:
                data = f.read()
                self.textBrowser.setText(data)
        
    def loadFile(self):
        self.loadMapSignal.emit(self.treeWidget.filePath)


# 加载波形时弹出的文件选择Dialog
class LoadWaveDialog(LoadFileDialog):
    loadWaveSignal = QtCore.pyqtSignal(list)

    def __init__(self,folderPath):
        super().__init__('wave',folderPath)

    def setupUi(self):
        self.resize(759, 628)
        self.setWindowTitle("load " + self.fileType)
        self.setWindowIcon(QtGui.QIcon('src/images/grid.png'))
        self.centralwidget = QtWidgets.QWidget(self)
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)

        self.controlLayout = QtWidgets.QGridLayout()
        self.gridLayout.addLayout(self.controlLayout, 0, 0, 1, 1)

        self.treeWidget = WaveTreeWidget(self.centralwidget,self.folderPath)
        self.gridLayout.addWidget(self.treeWidget, 1, 0, 5, 1)

        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.gridLayout.addWidget(self.textBrowser, 0, 1, 6, 1)

        self.pbt_getPath = QtWidgets.QPushButton(self.centralwidget)
        self.pbt_getPath.setText("选择文件夹")
        self.controlLayout.addWidget(self.pbt_getPath, 0, 0, 1, 2)

        self.pbt_all = QtWidgets.QPushButton(self.centralwidget)
        self.pbt_all.setText("本页全选")
        self.pbt_all.setEnabled(True)
        
        self.controlLayout.addWidget(self.pbt_all, 1, 0, 1, 1)

        self.pbt_clear = QtWidgets.QPushButton(self.centralwidget)
        self.pbt_clear.setText("清空已选")
        self.pbt_clear.setEnabled(True)
        self.controlLayout.addWidget(self.pbt_clear, 1, 1, 1, 1)

        self.pbt_load = QtWidgets.QPushButton(self.centralwidget)
        self.pbt_load.setText("加载选中波形")
        self.pbt_load.setEnabled(True)
        self.controlLayout.addWidget(self.pbt_load, 2, 0, 1, 2)

        self.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.setStatusBar(self.statusbar)
        self.gridLayout.setColumnStretch(1, 1)

        QtCore.QMetaObject.connectSlotsByName(self)

        self.pbt_getPath.clicked.connect(self.getPath)
        self.pbt_load.clicked.connect(self.loadFile)
        self.pbt_all.clicked.connect(self.treeWidget.selectAllFiles)
        self.pbt_clear.clicked.connect(self.treeWidget.selectNoFiles)
        self.treeWidget.clicked.connect(lambda:self.chooseItem('singleClick'))

    def loadFile(self):
        self.loadWaveSignal.emit(self.treeWidget.wavePathList)

    def showWidget(self):
        # 窗口跳到最前端
        self.activateWindow()
        self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        self.showNormal()