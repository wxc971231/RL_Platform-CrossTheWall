# 在定义抽象类时，避免 QObject 元类不是 abc.ABCMeta 导致的冲突
from PyQt5 import QtCore
import abc

class QABCMeta(type(QtCore.QObject), abc.ABCMeta):
    pass