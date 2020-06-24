from qtpy import QtWidgets, QtGui, QtCore
from utils import createIconByColor


class ColorButton(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(ColorButton, self).__init__(parent)
        self._button = QtWidgets.QToolButton(self)
        self._button.setText('Choose')
        self._button.setIcon(createIconByColor(QtGui.QColor(255, 0, 0)))
        self._button.setIconSize(QtCore.QSize(16, 16))
        self._button.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)

        self._lv = QtWidgets.QHBoxLayout()
        self._lv.setContentsMargins(0, 0, 0, 0)
        self._lv.addWidget(self._button)
        self.setLayout(self._lv)
        self._color = QtGui.QColor(255, 0, 0)

        self._button.clicked.connect(self.onChooseColor)

    def setColor(self, color):
        self._color = color
        self._button.setIcon(createIconByColor(color))

    def getColor(self):
        return self._color

    def onChooseColor(self):
        color = QtWidgets.QColorDialog.getColor()
        if color:
            self.setColor(color)
