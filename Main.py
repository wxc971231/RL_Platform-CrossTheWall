import sys
from PyQt5.QtWidgets import QApplication
from core.Core import Controller

if __name__ == '__main__':
    app = QApplication(sys.argv)   
    controller = Controller()
    controller.show()
    sys.exit(app.exec_())   