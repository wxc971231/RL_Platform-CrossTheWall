# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\Users\wwxc9\Desktop\3_CrossingWall\src\UI\CodeMatrix.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1095, 816)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.codeMatrix = QtWidgets.QWidget(self.centralwidget)
        self.codeMatrix.setObjectName("codeMatrix")
        self.gridLayout.addWidget(self.codeMatrix, 0, 0, 1, 3)
        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser.setObjectName("textBrowser")
        self.gridLayout.addWidget(self.textBrowser, 1, 2, 5, 1)
        self.pbt_updateColumCode = QtWidgets.QPushButton(self.centralwidget)
        self.pbt_updateColumCode.setObjectName("pbt_updateColumCode")
        self.gridLayout.addWidget(self.pbt_updateColumCode, 2, 0, 1, 2)
        self.pbt_updateAllColum = QtWidgets.QPushButton(self.centralwidget)
        self.pbt_updateAllColum.setObjectName("pbt_updateAllColum")
        self.gridLayout.addWidget(self.pbt_updateAllColum, 3, 0, 1, 1)
        self.pbt_updateAllProcess = QtWidgets.QProgressBar(self.centralwidget)
        self.pbt_updateAllProcess.setProperty("value", 24)
        self.pbt_updateAllProcess.setObjectName("pbt_updateAllProcess")
        self.gridLayout.addWidget(self.pbt_updateAllProcess, 3, 1, 1, 1)
        self.pbt_showColumSVC = QtWidgets.QPushButton(self.centralwidget)
        self.pbt_showColumSVC.setObjectName("pbt_showColumSVC")
        self.gridLayout.addWidget(self.pbt_showColumSVC, 4, 0, 1, 1)
        self.pbt_trainColumSVC = QtWidgets.QPushButton(self.centralwidget)
        self.pbt_trainColumSVC.setObjectName("pbt_trainColumSVC")
        self.gridLayout.addWidget(self.pbt_trainColumSVC, 4, 1, 1, 1)
        self.pbt_trainAllSVC = QtWidgets.QPushButton(self.centralwidget)
        self.pbt_trainAllSVC.setObjectName("pbt_trainAllSVC")
        self.gridLayout.addWidget(self.pbt_trainAllSVC, 5, 0, 1, 1)
        self.pbt_trainAllProcess = QtWidgets.QProgressBar(self.centralwidget)
        self.pbt_trainAllProcess.setProperty("value", 24)
        self.pbt_trainAllProcess.setObjectName("pbt_trainAllProcess")
        self.gridLayout.addWidget(self.pbt_trainAllProcess, 5, 1, 1, 1)
        self.comboBox_phase = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox_phase.setObjectName("comboBox_phase")
        self.gridLayout.addWidget(self.comboBox_phase, 1, 0, 1, 2)
        self.gridLayout.setColumnStretch(2, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1095, 23))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Code Matrix"))
        self.pbt_updateColumCode.setText(_translate("MainWindow", "更新此列编码"))
        self.pbt_updateAllColum.setText(_translate("MainWindow", "更新全部列编码"))
        self.pbt_showColumSVC.setText(_translate("MainWindow", "显示此二分类器"))
        self.pbt_trainColumSVC.setText(_translate("MainWindow", "训练此二分类器"))
        self.pbt_trainAllSVC.setText(_translate("MainWindow", "训练全部二分类器"))

