from PyQt5 import QtWidgets, Qt, QtCore

class ToolBar(QtWidgets.QToolBar):
    def __init__(self, title):
        super().__init__(title)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.FramelessWindowHint)

    def addAction(self, action):
        if isinstance(action, QtWidgets.QWidgetAction):
            return  super(ToolBar, self).addAction(action)
        btn = ToolButton()
        btn.setDefaultAction(action)
        btn.setToolButtonStyle(self.toolButtonStyle())
        self.addWidget(btn)


class ToolButton(QtWidgets.QToolButton):
    minSize =  (60,60)
    def minimumSizeHint(self):
        ms = super(ToolButton, self).minimumSizeHint()
        w1, h1 = ms.width(), ms.height()
        w2, h2 = self.minSize
        self.minSize = max(w1, w2), max(h1, h2)
        return QtCore.QSize(*self.minSize)
