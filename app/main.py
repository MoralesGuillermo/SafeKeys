"""Main logic of safekeys"""
import sys
from PyQt5.QtWidgets import QApplication
import app as myApp

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName("Safekeys")

    safekeys = myApp.MainWindow()

    sys.exit(app.exec_())

