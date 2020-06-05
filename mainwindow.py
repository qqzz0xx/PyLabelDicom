from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt

from canvas import Canvas
import utils
import sys
from loader import Loader
from imagedata_wapper import ImageDataWapper
from zoom_widget import ZoomWidget
from tool_bar import ToolBar

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

        self.canvas = Canvas(self)
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidget(self.canvas)
        scroll_area.setWidgetResizable(True)

        self.addDockWidget(Qt.RightDockWidgetArea, self.labelListDock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.colorTableDock)

        self.setCentralWidget(scroll_area)
        self.statusBar().show()
        self.resize(800, 600)

        open_ = utils.createAction(self, "&Open", self.open, 'open')
        exit_ = utils.createAction(self, "&Exit")
        openDir_ = utils.createAction(self, "&Open Dir", self.open, 'open')

        zoom_widget = ZoomWidget()
        zoom_ = QtWidgets.QWidgetAction(self)
        zoom_.setDefaultWidget(zoom_widget)

        self.actions = utils.struct(
            open=open_,
            fileMenu=(
                open_,
                openDir_,
                None,
                exit_,

            ))

        self.tools_actions = (
            open_,
            openDir_,
            None,
            zoom_

        )
        self.toolbar = ToolBar('toolbar')
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.addToolBar(Qt.TopToolBarArea, self.toolbar)
        utils.addActions(self.toolbar, self.tools_actions)

        self.menu = self.addMenu("&File", self.actions.fileMenu)

    def addMenu(self, title, actions=None):
        menu = self.menuBar().addMenu(title)
        if actions:
            utils.addActions(menu, actions)
        return menu

    def showStatusTips(self, tips, dt=3000):
        self.statusBar().showMessage(tips, 3000)

    def open(self):
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self)
        print(fileName)

        if fileName and fileName != '':
            self.loader = Loader()
            self.loader.loadDicom(fileName)

            wapper = ImageDataWapper(self.loader.getImageData())
            self.canvas.image_wapper = wapper

    def resizeEvent(self, event):
        self.canvas.adjustSize()
        self.canvas.update()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    win = MainWindow()
    win.show()

    app.exec()
