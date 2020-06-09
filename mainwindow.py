from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt

import utils
import sys
import functools

import canvas
from canvas import Canvas
from loader import Loader
from imagedata_wapper import ImageDataWapper
from zoom_widget import ZoomWidget
from tool_bar import ToolBar


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setMouseTracking(True)
        self.loader = None

        self.labelListWidget = QtWidgets.QListWidget(self)
        self.labelListDock = QtWidgets.QDockWidget('LabelList', self)
        self.labelListDock.setWidget(self.labelListWidget)

        self.colorTableWidget = QtWidgets.QListWidget(self)
        self.colorTableDock = QtWidgets.QDockWidget('ColorTable', self)
        self.colorTableDock.setWidget(self.colorTableWidget)

        self.canvas = Canvas(self)
        scrollArea = QtWidgets.QScrollArea()
        scrollArea.setWidget(self.canvas)
        scrollArea.setWidgetResizable(True)

        self.scrollBars = {
            Qt.Horizontal: scrollArea.horizontalScrollBar(),
            Qt.Vertical: scrollArea.verticalScrollBar(),
        }

        self.addDockWidget(Qt.RightDockWidgetArea, self.labelListDock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.colorTableDock)

        self.setCentralWidget(scrollArea)
        self.statusBar().show()
        self.resize(1200, 800)

        open_ = utils.createAction(
            self, "&Open", self.open, 'open', u'Open image or label file')
        exit_ = utils.createAction(self, "&Exit", tip=u'Quit Application')
        openDir_ = utils.createAction(self, "&Open Dir", self.open, 'open')
        create_mode_ = utils.createAction(self, "&Create Polygons", lambda: self.setCreateMode(
            'polygon'), 'objects', u'Start drawing polygons')

        edit_ = utils.createAction(self, '&Edit Label', self.editLabel,
                                   'edit', 'Modify the label of the selected polygon',
                                   enabled=False)
        self.zoom_widget = ZoomWidget()
        zoom_ = QtWidgets.QWidgetAction(self)
        zoom_.setDefaultWidget(self.zoom_widget)

        self.actions = utils.struct(
            open=open_,
            exit=exit_,
            openDir=openDir_,
            create_mode=create_mode_,
            edit=edit_,

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
            create_mode_,
            edit_,
            None,
            zoom_

        )
        self.toolbar = ToolBar('toolbar')
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.addToolBar(Qt.TopToolBarArea, self.toolbar)
        utils.addActions(self.toolbar, self.tools_actions)

        self.menu = self.addMenu("&File", self.actions.fileMenu)
        # signal

        self.canvas.zoomChanged.connect(
            lambda v: self.zoom_widget.setValue(v*100))
        self.zoom_widget.valueChanged.connect(self.zoomChanged)
        self.canvas.centerChanged.connect(self.centerChanged)
        self.canvas.selectionChanged.connect(self.shapeSelectionChanged)

        self.initBarStatus()

    def initBarStatus(self):
        self.setCreateMode('polygon')

    def shapeSelectionChanged(self, selected_shapes):
        # self._noSelectionSlot = True
        # for shape in self.canvas.selectedShapes:
        #     shape.selected = False
        # self.labelList.clearSelection()
        self.canvas.selectedShapes = selected_shapes
        for shape in self.canvas.selectedShapes:
            shape.selected = True
            # item = self.labelList.get_item_from_shape(shape)
            # item.setSelected(True)
        # self._noSelectionSlot = False
        # n_selected = len(selected_shapes)
        # self.actions.delete.setEnabled(n_selected)
        # self.actions.copy.setEnabled(n_selected)
        # self.actions.edit.setEnabled(n_selected == 1)
        # self.actions.shapeLineColor.setEnabled(n_selected)
        # self.actions.shapeFillColor.setEnabled(n_selected)

    def editLabel(self):
        self.canvas.setMode(canvas.EDIT)
        self.actions.edit.setEnabled(False)
        self.actions.create_mode.setEnabled(True)

    def setCreateMode(self, mode):
        if mode:
            self.canvas.setMode(canvas.CREATE)
            self.canvas.setCreateMode(mode)
            self.actions.edit.setEnabled(True)
            self.actions.create_mode.setEnabled(False)
        else:
            self.canvas.setMode(canvas.EDIT)

    def centerChanged(self, delta):
        units = - delta * 0.1
        bar_x = self.scrollBars[Qt.Horizontal]
        bar_y = self.scrollBars[Qt.Vertical]
        print('bar val:{0} bar step:{1} delta:{2}'.format(
            bar_y.value(), bar_y.singleStep(), delta))

        bar_x.setValue(bar_x.value() + bar_x.singleStep() * units.x())
        bar_y.setValue(bar_y.value() + bar_y.singleStep() * units.y())

    def zoomChanged(self, scale):
        self.updateCanvas()

    def updateCanvas(self):
        self.canvas.scale = self.zoom_widget.value() * 0.01
        self.canvas.adjustSize()
        self.canvas.update()

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
        self.updateCanvas()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    win = MainWindow()
    win.show()
    win.loader = Loader()
    win.loader.loadDicom(r'F:\github\labeldicom_cpp\testData\5_a.png')
    wapper = ImageDataWapper(win.loader.getImageData())
    win.canvas.image_wapper = wapper

    app.exec()
