from qtpy import QtWidgets, QtCore, QtGui
from qtpy.QtCore import Qt
from .html_delegate import HTMLDelegate
from .tag_edit_dialog import TagEditDialog
from utils import struct, addActions


class TaglistWidget(QtWidgets.QTreeView):
    itemsDelete = QtCore.Signal(list)

    def __init__(self, parent):
        super(TaglistWidget, self).__init__(parent)
        self.menu = QtWidgets.QMenu()
        self.setModel(QtGui.QStandardItemModel())
        self.setItemDelegate(HTMLDelegate())
        self.header().hide()
        self.setEditTriggers(QtWidgets.QTreeView.NoEditTriggers)

    def __len__(self):
        return self.model().rowCount()

    def __getitem__(self, i):
        return self.model().item(i)

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

    def addMenu(self, menu):
        addActions(self.menu, menu)

    def createItem(self, id, color, desc):
        item = QtGui.QStandardItem()
        item.setText('<font color="#{:02x}{:02x}{:02x}">■</font>{} {}'.format(
            *color[0:3], desc, id,
        ))
        obj = struct(id=id, color=color, desc=desc)
        item.setData(obj, Qt.UserRole)

        return item

    def addChild(self, parent, id, color, desc, childs=None):
        item = self.createItem(id, color, desc)
        if parent:
            parent.appendRow(item)
        else:
            self.addItem(item)
        if childs:
            for c in childs:
                self.addChild(item, **c)

    def insertItem(self, parent, item, pos):
        if parent:
            parent.insertRow(pos, item)
        else:
            self.model().insertRow(pos, item)

    def loadFromJson(self, js):
        self.clear()

        for d in js:
            self.addChild(None, **d)

        self.setCurrentRow(0)

    def getObjectByItem(self, item):
        return item.data(Qt.UserRole)

    def count(self):
        return len(self)

    def currentItem(self):
        return self.model().itemFromIndex(self.currentIndex())

    def currentRow(self):
        return self.currentIndex().row()

    def selectedItems(self):
        return [i for i in self.selectedIndexes()]

    def selectItem(self, item):
        index = self.model().indexFromItem(item)
        self.selectionModel().select(index, QtCore.QItemSelectionModel.Select)
        self.setCurrentIndex(index)

    def setCurrentRow(self, row):
        item = self.model().item(row, 0)
        self.selectItem(item)

    def selectHome(self):
        self.setCurrentRow(0)

    def selectEnd(self):
        self.setCurrentRow(self.count() - 1)

    def selectNext(self):
        row = self.currentRow() + 1
        if row < self.count() and row > -1:
            self.setCurrentRow(row)

    def selectPrev(self):
        row = self.currentRow() - 1
        if row < self.count() and row > -1:
            self.setCurrentRow(row)

    def deleteSelected(self):
        shapes = []
        for index in self.selectedItems():
            item = self.model().itemFromIndex(index)
            shapes.append(self.getObjectByItem(item))
            self.model().removeRow(index.row(), index.parent())

        self.itemsDelete.emit(shapes)

    def clear(self):
        self.model().clear()

    def addItem(self, item):
        self.model().setItem(self.model().rowCount(), 0, item)
        item.setSizeHint(self.itemDelegate().sizeHint(None, None))

    def insertTag_(self, func):
        dlg = TagEditDialog(self)
        pos = QtGui.QCursor.pos()
        pos = self.mapFromGlobal(pos)
        pos = self.mapToGlobal(QtCore.QPoint(0, pos.y()-150))
        dlg.move(pos)
        ok = dlg.exec()
        if ok:
            obj = dlg.getTagObj()
            new_item = self.createItem(obj.id, obj.color, obj.desc)
            cur_item = self.currentItem()
            if func:
                func(cur_item, new_item)

    def addTag(self):
        self.insertTag_(lambda cur_item, new_item: self.insertItem(
            cur_item.parent(), new_item, cur_item.row()+1))

    def insertTag(self):
        self.insertTag_(lambda cur_item, new_item: self.insertItem(cur_item, new_item, 0))

    def mousePressEvent(self, ev):
        super(TaglistWidget, self).mousePressEvent(ev)

        if ev.button() == Qt.RightButton:
            index = self.indexAt(ev.pos())
            if self.menu and index.isValid():
                self.menu.exec_(self.mapToGlobal(ev.pos()))

    # def keyPressEvent(self, event):
    #     if event.key() == Qt.Key_Delete:
    #         self.clearSelection()
