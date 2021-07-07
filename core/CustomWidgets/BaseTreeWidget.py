from PyQt5 import QtCore, QtGui, QtWidgets
from core.Util import QABCMeta
import abc
import os

# 文件树类,继承自QTreeWidget
class BaseTreeWidget(QtWidgets.QTreeWidget,metaclass = QABCMeta):
    tree_refresh_signal = QtCore.pyqtSignal(str,list,list)

    def __init__(self,widget,folderPath):
        super().__init__(widget)
        self.folderPath = folderPath    # 文件树的目录
        self.filePath = ''              # 最近一次选中的文件          
        self.filePathList = []          # 当前路径下所有文件路径（不含文件夹）
        self.ImageDict = dict([         # 资源路径字典
                            ('txt'      ,   'src/images/txt.png'),
                            ('others'   ,   'src/images/others.png'),
                            ('floder'   ,   'src/images/floder.png'),
                            ('back'     ,   'src/images/back.png')
                            ])

        self.setupUi()

    def setupUi(self):
        self.setColumnCount(2)
        self.setHeaderLabels(['file','fileSize'])
        self.setColumnWidth(0,200)      # 第一列宽度200
        self.setColumnWidth(1,60)       # 第二列宽度300

        self.backNode = QtWidgets.QTreeWidgetItem(self)
        self.backNode.setText(0,'<Back>')
        self.backNode.setIcon(0,QtGui.QIcon(self.ImageDict['back']))
        self.backNode.setDisabled(True)

        self.floderRoot = QtWidgets.QTreeWidgetItem(self)
        self.floderRoot.setIcon(0,QtGui.QIcon(self.ImageDict['floder']))
        self.floderRoot.setText(0,'Current dir')

    # 清空file_root节点
    def clearFileTree(self):
        for i in range(self.floderRoot.childCount()):
            self.floderRoot.removeChild(self.floderRoot.child(0))

    # 刷新文件树上的文件夹
    def refreshFloders(self,floderNameList):
        if floderNameList == ['']:                                 
            return
        for f in floderNameList:        
            floder = QtWidgets.QTreeWidgetItem(self.floderRoot)  
            floder.setText(0,f)
            floder.setText(1,'-    ')
            floder.setTextAlignment(1,QtCore.Qt.AlignRight)  # 第二列设为右对齐
            floder.setIcon(0,QtGui.QIcon(self.ImageDict['floder']))
            self.floderRoot.addChild(floder)
    
    # 刷新文件树
    def refreshFileTree(self,path):
        # 先遍历当前文件夹，分离文件夹和文件
        try:
            items = os.listdir(path)    # 获取路径下所有文件名
        except PermissionError:
            print("无访问权限")
            return False

        self.folderPath = path
        root = self.floderRoot

        floderNameList,filePathList,fileSizeList = [],[],[]
        for item in items:
            filePath = os.path.join(path, item).replace('\\','/')
            if os.path.isdir(filePath):
                floderNameList.append(item)
            else:
                fileSize = str(round(os.stat(filePath).st_size/1024))
                filePathList.append(filePath)
                fileSizeList.append(fileSize)
        self.filePathList = filePathList

        # 先把以前的treeWidget清空
        self.clearFileTree() 
                               
        # 设置根节点
        root_name = path[path.rfind('/')+1:] 
        if root_name == '' or root_name[-1] == ':': # 已到根目录 
            root_name = path[0:path.rfind('/')]
            self.backNode.setDisabled(True)
            self.setCurrentItem(self.floderRoot.child(1))
            print('根目录')
        else:                                       # 非根目录
            self.backNode.setDisabled(False)
        root.setText(0,root_name)

        # 刷新显示文件树
        self.refreshFloders(floderNameList)
        self.refreshFiles(filePathList,fileSizeList) 

        # 展开根节点
        self.floderRoot.setExpanded(True)
        return True

    # 重新加载当前路径下文件树
    def refreshCurrentFileTree(self):
        self.refreshFileTree(self.folderPath)

    # 在treeWidget中选择节点
    def nodeSelected(self):
        item = self.currentItem()
        if item!= None and (item.parent() != None or item.text(0) == '<Back>'):
            nodePath = self.folderPath

            # 回上层目录
            if item.text(0) == '<Back>':
                if self.backNode.isDisabled():
                    return False,"已到磁盘根目录"
            
                path = self.folderPath
                path = path[0 : path.rfind('/')]
                self.folderPath = path if path[-1] != ':' else path + '/'
                self.refreshFileTree(self.folderPath)

                return False,self.folderPath
            else:
                nodePath = nodePath + '/' + item.text(0) if nodePath[-1] != '/' else nodePath + item.text(0)
                # 进入子目录
                if os.path.isdir(nodePath):                # 确认是目录
                    if not self.refreshFileTree(nodePath): # 刷新文件树
                        return False,"无访问权限"
                    else:
                        self.folderPath = nodePath         # 设定为新的根目录
                        return False,nodePath
                # 选中文件
                else:
                    self.filePath = nodePath
                    self.selectFile()
                    return True,nodePath

    def selectFile(self):
        pass

    @abc.abstractmethod
    def refreshFiles(self,filePathList,fileSizeList):
        pass