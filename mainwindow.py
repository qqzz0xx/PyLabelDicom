from qtpy import QtWidgets, QtGui, QtCore
from qtpy.QtCore import Qt

import sys
import functools
import json
import os.path as osp

import utils
import config
from view import canvas
from view import Canvas, BaseView, DicomView, ImageView, VideoView
from utils import Loader, Saver, ImageDataWapper
from widgets import ZoomWidget, ToolBar, TaglistWidget
from widgets import LabelListWidgetItem, LabelListWidget
from shape import Shape
import type


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setAcceptDrops(True)

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

        self.addDockWidget(Qt.RightDockWidgetArea, self.allLabelListDock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.colorTableDock)
        self.tabifyDockWidget(self.allLabelListDock, self.labelListDock)

        self.view = BaseView()
        self.setCentralWidget(self.view)
        self.statusBar().show()
        self.resize(1200, 800)

        action = functools.partial(utils.createAction, self)
        open_ = action("&Open", self.open, 'open',
                       self.tr('Open image or label file'))
        exit_ = action("&Exit", tip=self.tr('Quit Application'))
        openDir_ = action("&Open Dir", self.open, 'open')
        createMode_ = action(
            "&Create Polygons",
            lambda: self.toggleDrawMode(type.Mode_polygon),
            'objects',
            self.tr('Start drawing polygons'))

        createRectangleMode_ = action(
            self.tr('Create Rectangle'),
            lambda: self.toggleDrawMode(type.Mode_rectangle),
            'objects',
            self.tr('Start drawing rectangles'),
            enabled=False,
        )
        createCircleMode_ = action(
            self.tr('Create Circle'),
            lambda: self.toggleDrawMode(type.Mode_circle),
            'objects',
            self.tr('Start drawing circles'),
            enabled=False,
        )
        createLineMode_ = action(
            self.tr('Create Line'),
            lambda: self.toggleDrawMode(type.Mode_line),
            'objects',
            self.tr('Start drawing lines'),
            enabled=False,
        )
        createPointMode_ = action(
            self.tr('Create Point'),
            lambda: self.toggleDrawMode(type.Mode_point),
            'objects',
            self.tr('Start drawing points'),
            enabled=False,
        )
        createLineStripMode_ = action(
            self.tr('Create LineStrip'),
            lambda: self.toggleDrawMode(type.Mode_linestrip),
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

        save_ = action(self.tr('&Save'),
                       self.saveFile, 'save',
                       self.tr('Save labels to file'), enabled=False)

        saveAs_ = action(self.tr('&Save As'),
                         self.saveFileAs,
                         'save-as', self.tr('Save labels to a different file'),
                         enabled=False)

        nextTag_ = action(self.tr('&Next Tag'),
                          slot=lambda: self.colorTableWidget.selectNext(),
                          tip=self.tr('Go to a next tag'),
                          )
        prevTag_ = action(self.tr('&Previous Tag'),
                          slot=lambda: self.colorTableWidget.selectPrev(),
                          tip=self.tr('Go to a previous tag'),
                          )
        homeTag_ = action(self.tr('&Home Tag'),
                          slot=lambda: self.colorTableWidget.selectHome(),
                          tip=self.tr('Go to a start tag'),
                          )
        endTag_ = action(self.tr('&End Tag'),
                         slot=lambda: self.colorTableWidget.selectEnd(),
                         tip=self.tr('Go to a end tag'),
                         )
        deleteTag_ = action(self.tr('&Delete Tag'),
                            slot=lambda: self.colorTableWidget.deleteSelected(),
                            )
        fitWindow_ = action(self.tr('&Fit Window'),
                            slot=self.fitWindow,
                            icon='fit-window',
                            tip=self.tr('Zoom follows window size'))

        self.zoom_widget = ZoomWidget()
        zoom_ = QtWidgets.QWidgetAction(self)
        zoom_.setDefaultWidget(self.zoom_widget)

        self.actions = utils.struct(
            open=open_,
            exit=exit_,
            openDir=openDir_,
            createMode=createMode_,
            createRectangleMode=createRectangleMode_,
            createCircleMode=createCircleMode_,
            createLineMode=createLineMode_,
            createPointMode=createPointMode_,
            createLineStripMode=createLineStripMode_,
            edit=edit_,
            delete=delete_,
            save=save_,
            saveAs=saveAs_,
            nextTag=nextTag_,
            prevTag=prevTag_,
            homeTag=homeTag_,
            endTag=endTag_,
            deleteTag=deleteTag_,
            fitWindow=fitWindow_,
            # load=load_,

            fileMenu=(
                open_,
                openDir_,
                None,
                save_,
                saveAs_,
                None,
                # load_,
                None,
                exit_,
            ),
            editMenu=(
                createMode_,
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
            selectionMenu=(
                nextTag_,
                prevTag_,
                homeTag_,
                endTag_,
            ),
            viewMenu=(
                self.labelListDock.toggleViewAction(),
                self.allLabelListDock.toggleViewAction(),
                self.colorTableDock.toggleViewAction(),
                None,
                fitWindow_,
            ),
            labelListMenu=(
                delete_,
            ),
            tagListMenu=(
                deleteTag_,
            )
        )

        self.tools_actions = (
            open_,
            openDir_,
            save_,
            saveAs_,
            None,
            createMode_,
            edit_,
            None,
            zoom_,
            fitWindow_,

        )
        self.toolbar = ToolBar('toolbar')
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.addToolBar(Qt.TopToolBarArea, self.toolbar)
        utils.addActions(self.toolbar, self.tools_actions)
        # utils.addActions(self.canvas.menu, self.actions.editMenu)
        self.view.addMenu(self.actions.editMenu)
        self.labelListWidget.addMenu(self.actions.labelListMenu)
        self.colorTableWidget.addMenu(self.actions.tagListMenu)

        self.addMenu("&File", self.actions.fileMenu)
        self.addMenu("&Edit", self.actions.editMenu)
        self.addMenu("&Selection", self.actions.selectionMenu)
        self.addMenu("&View", self.actions.viewMenu)
        # signal

        self.zoom_widget.valueChanged.connect(self.zoomChanged)
        self.labelListWidget.itemChanged.connect(self.labelItemChanged)
        self.labelListWidget.itemDoubleClicked.connect(self.editLabel)
        self.labelListWidget.itemSelectionChanged.connect(
            self.labelSelectionChanged)
        self.labelListWidget.itemDeleteSelected.connect(
            self.deleteSelectedShape)
        self.colorTableWidget.itemsDelete.connect(self.tagsDelete)

        self.init()
        self.initViewSlot()

    def init(self):
        self.toggleDrawMode(type.Mode_polygon)

        keymaps = self._config['keymap']
        for km in keymaps:
            key = km['key']
            action = km['action']
            if hasattr(self.actions, action):
                key = key.replace(' ', '')
                action = self.actions.__dict__[action]
                if isinstance(key, (list, tuple)):
                    action.setShortcuts(key)
                else:
                    action.setShortcut(key)

    def initViewSlot(self):
        self.view.zoomChanged.connect(
            lambda canvas, v: self.zoom_widget.setValue(v*100))
        self.view.centerChanged.connect(
            lambda canvas, v: self.centerChanged(canvas, v))
        self.view.frameChanged.connect(
            lambda canvas, v: self.frameChanged(canvas, v))
        self.view.selectionChanged.connect(
            lambda canvas, v: self.shapeSelectionChanged(canvas, v))
        self.view.newShape.connect(
            lambda canvas, v: self.newShape(canvas, v))
        self.view.onMousePress.connect(
            lambda canvas, v: self.status(
                "world pos: [{0},{1}]".format(v.x(), v.y()))
        )

    def fitWindow(self):
        scale = [self.scaleFitWindow(s) for s in self.view]
        scale = scale[0] if len(scale) == 1 else min(*scale)
        print('fitWindow ', scale)
        self.zoom_widget.setValue(scale*100)

    def scaleFitWindow(self, canvas):
        """Figure out the size of the pixmap to fit the main widget."""
        e = 2.0  # So that no scrollbars are generated.
        w1 = canvas.parent().width() - e
        h1 = canvas.parent().height() - e
        a1 = w1 / h1
        # Calculate a new scale value based on the pixmap's aspect ratio.
        w2 = canvas.pixmap().width() - 0.0
        h2 = canvas.pixmap().height() - 0.0
        a2 = w2 / h2
        return w1 / w2 if a2 >= a1 else h1 / h2

    def loadJson(self, file):
        if file:
            with open(file, encoding='UTF-8') as f:
                j = json.load(f, strict=False)
            if str.endswith(file, 'tags.json'):
                self.colorTableWidget.loadFromJson(j)
                self._config['tags'] = j
            else:
                shapes = []
                for d in j['shapes']:
                    s = Shape(None, None)
                    s.__dict__.update(d)
                    s.label = utils.struct(**s.label)
                    s.points = [QtCore.QPointF(x, y) for x, y in s.points]
                    shapes.append(s)
                [self.addLabel(s) for s in shapes]
            self._json_file = file

    def tagsDelete(self, tags):
        tag_ids = [tag.id for tag in tags]
        del_shapes = [
            shape for canvas in self.view for shape in canvas.shapes if shape.label.id in tag_ids]
        for canvas in self.view:
            canvas.selectShapes(del_shapes)

        if del_shapes:
            yes, no = QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No
            msg = self.tr(
                'You are about to permanently delete {} polygons, '
                'proceed anyway?'
            ).format(len(del_shapes))
            if yes == QtWidgets.QMessageBox.warning(
                    self, self.tr('Attention'), msg,
                    yes | no, yes):
                [canvas.deleteSelected() for canvas in self.view]
                self.remLabels(del_shapes)
                self.setDirty()

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
        if not shapes:
            return

        for shape in shapes:
            if shape.label == None:
                curItem = self.colorTableWidget.currentItem()
                label = self.colorTableWidget.getObjectByItem(curItem)
                shape = canvas.lastShape()
                shape.label = label
            print("new shape: ", shape)
            self.addLabel(shape)
        self.setDirty()

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

        self.actions.createMode.setEnabled(mode != canvas.Mode_polygon)
        self.actions.createRectangleMode.setEnabled(
            mode != canvas.Mode_rectangle)
        self.actions.createCircleMode.setEnabled(mode != canvas.Mode_circle)
        self.actions.createLineMode.setEnabled(mode != canvas.Mode_line)
        self.actions.createLineStripMode.setEnabled(
            mode != canvas.Mode_linestrip)
        self.actions.createPointMode.setEnabled(mode != canvas.Mode_point)
        self.actions.edit.setEnabled(not self.view.editing())

    def frameChanged(self, canvas, val):
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

    def status(self, tips, dt=3000):
        self.statusBar().showMessage(tips, 3000)

    def open(self, fileName=None):
        if not self.mayContinue():
            return

        dir = None
        if not fileName:
            if self.loader:
                dir = self.loader.image_dir
            formats = "ALL(*);;" + ";;".join(type.SUPPORT_FORMAT)
            fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self,
                                                                "Open File", dir, formats)
        print("open: ", fileName)
        if not osp.exists(fileName):
            return

        if fileName and fileName != '':
            if osp.splitext(fileName)[-1] == '.json':
                self.loadJson(fileName)
            else:
                self._open(fileName)

        self.status(self.tr('{} open success!'.format(fileName)))

    def _open(self, fileName):
        self.clearLabels()
        self.view.clear()
        loader = Loader()
        d = loader.loadDicom(fileName)
        if loader.isImage():
            self.view = ImageView()
        elif loader.isVolume():
            self.view = DicomView()
        elif loader.isVideo():
            self.view = VideoView()

        self.initViewSlot()
        self.setCentralWidget(self.view)
        self.view.addMenu(self.actions.editMenu)

        self.view.loadImage(d)
        self.zoom_widget.setValue(100)
        self.actions.saveAs.setEnabled(False)
        self.loader = loader

    def mayContinue(self):
        if not self.dirty:
            return True
        mb = QtWidgets.QMessageBox
        msg = self.tr('Save annotations to "{}" before closing?').format(
            self.loader.image_path)
        answer = mb.question(self,
                             self.tr('Save annotations?'),
                             msg,
                             mb.Save | mb.Discard | mb.Cancel,
                             mb.Save)
        if answer == mb.Discard:
            return True
        elif answer == mb.Save:
            self.saveLabels(self.loader.image_dir)
            return True
        else:  # answer == mb.Cancel
            return False

    def getDirDialog(self):
        dir = None
        if hasattr(self, 'output_dir') and self.output_dir:
            dir = self.output_dir

        dir_name = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Find Directory ..", dir)
        return dir_name

    def saveFile(self):
        if hasattr(self, 'saver') and self.saver:
            self.saveLabels(self.saver.saveDirName)
        else:
            self.saveLabels(self.getDirDialog())

    def saveFileAs(self):
        self.saveLabels(self.getDirDialog())

    def saveLabels(self, dirname):
        if not dirname:
            return
        saver = Saver()
        shapes = [item.shape() for item in self.allLabelList]
        saver.saveLabels(dirname, shapes, self.loader.image_path)

        self.saver = saver
        self.setClean()

    def setDirty(self):
        print("setDirty")
        self.dirty = True
        self.actions.save.setEnabled(True)
        self.actions.saveAs.setEnabled(True)

    def setClean(self):
        self.dirty = False
        self.actions.save.setEnabled(False)
        self.actions.createMode.setEnabled(True)
        self.actions.createRectangleMode.setEnabled(True)
        self.actions.createCircleMode.setEnabled(True)
        self.actions.createLineMode.setEnabled(True)
        self.actions.createPointMode.setEnabled(True)
        self.actions.createLineStripMode.setEnabled(True)

    def clearLabels(self):
        self.allLabelList.clear()
        self.labelListWidget.clear()
        self.setClean()

    def resizeEvent(self, event):
        self.updateCanvas()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Space:
            if self.view:
                self.view[-1].newTagLabel()

    def dragEnterEvent(self, ev):
        if ev.mimeData().hasUrls():
            ev.setDropAction(Qt.LinkAction)
            ev.accept()

    def dropEvent(self, ev):
        urls = ev.mimeData().urls()
        for url in urls:
            file = url.toLocalFile()
            self.open(file)

        if len(urls) == 1:
            file = urls[0].toLocalFile()
            if not str.endswith(file, '.json'):
                file = osp.splitext(file)[0] + '.json'
                try:
                    self.open(file)
                except:
                    self.status(self.tr('Load json failed!'))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    win = MainWindow()
    win.show()
    win._open(r"F:\github\labeldicom_cpp\testData\0_resized.nii.gz")

    app.exec()
