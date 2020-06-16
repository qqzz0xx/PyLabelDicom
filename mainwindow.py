from qtpy import QtWidgets, QtGui
from qtpy.QtCore import Qt

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
from view import DicomView


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setMouseTracking(True)
        self.loader = None
        self.dirty = False
        self._selectSlotBlock = False
        self._config = config.get_default_config()

        self.labelListWidget = LabelListWidget(self)
        self.labelListDock = QtWidgets.QDockWidget(
            'Displayed Label List', self)
        self.labelListDock.setWidget(self.labelListWidget)

        self.allLabelList = LabelListWidget(self)
        self.allLabelListDock = QtWidgets.QDockWidget('Label List', self)
        self.allLabelListDock.setWidget(self.allLabelList)

        self.colorTableWidget = TaglistWidget(self)
        self.colorTableWidget.loadFromJson(self._config['tags'])
        self.colorTableDock = QtWidgets.QDockWidget('Color Table', self)
        self.colorTableDock.setWidget(self.colorTableWidget)

        self.addDockWidget(Qt.RightDockWidgetArea, self.labelListDock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.colorTableDock)
        self.tabifyDockWidget(self.labelListDock, self.allLabelListDock)

        self.view = DicomView()

        self.setCentralWidget(self.view)
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
            delete=delete_,
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
            ),
            viewMenu=(
                self.labelListDock.toggleViewAction(),
                self.colorTableDock.toggleViewAction(),
            )
        )

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
        # utils.addActions(self.canvas.menu, self.actions.editMenu)
        self.view.addMenu(self.actions.editMenu)

        self.menu = self.addMenu("&File", self.actions.fileMenu)
        self.menu = self.addMenu("&Edit", self.actions.editMenu)
        self.menu = self.addMenu("&View", self.actions.viewMenu)
        # signal
        self.view.zoomChanged.connect(
            lambda canvas, v: self.zoom_widget.setValue(v*100))
        self.view.centerChanged.connect(
            lambda canvas, v: self.centerChanged(canvas, v))
        self.view.nextFrame.connect(
            lambda canvas, v: self.nextFrame(canvas, v))
        self.view.selectionChanged.connect(
            lambda canvas, v: self.shapeSelectionChanged(canvas, v))
        self.view.newShape.connect(
            lambda canvas, v: self.newShape(canvas, v))
        self.view.onMousePress.connect(
            lambda canvas, v: self.showStatusTips(
                "world pos: [{0},{1}]".format(v.x(), v.y()))
        )

        self.zoom_widget.valueChanged.connect(self.zoomChanged)
        self.labelListWidget.itemChanged.connect(self.labelItemChanged)
        self.labelListWidget.itemDoubleClicked.connect(self.editLabel)
        self.labelListWidget.itemSelectionChanged.connect(
            self.labelSelectionChanged)
        self.labelListWidget.itemDeleteSelected.connect(
            self.deleteSelectedShape)

        self.initBarStatus()

    def initBarStatus(self):
        self.toggleDrawMode('polygon')

    def labelSelectionChanged(self):
        if not self._selectSlotBlock:
            if self.view.editing():
                selected_shapes = []
                for item in self.labelListWidget.selectedItems():
                    selected_shapes.append(item.shape())
                if selected_shapes:
                    for canvas in self.view:
                        canvas.selectShapes(selected_shapes)
                else:
                    for canvas in self.view:
                        canvas.deSelectShape()

    def labelItemChanged(self, item):
        shape = item.shape()
        for canvas in self.view:
            canvas.setShapeVisible(shape, item.checkState() == Qt.Checked)

    def remLabels(self, shapes):
        for shape in shapes:
            print(shape)
            item = self.labelListWidget.findItemByShape(shape)
            self.labelListWidget.removeItem(item)
            item = self.allLabelList.findItemByShape(shape)
            self.allLabelList.removeItem(item)

    def editLabel(self, item=None):
        self.toggleDrawMode(None)

        if not item:
            return
        if not isinstance(item, LabelListWidgetItem):
            return
        self.labelSelectionChanged()

    def addLabel(self, shape):

        self.labelListWidget.addShape(shape)
        self.allLabelList.addShape(shape)

        label = shape.label
        r, g, b, a = label.color
        shape.line_color = QtGui.QColor(r, g, b, a)
        shape.vertex_fill_color = QtGui.QColor(r, g, b, a)
        shape.hvertex_fill_color = QtGui.QColor(255, 255, 255)
        shape.fill_color = QtGui.QColor(r, g, b, a*0.5)
        shape.select_line_color = QtGui.QColor(255, 255, 255)
        shape.select_fill_color = QtGui.QColor(r, g, b, a*0.8)

    def newShape(self, canvas, shapes):
        for shape in shapes:
            if shape.label == None:
                curItem = self.colorTableWidget.currentItem()
                label = self.colorTableWidget.getObjectByItem(curItem)
                shape = canvas.lastShape()
                shape.label = label
            print(shape)
            self.addLabel(shape)

    def copyShape(self, shape):
        for canvas in self.view:
            canvas.endMove(copy=True)
        self.labelListWidget.clearSelection()
        for canvas in self.view:
            for shape in canvas.selectedShapes:
                self.addLabel(shape)
        self.setDirty()

    def deleteSelectedShape(self):
        shapes = [s for canvas in self.view for s in canvas.selectedShapes]

        if shapes:
            yes, no = QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No
            msg = self.tr(
                'You are about to permanently delete {} polygons, '
                'proceed anyway?'
            ).format(len(shapes))
            if yes == QtWidgets.QMessageBox.warning(
                    self, self.tr('Attention'), msg,
                    yes | no, yes):

                del_shapes = [
                    s for canvas in self.view for s in canvas.deleteSelected()]
                self.remLabels(del_shapes)
                self.setDirty()
                # if self.noShapes():
                #     for action in self.actions.onShapesPresent:
                #         action.setEnabled(False)

    def shapeSelectionChanged(self, canvas, selected_shapes):
        # self._noSelectionSlot = True
        for shape in canvas.selectedShapes:
            shape.selected = False
        self.labelListWidget.clearSelection()
        canvas.selectedShapes = selected_shapes
        self._selectSlotBlock = True
        for shape in canvas.selectedShapes:
            shape.selected = True
            item = self.labelListWidget.findItemByShape(shape)
            self.labelListWidget.selectItem(item)
            self.labelListWidget.scrollToItem(item)
        # self._noSelectionSlot = False
        self._selectSlotBlock = False
        n_selected = len(selected_shapes)
        self.actions.delete.setEnabled(n_selected)
        # self.actions.copy.setEnabled(n_selected)
        # self.actions.edit.setEnabled(n_selected == 1)

    def toggleDrawMode(self, mode):
        self.view.toggleDrawMode(mode)

        self.actions.create_mode.setEnabled(mode != canvas.Mode_polygon)
        self.actions.createRectangleMode.setEnabled(
            mode != canvas.Mode_rectangle)
        self.actions.createCircleMode.setEnabled(mode != canvas.Mode_circle)
        self.actions.createLineMode.setEnabled(mode != canvas.Mode_line)
        self.actions.createLineStripMode.setEnabled(
            mode != canvas.Mode_linestrip)
        self.actions.createPointMode.setEnabled(mode != canvas.Mode_point)
        self.actions.edit.setEnabled(not self.view.editing())

    def nextFrame(self, canvas, delta):
        curIdx = canvas.curFrameIndex()
        if delta.y() > 0:
            curIdx += 1
        else:
            curIdx -= 1
        canvas.image_wapper.update(curIdx)
        canvas.update()

        slice_types = [(c.sliceType(), c.sliceIndex()) for c in self.view]

        items = [item for item in self.allLabelList if (
            item.shape().slice_type, item.shape().slice_index) in slice_types]
        self.labelListWidget.clear()
        for c in self.view:
            d = [i.shape()
                 for i in items if i.shape().slice_type == c.sliceType()]
            c.loadShapes(d)
            for s in d:
                self.labelListWidget.addShape(s)

    def centerChanged(self, canvas, delta):
        pass
        # units = - delta * 0.1
        # bar_x = self.scrollBars[Qt.Horizontal]
        # bar_y = self.scrollBars[Qt.Vertical]
        # print('bar val:{0} bar step:{1} delta:{2}'.format(
        #     bar_y.value(), bar_y.singleStep(), delta))

        # bar_x.setValue(bar_x.value() + bar_x.singleStep() * units.x())
        # bar_y.setValue(bar_y.value() + bar_y.singleStep() * units.y())

    def zoomChanged(self, scale):
        self.updateCanvas()

    def updateCanvas(self):
        for canvas in self.view:
            canvas.scale = self.zoom_widget.value() * 0.01
            canvas.adjustSize()
            canvas.update()

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
            self._open(fileName)

    def _open(self, fileName):
        self.loader = Loader()
        d = self.loader.loadDicom(fileName)
        self.view.loadImage(d)

    def setDirty(self):
        self.dirty = True

    def resizeEvent(self, event):
        self.updateCanvas()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    win = MainWindow()
    win.show()
    win._open(r"F:\github\labeldicom_cpp\testData\0_resized.nii.gz")

    app.exec()
