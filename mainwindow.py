from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt

import utils
import sys
import functools
import config
import canvas

from canvas import Canvas
from loader import Loader
from imagedata_wapper import ImageDataWapper
from zoom_widget import ZoomWidget
from tool_bar import ToolBar
from tag_list_widget import TaglistWidget
from label_list_widget import LabelListWidgetItem, LabelListWidget


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setMouseTracking(True)
        self.loader = None
        self._config = config.get_default_config()

        self.labelListWidget = LabelListWidget(self)
        self.labelListDock = QtWidgets.QDockWidget('LabelList', self)
        self.labelListDock.setWidget(self.labelListWidget)

        self.colorTableWidget = TaglistWidget(self)
        self.colorTableWidget.loadFromJson(self._config['tags'])
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

        action = functools.partial(utils.createAction, self)
        open_ = action("&Open", self.open, 'open', u'Open image or label file')
        exit_ = action("&Exit", tip=u'Quit Application')
        openDir_ = action("&Open Dir", self.open, 'open')
        create_mode_ = action(
            "&Create Polygons",
            lambda: self.toggleDrawMode(canvas.Mode_polygon),
            'objects',
            u'Start drawing polygons')

        createRectangleMode_ = action(
            self.tr('Create Rectangle'),
            lambda: self.toggleDrawMode(canvas.Mode_rectangle),
            'objects',
            self.tr('Start drawing rectangles'),
            enabled=False,
        )
        createCircleMode_ = action(
            self.tr('Create Circle'),
            lambda: self.toggleDrawMode(canvas.Mode_circle),
            'objects',
            self.tr('Start drawing circles'),
            enabled=False,
        )
        createLineMode_ = action(
            self.tr('Create Line'),
            lambda: self.toggleDrawMode(canvas.Mode_line),
            'objects',
            self.tr('Start drawing lines'),
            enabled=False,
        )
        createPointMode_ = action(
            self.tr('Create Point'),
            lambda: self.toggleDrawMode(canvas.Mode_point),
            'objects',
            self.tr('Start drawing points'),
            enabled=False,
        )
        createLineStripMode_ = action(
            self.tr('Create LineStrip'),
            lambda: self.toggleDrawMode(canvas.Mode_linestrip),
            'objects',
            self.tr('Start drawing linestrip. Ctrl+LeftClick ends creation.'),
            enabled=False,
        )

        delete_ = action(
            self.tr('Delete Polygons'),
            self.deleteSelectedShape,
            'cancel',
            self.tr('Delete the selected polygons'),
            enabled=False)

        edit_ = action('&Edit Label', self.editLabel,
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
            createRectangleMode=createRectangleMode_,
            createCircleMode=createCircleMode_,
            createLineMode=createLineMode_,
            createPointMode=createPointMode_,
            createLineStripMode=createLineStripMode_,

            edit=edit_,
            fileMenu=(
                open_,
                openDir_,
                None,
                exit_,

            ),
            editMenu=(
                create_mode_,
                createRectangleMode_,
                createCircleMode_,
                createLineMode_,
                createPointMode_,
                createLineStripMode_,
                None,
                edit_,
                None,
                delete_,

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
        self.menu = self.addMenu("&Edit", self.actions.editMenu)

        # signal
        self.canvas.zoomChanged.connect(
            lambda v: self.zoom_widget.setValue(v*100))
        self.zoom_widget.valueChanged.connect(self.zoomChanged)
        self.canvas.centerChanged.connect(self.centerChanged)
        self.canvas.selectionChanged.connect(self.shapeSelectionChanged)
        self.canvas.newShape(self.newShape)

        self.initBarStatus()

    def initBarStatus(self):
        self.toggleDrawMode('polygon')

    def addLabel(self, shape):
        id, color, desc = shape.label
        list_item = LabelListWidgetItem(desc, shape)
        self.labelListWidget.addItem(list_item)

    def newShape(self):
        curItem = self.colorTableWidget.currentItem()
        label = self.colorTableWidget.getObjectByItem(curItem)
        shape = self.canvas.lastShape()
        shape.label = label
        addLabel(shape)

    def deleteSelectedShape(self):
        pass

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
        self.toggleDrawMode(None)

    def toggleDrawMode(self, mode):
        if mode:
            self.canvas.setMode(canvas.CREATE)
            self.canvas.setCreateMode(mode)

        else:
            self.canvas.setMode(canvas.EDIT)

        self.actions.create_mode.setEnabled(mode != canvas.Mode_polygon)
        self.actions.createRectangleMode.setEnabled(
            mode != canvas.Mode_rectangle)
        self.actions.createCircleMode.setEnabled(mode != canvas.Mode_circle)
        self.actions.createLineMode.setEnabled(mode != canvas.Mode_line)
        self.actions.createLineStripMode.setEnabled(
            mode != canvas.Mode_linestrip)
        self.actions.createPointMode.setEnabled(mode != canvas.Mode_point)
        self.actions.edit.setEnabled(not self.canvas.editing())

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
    win.loader.loadDicom(r'E:\testData\outputs\1.png')
    wapper = ImageDataWapper(win.loader.getImageData())
    win.canvas.image_wapper = wapper

    app.exec()
