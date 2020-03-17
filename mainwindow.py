from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt

from canvas import Canvas


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.labelListWidget = QtWidgets.QListWidget(self)
        self.labelListDock = QtWidgets.QDockWidget('LabelList', self)
        self.labelListDock.setWidget(self.labelListWidget)

        self.colorTableWidget = QtWidgets.QListWidget(self)
        self.colorTableDock = QtWidgets.QDockWidget('ColorTable', self)
        self.colorTableDock.setWidget(self.colorTableWidget)

        self.canvas = Canvas()
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidget(self.canvas)
        scroll_area.setWidgetResizable(True)

        self.addDockWidget(Qt.RightDockWidgetArea, self.labelListDock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.colorTableDock)

        self.setCentralWidget(scroll_area)

        self.statusBar().show()

        self.resize(800, 600)
