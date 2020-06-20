from qtpy import QtWidgets


class TagEditDialog(QtWidgets.QDialog):
    def __init__(self, parent, *args, **kwargs):
        super(TagEditDialog, self).__init__(parent)
        layout = QtWidgets.QHBoxLayout()
        self.line_edit = QtWidgets.QLineEdit('Label', self)
        self.color_edit = QtWidgets.QLabel('Color')
        layout.addWidget(self.line_edit)
        layout.addWidget(self.color_edit)
        self.setLayout(layout)

    def getTagItem(self):
        obj = struct(id=0, color=[2, 3, 4, 5], desc='Label')
        item = QtWidgets.QListWidgetItem()
        item.setText('{} {} <font color="#{:02x}{:02x}{:02x}">■</font>'.format(
            desc, id, *color
        ))
        item.setData(Qt.UserRole, obj)
        return item
