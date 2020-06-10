from qtpy import QtWidgets
import sys

from mainwindow import MainWindow


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    win = MainWindow()
    win.show()

    app.exec()
