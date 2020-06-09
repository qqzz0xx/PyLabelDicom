from PyQt5 import QtWidgets, Qt
from html_delegate import HTMLDelegate


class TaglistWidget(QtWidgets.QListWidget):
    def __init__(self, parent):
        super(TaglistWidget, self).__init__(parent)
        self.setItemDelegate(HTMLDelegate())

    def createItem(self, id, color, desc):
        item = QtWidgets.QListWidgetItem()
        item.setText('{} {} <font color="#{:02x}{:02x}{:02x}">●</font>'.format(
            desc, id, *color
        ))

        return item

    def addChild(self, parent, id, color, desc, childs=None):
        item = self.createItem(id, color, desc)
        self.addItem(item)

    def loadFromJson(self, js):
        for d in js:
            self.addChild(None, **d)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.clearSelection()
