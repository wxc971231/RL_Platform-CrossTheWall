# 选择地图时使用的文件树控件
from core.CustomWidgets.BaseTreeWidget import BaseTreeWidget
from PyQt5 import QtCore, QtGui, QtWidgets

class MapTreeWidget(BaseTreeWidget):
    def __init__(self,widget,folderPath):
        super().__init__(widget,folderPath)
    
    # 刷新文件树上的文件
    def refreshFiles(self,filePathList,fileSizeList):
        if filePathList == [''] or fileSizeList == ['']:
            return
        for f,s in zip(filePathList,fileSizeList):          
            child = QtWidgets.QTreeWidgetItem(self.floderRoot)             
            child.setText(0,f[f.rfind('/')+1:])            # 第一列是文件名

            child.setText(1,s +' KB   ')
            child.setTextAlignment(1,QtCore.Qt.AlignRight)  # 第二列是文件大小，设为右对齐
            self.floderRoot.addChild(child)           

            pos = f.rfind('.')                              # 设置ico 
            file_type =  f[pos+1:]
            if file_type in self.ImageDict:    
                child.setIcon(0,QtGui.QIcon(self.ImageDict[file_type]))
            else:
                child.setIcon(0,QtGui.QIcon(self.ImageDict['others']))