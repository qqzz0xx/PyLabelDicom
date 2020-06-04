from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt

from canvas import Canvas
import utils
import sys
from loader import Loader
from imagedata_wapper import ImageDataWapper


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.loader = None

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

        open_ = utils.creatAction(self, "Open", self.open)
        exit_ = utils.creatAction(self, "Exit")

        self.actions = utils.struct(
            open=open_,
            fileMenu=(
                open_,
                None,
                exit_,

            ))

        self.menu = self.addMenu("&File", self.actions.fileMenu)

    def addMenu(self, title, actions=None):
        menu = self.menuBar().addMenu(title)
        if actions:
            utils.addActions(menu, actions)
        return menu

    def open(self):
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self)
        print(fileName)

        if fileName:
            self.loader = Loader()
            self.loader.loadDicom(fileName)

            wapper = ImageDataWapper(self.loader.getImageData())
            self.canvas.image_wapper = wapper


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    win = MainWindow()
    win.show()

    app.exec()
