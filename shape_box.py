from shape import Shape
from qtpy import QtGui, QtCore, QtWidgets
from qtpy.QtCore import QPointF
from type import Mode_box
import utils
import numpy as np


class Box3D:
    def __init__(self):
        self.bounds = []
        self.points = []
        self.label = None
        self.shapes = []
        for i in range(3):
            s = ShapeBox(i, 0)
            self.shapes.append(s)

    def zero(self):
        self.bounds = []
        self.points = []

    def addPoint(self, pos):
        if not self.bounds:
            for i in range(3):
                self.bounds.append(pos[i])
                self.bounds.append(pos[i])
            return

        for i in range(3):
            self.bounds[i*2] = min(pos[i], self.bounds[i*2])
            self.bounds[i*2+1] = max(pos[i], self.bounds[i*2+1])

    def containsPoint(self, pos):
        return self.bounds[0] <= pos[0] < self.bounds[1] \
            and self.bounds[2] <= pos[1] < self.bounds[3]\
            and self.bounds[4] <= pos[2] < self.bounds[5]

    def contains(self, slice_type, slice_index):
        return self.bounds[slice_type*2] <= slice_index < self.bounds[slice_type*2+1]

    def computeRect(self):
        points = []
        bds = self.bounds
        p1 = [bds[2], bds[4]]
        p2 = [bds[3], bds[5]]
        points.extend([QPointF(*p1), QPointF(*p2)])
        p1 = [bds[0], bds[4]]
        p2 = [bds[1], bds[5]]
        points.extend([QPointF(*p1), QPointF(*p2)])
        p1 = [bds[0], bds[2]]
        p2 = [bds[1], bds[3]]
        points.extend([QPointF(*p1), QPointF(*p2)])
        self.points = points

    def getRectangle(self, slice_type):
        self.computeRect()
        i = slice_type * 2
        return self.points[i:i+2]

    def getRectShape(self, canvas):
        st = canvas.sliceType()
        si = canvas.sliceIndex()
        if self.contains(st, si):
            s = self.shapes[st]
            s.box = self
            s.shape_type = Mode_box
            s.points = self.getRectangle(st)
            if self.label:
                s.label = self.label
                r, g, b, a = s.label.color
                s.line_color = QtGui.QColor(r, g, b, a)
                s.vertex_fill_color = QtGui.QColor(r, g, b, a)
                s.hvertex_fill_color = QtGui.QColor(255, 255, 255)
                s.fill_color = QtGui.QColor(r, g, b, a*0.5)
                s.select_line_color = QtGui.QColor(255, 255, 255)
                s.select_fill_color = QtGui.QColor(r, g, b, a*0.8)
            return s


class ShapeBox(Shape):
    def updateBox(self):
        win = QtWidgets.QApplication.instance().win
        canvas = win.view[self.slice_type]
        box = self.box
        p1 = utils.sliceToVoxPos(canvas, self[0])
        p1[self.slice_type] = self.box.bounds[self.slice_type*2]
        p2 = utils.sliceToVoxPos(canvas, self[1])
        p2[self.slice_type] = self.box.bounds[self.slice_type*2 + 1]

        box.zero()
        box.addPoint(p1)
        box.addPoint(p2)

        for s in win.view:
            if s != canvas:
                box.getRectShape(s)
                s.update()

    def moveBy(self, offset):
        super(ShapeBox, self).moveBy(offset)
        self.updateBox()

    def moveVertexBy(self, i, offset):
        super(ShapeBox, self).moveVertexBy(i, offset)
        self.updateBox()
