from qtpy import QtWidgets
import sys
import utils
from mainwindow import MainWindow


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName('LabelDicom')
    app.setWindowIcon(utils.createIcon('icon'))

    win = MainWindow()
    win.show()

    app.exec()
