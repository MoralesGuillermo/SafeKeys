"""Main logic of safekeys"""
import sys
from PyQt5.QtWidgets import QApplication
import app as myApp

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # TODO: LOGIC
    safekeys = myApp.App()
    safekeys.main_window()
    sys.exit(app.exec_())

