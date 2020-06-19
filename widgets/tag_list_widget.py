from qtpy import QtWidgets, QtCore
from qtpy.QtCore import Qt
from .html_delegate import HTMLDelegate
from utils import struct, addActions


class TaglistWidget(QtWidgets.QListWidget):
    itemsDelete = QtCore.Signal(list)

    def __init__(self, parent):
        super(TaglistWidget, self).__init__(parent)
        self.menu = QtWidgets.QMenu()
        self.setItemDelegate(HTMLDelegate())

    def addMenu(self, menu):
        addActions(self.menu, menu)

    def createItem(self, id, color, desc):
        item = QtWidgets.QListWidgetItem()
        item.setText('{} {} <font color="#{:02x}{:02x}{:02x}">■</font>'.format(
            desc, id, *color
        ))
        obj = struct(id=id, color=color, desc=desc)
        item.setData(Qt.UserRole, obj)

        return item

    def addChild(self, parent, id, color, desc, childs=None):
        item = self.createItem(id, color, desc)
        self.addItem(item)

    def loadFromJson(self, js):
        self.clear()

        for d in js:
            self.addChild(None, **d)

        self.setCurrentRow(0)

    def getObjectByItem(self, item):
        return item.data(Qt.UserRole)

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
        for item in self.selectedItems():
            shapes.append(self.getObjectByItem(item))
            self.takeItem(self.row(item))

        self.itemsDelete.emit(shapes)

    def mousePressEvent(self, ev):
        super(TaglistWidget, self).mousePressEvent(ev)

        if ev.button() == Qt.RightButton:
            item = self.itemAt(ev.pos())
            if self.menu and item:
                self.menu.exec_(self.mapToGlobal(ev.pos()))

    # def keyPressEvent(self, event):
    #     if event.key() == Qt.Key_Delete:
    #         self.clearSelection()
