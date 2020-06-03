from PyQt5 import QtWidgets


def creatAction(parent, name, slot=None, icon=None):
    action = QtWidgets.QAction(name, parent)
    if slot:
        action.triggered.connect(slot)
    if icon:
        action.setIcon(icon)

    return action


def addActions(parent: QtWidgets.QMenu, actions):
    for action in actions:
        if action is None:
            parent.addSeparator()
        elif isinstance(action, QtWidgets.QMenu):
            parent.addMenu(action)
        else:
            parent.addAction(action)


class struct(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
