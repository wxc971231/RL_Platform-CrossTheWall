# 选择波形时使用的文件树控件
from core.CustomWidgets.BaseTreeWidget import BaseTreeWidget
from PyQt5 import QtCore, QtWidgets

class WaveTreeWidget(BaseTreeWidget):
    def __init__(self,widget,folderPath):
        super().__init__(widget,folderPath)
        self.wavePathList = []

    # 刷新文件树上的文件
    def refreshFiles(self,filePathList,fileSizeList):
        if filePathList == [''] or fileSizeList == ['']:
            return
        for f,s in zip(filePathList,fileSizeList):          
            child = QtWidgets.QTreeWidgetItem(self.floderRoot)             
            child.setText(0,f[f.rfind('/')+1:])             # 第一列是文件名

            child.setText(1,s +' KB   ')
            child.setTextAlignment(1,QtCore.Qt.AlignRight)  # 第二列是文件大小，设为右对齐
            self.floderRoot.addChild(child)           

            child.setCheckState(0, QtCore.Qt.Checked if f in self.wavePathList else QtCore.Qt.Unchecked)  # check box

    def selectFile(self):
        item = self.currentItem()
        if item != None:
            if item.checkState(0) == QtCore.Qt.Unchecked:
                self.wavePathList.append(self.filePath)
                item.setCheckState(0,QtCore.Qt.Checked)
            else:
                try:
                    self.wavePathList.remove(self.filePath)
                    item.setCheckState(0,QtCore.Qt.Unchecked)
                except Exception as e:
                    print(e)
                        
    def selectAllFiles(self):
        self.wavePathList.extend(self.filePathList.copy())
        for i in range(self.floderRoot.childCount()):
            if self.floderRoot.child(i).text(1) != '-    ':
                self.floderRoot.child(i).setCheckState(0,QtCore.Qt.Checked)
        
    def selectNoFiles(self):
        self.wavePathList.clear()
        for i in range(self.floderRoot.childCount()):
            if self.floderRoot.child(i).text(1)!= '-    ':
                self.floderRoot.child(i).setCheckState(0,QtCore.Qt.Unchecked)
