from qtpy import QtWidgets
from qtpy.QtCore import Qt
from .html_delegate import HTMLDelegate
from utils import struct


class TaglistWidget(QtWidgets.QListWidget):
    tagObjects = []

    def __init__(self, parent):
        super(TaglistWidget, self).__init__(parent)
        self.setItemDelegate(HTMLDelegate())

    def createItem(self, id, color, desc):
        item = QtWidgets.QListWidgetItem()
        item.setText('{} {} <font color="#{:02x}{:02x}{:02x}">■</font>'.format(
            desc, id, *color
        ))

        return item

    def addChild(self, parent, id, color, desc, childs=None):
        item = self.createItem(id, color, desc)
        obj = (item,  struct(id=id, color=color, desc=desc))
        self.tagObjects.append(obj)
        self.addItem(item)

    def loadFromJson(self, js):
        for d in js:
            self.addChild(None, **d)

        self.setCurrentRow(0)

    def getObjectByItem(self, item):
        for i, obj in self.tagObjects:
            if item == i:
                return obj
        return None

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.clearSelection()
