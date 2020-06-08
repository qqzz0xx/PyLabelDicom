from PyQt5 import QtWidgets, QtGui
import os.path as osp
import math


pwd = osp.dirname(osp.abspath(__file__))


def createIcon(name):
    icons_dir = osp.join(pwd, './icons')
    return QtGui.QIcon(osp.join(':/', icons_dir, '%s.png' % name))


def createAction(parent, name, slot=None, icon=None, tip=None):
    action = QtWidgets.QAction(name, parent)
    if slot:
        action.triggered.connect(slot)
    if icon:
        action.setIconText(name.replace(' ', '\n'))
        action.setIcon(createIcon(icon))
    if tip:
        action.setToolTip(tip)

    return action


def addActions(parent, actions):
    for action in actions:
        if action is None:
            parent.addSeparator()
        elif isinstance(action, QtWidgets.QMenu):
            parent.addMenu(action)
        else:
            parent.addAction(action)


def distance(p):
    return math.sqrt(p.x() * p.x() + p.y() * p.y())


class struct(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
