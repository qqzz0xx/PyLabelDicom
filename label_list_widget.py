from qtpy import QtCore, QtGui, QtWidgets
from qtpy.QtCore import Qt
from html_delegate import HTMLDelegate


class LabelListWidgetItem(QtGui.QStandardItem):
    def __init__(self, text=None, shape=None):
        super(LabelListWidgetItem, self).__init__()

        if text and shape:
            self.setText(
                '{} <font color="#{:02x}{:02x}{:02x}">●</font>'.format(text, *shape.label.color))
            self.setShape(shape)
        self._desc = text

        self.setCheckable(True)
        self.setCheckState(Qt.Checked)
        self.setEditable(False)
        self.setTextAlignment(Qt.AlignBottom)

    def desc(self):
        return self._desc

    def clone(self):
        return LabelListWidgetItem(self.desc(), self.shape())

    def setShape(self, shape):
        self.setData(shape, Qt.UserRole)

    def shape(self):
        return self.data(Qt.UserRole)

    def __hash__(self):
        return id(self)

    def __repr__(self):
        return '{}("{}")'.format(self.__class__.__name__, self.text())


class LabelListWidget(QtWidgets.QListView):

    itemDoubleClicked = QtCore.Signal(LabelListWidgetItem)
    itemSelectionChanged = QtCore.Signal(list, list)
    itemDropped = QtCore.Signal()
    itemDeleteSelected = QtCore.Signal(list)

    def __init__(self, parent):
        super(LabelListWidget, self).__init__(parent)
        self._selectedItems = []

        self.setWindowFlags(Qt.Window)
        self.setModel(QtGui.QStandardItemModel())
        self.model().setItemPrototype(LabelListWidgetItem())
        self.setItemDelegate(HTMLDelegate())
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.setDefaultDropAction(Qt.MoveAction)

        self.doubleClicked.connect(self.itemDoubleClickedEvent)
        self.selectionModel().selectionChanged.connect(
            self.itemSelectionChangedEvent
        )

    def __len__(self):
        return self.model().rowCount()

    def __getitem__(self, i):
        return self.model().item(i)

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

    def dropEvent(self, event):
        super(LabelListWidget, self).dropEvent(event)
        self.itemDropped.emit()

    @property
    def itemChanged(self):
        return self.model().itemChanged

    def itemSelectionChangedEvent(self, selected, deselected):
        selected = [self.model().itemFromIndex(i) for i in selected.indexes()]
        deselected = [
            self.model().itemFromIndex(i) for i in deselected.indexes()
        ]
        self.itemSelectionChanged.emit(selected, deselected)

    def itemDoubleClickedEvent(self, index):
        self.itemDoubleClicked.emit(self.model().itemFromIndex(index))

    def selectedItems(self):
        return [self.model().itemFromIndex(i) for i in self.selectedIndexes()]

    def scrollToItem(self, item):
        self.scrollTo(self.model().indexFromItem(item))

    def addItem(self, item):
        if not isinstance(item, LabelListWidgetItem):
            raise TypeError("item must be LabelListWidgetItem")
        self.model().setItem(self.model().rowCount(), 0, item)
        item.setSizeHint(self.itemDelegate().sizeHint(None, None))

    def addShape(self, shape):
        label = shape.label
        item = LabelListWidgetItem(label.desc, shape)
        self.addItem(item)
        return item

    def removeItem(self, item):
        index = self.model().indexFromItem(item)
        self.model().removeRows(index.row(), 1)

    def selectItem(self, item):
        index = self.model().indexFromItem(item)
        self.selectionModel().select(index, QtCore.QItemSelectionModel.Select)

    def findItemByShape(self, shape):
        for row in range(self.model().rowCount()):
            item = self.model().item(row, 0)
            if item.shape() == shape:
                return item

    def clear(self):
        self.model().clear()

    def keyPressEvent(self, ev):
        if ev.key() == Qt.Key_Delete:
            items = self.selectedItems()
            self.itemDeleteSelected.emit(items)
