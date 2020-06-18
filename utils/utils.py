from qtpy import QtWidgets, QtGui
import os.path as osp
import math
import numpy as np
import json

pwd = osp.dirname(osp.abspath(__file__))


def createIcon(name):
    icons_dir = osp.join(pwd, '../icons')
    return QtGui.QIcon(osp.join(':/', icons_dir, '%s.png' % name))


def createAction(parent, name, slot=None, icon=None, tip=None, enabled=True):
    action = QtWidgets.QAction(name, parent)
    action.setEnabled(enabled)

    if slot:
        action.triggered.connect(slot)
    if icon:
        action.setIconText(name.replace(' ', '\n'))
        action.setIcon(createIcon(icon))
    if tip:
        action.setToolTip(tip)
        action.setStatusTip(tip)

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


def distancetoline(point, line):
    p1, p2 = line
    p1 = np.array([p1.x(), p1.y()])
    p2 = np.array([p2.x(), p2.y()])
    p3 = np.array([point.x(), point.y()])
    if np.dot((p3 - p1), (p2 - p1)) < 0:
        return np.linalg.norm(p3 - p1)
    if np.dot((p3 - p2), (p1 - p2)) < 0:
        return np.linalg.norm(p3 - p2)
    return np.linalg.norm(np.cross(p2 - p1, p1 - p3)) / np.linalg.norm(p2 - p1)


def jsonToQColor(j):
    return QtGui.QColor(*j)


def qcolorToJson(color):
    return color.getRgb()


class struct(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
