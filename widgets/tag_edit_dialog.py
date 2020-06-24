from qtpy import QtWidgets, QtCore
import sys
import utils
from .color_button import ColorButton


class TagEditDialog(QtWidgets.QDialog):
    def __init__(self, parent, *args, **kwargs):
        super(TagEditDialog, self).__init__(parent)
        layout = QtWidgets.QVBoxLayout()
        layout_edit = QtWidgets.QHBoxLayout()
        layout.addLayout(layout_edit)
        self.line_edit = QtWidgets.QLineEdit('Label', self)
        self.color_edit = ColorButton(self)
        layout_edit.addWidget(self.line_edit)
        layout_edit.addWidget(self.color_edit)
        self.setLayout(layout)

        self.buttonBox = bb = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal,
            self,
        )
        layout.addWidget(bb)

        bb.accepted.connect(self.validate)
        bb.rejected.connect(self.reject)

    def validate(self):
        text = self.line_edit.text()
        if text:
            self.accept()

    def getTagObj(self, id=0):
        obj = utils.struct(id=id, color=self.color_edit.getColor().getRgb(), desc=self.line_edit.text())
        return obj
