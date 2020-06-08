from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPainterPath, QPainter
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtWidgets, QtCore, QtGui

import utils
from shape import Shape

CURSOR_DEFAULT = QtCore.Qt.ArrowCursor
CURSOR_POINT = QtCore.Qt.PointingHandCursor
CURSOR_DRAW = QtCore.Qt.CrossCursor
CURSOR_MOVE = QtCore.Qt.ClosedHandCursor

CREATE, EDIT = 0, 1

# clCURSOR_GRAB = QtCore.Qt.OpenHandCursorass


class Canvas(QtWidgets.QWidget):
    centerChanged = QtCore.pyqtSignal(QtCore.QPointF)
    zoomChanged = QtCore.pyqtSignal(float)
    drawingPolygon = QtCore.pyqtSignal(bool)
    newShape = QtCore.pyqtSignal()
    image_wapper = None
    scale = 1.0

    mode = CREATE
    _createMode = 'polygon'
    _fill_drawing = False

    def __init__(self, parent):
        super(Canvas, self).__init__(parent)

        self.epsilon = 10.0
        self.main_win = parent
        self._curCursor = CURSOR_DEFAULT
        self.shapes = []
        self.shapesBackups = []
        self.visible = {}
        self.current = None
        self.selectedShapesCopy = None
        self.hShape = None
        self.hVertex = None
        self.hEdge = None
        self._hideBackround = False
        self.hideBackround = False

        self._Painter = QtGui.QPainter()
        self.lineColor = QtGui.QColor(0, 0, 255)
        self.line = Shape(line_color=self.lineColor)

        self.setMouseTracking(True)
        self.setFocusPolicy(QtCore.Qt.WheelFocus)

    def setMode(self, mode):
        Canvas.mode = mode

    def setCreateMode(self, value):
        if value not in ['polygon', 'rectangle', 'circle',
                         'line', 'point', 'linestrip']:
            raise ValueError('Unsupported createMode: %s' % value)
        Canvas._createMode = value

    def drawing(self):
        return Canvas.mode == CREATE

    def editing(self):
        return Canvas.mode == EDIT

    def fillDrawing(self):
        return self._fill_drawing

    def setFillDrawing(self, value):
        self._fill_drawing = value

    def wheelEvent(self, ev: QtGui.QWheelEvent):
        if not self.pixmap():
            return
        mods = ev.modifiers()
        delta = ev.angleDelta()
        if int(mods) != QtCore.Qt.ControlModifier:
            scale = self.scale
            if delta.y() > 0:
                scale *= 1.1
            else:
                scale *= 0.9

            self.zoomChanged.emit(scale)
        else:
            self.centerChanged.emit(delta)

    def mouseMoveEvent(self, ev):
        """Update line with last point and current coordinates."""

        pos = self.transformPos(ev.localPos())

        self.prevMovePoint = pos
        self.restoreCursor()

        # Polygon drawing.
        if self.drawing():
            self.line.shape_type = self._createMode

            self.overrideCursor(CURSOR_DRAW)
            if not self.current:
                return

            color = self.lineColor
            if self.outOfPixmap(pos):
                # Don't allow the user to draw outside the pixmap.
                # Project the point to the pixmap's edges.
                pos = self.intersectionPoint(self.current[-1], pos)
            elif len(self.current) > 1 and self._createMode == 'polygon' and\
                    self.closeEnough(pos, self.current[0]):
                # Attract line to starting point and
                # colorise to alert the user.
                pos = self.current[0]
                color = self.current.line_color
                self.overrideCursor(CURSOR_POINT)
                self.current.highlightVertex(0, Shape.NEAR_VERTEX)
            if self._createMode in ['polygon', 'linestrip']:
                self.line[0] = self.current[-1]
                self.line[1] = pos
            elif self._createMode == 'rectangle':
                self.line.points = [self.current[0], pos]
                self.line.close()
            elif self._createMode == 'circle':
                self.line.points = [self.current[0], pos]
                self.line.shape_type = "circle"
            elif self._createMode == 'line':
                self.line.points = [self.current[0], pos]
                self.line.close()
            elif self._createMode == 'point':
                self.line.points = [self.current[0]]
                self.line.close()
            self.line.line_color = color
            self.repaint()
            self.current.highlightClear()
            return

        # Polygon copy moving.
        if QtCore.Qt.RightButton & ev.buttons():
            if self.selectedShapesCopy and self.prevPoint:
                self.overrideCursor(CURSOR_MOVE)
                self.boundedMoveShapes(self.selectedShapesCopy, pos)
                self.repaint()
            elif self.selectedShapes:
                self.selectedShapesCopy = \
                    [s.copy() for s in self.selectedShapes]
                self.repaint()
            return

        # Polygon/Vertex moving.
        self.movingShape = False
        if QtCore.Qt.LeftButton & ev.buttons():
            if self.selectedVertex():
                self.boundedMoveVertex(pos)
                self.repaint()
                self.movingShape = True
            elif self.selectedShapes and self.prevPoint:
                self.overrideCursor(CURSOR_MOVE)
                self.boundedMoveShapes(self.selectedShapes, pos)
                self.repaint()
                self.movingShape = True
            return

        # Just hovering over the canvas, 2 posibilities:
        # - Highlight shapes
        # - Highlight vertex
        # Update shape/vertex fill and tooltip value accordingly.
        self.setToolTip("Image")
        for shape in reversed([s for s in self.shapes if self.isVisible(s)]):
            # Look for a nearby vertex to highlight. If that fails,
            # check if we happen to be inside a shape.
            index = shape.nearestVertex(pos, self.epsilon / self.scale)
            index_edge = shape.nearestEdge(pos, self.epsilon / self.scale)
            if index is not None:
                if self.selectedVertex():
                    self.hShape.highlightClear()
                self.hVertex = index
                self.hShape = shape
                self.hEdge = index_edge
                shape.highlightVertex(index, shape.MOVE_VERTEX)
                self.overrideCursor(CURSOR_POINT)
                self.setToolTip("Click & drag to move point")
                self.setStatusTip(self.toolTip())
                self.update()
                break
            elif shape.containsPoint(pos):
                if self.selectedVertex():
                    self.hShape.highlightClear()
                self.hVertex = None
                self.hShape = shape
                self.hEdge = index_edge
                self.setToolTip(
                    "Click & drag to move shape '%s'" % shape.label)
                self.setStatusTip(self.toolTip())
                self.overrideCursor(CURSOR_GRAB)
                self.update()
                break
        else:  # Nothing found, clear highlights, reset state.
            if self.hShape:
                self.hShape.highlightClear()
                self.update()
            self.hVertex, self.hShape, self.hEdge = None, None, None
        self.edgeSelected.emit(self.hEdge is not None)

    def mousePressEvent(self, ev):
        if not self.pixmap():
            return
        pos = self.transformPos(ev.localPos())
        self._curPos = pos
        self.main_win.showStatusTips(
            "world pos: [{0},{1}]".format(pos.x(), pos.y()))

        if ev.button() == QtCore.Qt.LeftButton:
            if self.drawing():
                if self.current:
                    # Add point to existing shape.
                    if self._createMode == 'polygon':
                        self.current.addPoint(self.line[1])
                        self.line[0] = self.current[-1]
                        if self.current.isClosed():
                            self.finalise()
                    elif self._createMode in ['rectangle', 'circle', 'line']:
                        assert len(self.current.points) == 1
                        self.current.points = self.line.points
                        self.finalise()
                    elif self._createMode == 'linestrip':
                        self.current.addPoint(self.line[1])
                        self.line[0] = self.current[-1]
                        if int(ev.modifiers()) == QtCore.Qt.ControlModifier:
                            self.finalise()
                elif not self.outOfPixmap(pos):
                    # Create new shape.
                    self.current = Shape(shape_type=self._createMode)
                    self.current.addPoint(pos)
                    if self._createMode == 'point':
                        self.finalise()
                    else:
                        if self._createMode == 'circle':
                            self.current.shape_type = 'circle'
                        self.line.points = [pos, pos]
                        self.setHiding()
                        self.drawingPolygon.emit(True)
                        self.update()
            else:
                group_mode = (int(ev.modifiers()) == QtCore.Qt.ControlModifier)
                self.selectShapePoint(pos, multiple_selection_mode=group_mode)
                self.prevPoint = pos
                self.repaint()
        elif ev.button() == QtCore.Qt.RightButton and self.editing():
            group_mode = (int(ev.modifiers()) == QtCore.Qt.ControlModifier)
            self.selectShapePoint(pos, multiple_selection_mode=group_mode)
            self.prevPoint = pos
            self.repaint()

    def intersectionPoint(self, p1, p2):
        # Cycle through each image edge in clockwise fashion,
        # and find the one intersecting the current line segment.
        # http://paulbourke.net/geometry/lineline2d/
        size = self.pixmap().size()
        points = [(0, 0),
                  (size.width() - 1, 0),
                  (size.width() - 1, size.height() - 1),
                  (0, size.height() - 1)]
        # x1, y1 should be in the pixmap, x2, y2 should be out of the pixmap
        x1 = min(max(p1.x(), 0), size.width() - 1)
        y1 = min(max(p1.y(), 0), size.height() - 1)
        x2, y2 = p2.x(), p2.y()
        d, i, (x, y) = min(self.intersectingEdges((x1, y1), (x2, y2), points))
        x3, y3 = points[i]
        x4, y4 = points[(i + 1) % 4]
        if (x, y) == (x1, y1):
            # Handle cases where previous point is on one of the edges.
            if x3 == x4:
                return QtCore.QPoint(x3, min(max(0, y2), max(y3, y4)))
            else:  # y3 == y4
                return QtCore.QPoint(min(max(0, x2), max(x3, x4)), y3)
        return QtCore.QPoint(x, y)

    def intersectingEdges(self, point1, point2, points):
        """Find intersecting edges.

        For each edge formed by `points', yield the intersection
        with the line segment `(x1,y1) - (x2,y2)`, if it exists.
        Also return the distance of `(x2,y2)' to the middle of the
        edge along with its index, so that the one closest can be chosen.
        """
        (x1, y1) = point1
        (x2, y2) = point2
        for i in range(4):
            x3, y3 = points[i]
            x4, y4 = points[(i + 1) % 4]
            denom = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)
            nua = (x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)
            nub = (x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)
            if denom == 0:
                # This covers two cases:
                #   nua == nub == 0: Coincident
                #   otherwise: Parallel
                continue
            ua, ub = nua / denom, nub / denom
            if 0 <= ua <= 1 and 0 <= ub <= 1:
                x = x1 + ua * (x2 - x1)
                y = y1 + ua * (y2 - y1)
                m = QtCore.QPoint((x3 + x4) / 2, (y3 + y4) / 2)
                d = utils.distance(m - QtCore.QPoint(x2, y2))
                yield d, i, (x, y)

    def boundedMoveShapes(self, shapes, pos):
        if self.outOfPixmap(pos):
            return False  # No need to move
        o1 = pos + self.offsets[0]
        if self.outOfPixmap(o1):
            pos -= QtCore.QPoint(min(0, o1.x()), min(0, o1.y()))
        o2 = pos + self.offsets[1]
        if self.outOfPixmap(o2):
            pos += QtCore.QPoint(min(0, self.pixmap.width() - o2.x()),
                                 min(0, self.pixmap.height() - o2.y()))
        # XXX: The next line tracks the new position of the cursor
        # relative to the shape, but also results in making it
        # a bit "shaky" when nearing the border and allows it to
        # go outside of the shape's area for some reason.
        # self.calculateOffsets(self.selectedShapes, pos)
        dp = pos - self.prevPoint
        if dp:
            for shape in shapes:
                shape.moveBy(dp)
            self.prevPoint = pos
            return True
        return False

    def addPointToEdge(self):
        if (self.hShape is None and
                self.hEdge is None and
                self.prevMovePoint is None):
            return
        shape = self.hShape
        index = self.hEdge
        point = self.prevMovePoint
        shape.insertPoint(index, point)
        shape.highlightVertex(index, shape.MOVE_VERTEX)
        self.hShape = shape
        self.hVertex = index
        self.hEdge = None

    def finalise(self):
        assert self.current
        self.current.close()
        self.shapes.append(self.current)
        self.storeShapes()
        self.current = None
        self.setHiding(False)
        self.newShape.emit()
        self.update()

    def isShapeRestorable(self):
        if len(self.shapesBackups) < 2:
            return False
        return True

    def storeShapes(self):
        shapesBackup = []
        for shape in self.shapes:
            shapesBackup.append(shape.copy())
        if len(self.shapesBackups) >= 10:
            self.shapesBackups = self.shapesBackups[-9:]
        self.shapesBackups.append(shapesBackup)

    def restoreShape(self):
        if not self.isShapeRestorable():
            return
        self.shapesBackups.pop()  # latest
        shapesBackup = self.shapesBackups.pop()
        self.shapes = shapesBackup
        self.selectedShapes = []
        for shape in self.shapes:
            shape.selected = False
        self.repaint()

    def setHiding(self, enable=True):
        self._hideBackround = self.hideBackround if enable else False

    def unHighlight(self):
        if self.hShape:
            self.hShape.highlightClear()
        self.hVertex = self.hShape = None

    def selectedVertex(self):
        return self.hVertex is not None

    def paintEvent(self, ev):
        # if not self.shapes:
        #     return super(Canvas, self).paintEvent(ev)
        if not self.pixmap():
            return

        p = self._Painter
        p.begin(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.HighQualityAntialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)

        p.scale(self.scale, self.scale)
        p.translate(self.offsetToCenter())
        # p.setPen(QColor(255, 0, 0))
        p.drawImage(0, 0, self.pixmap())

        Shape.scale = self.scale
        for shape in self.shapes:
            if (shape.selected or not self._hideBackround) and \
                    self.isVisible(shape):
                shape.fill = shape.selected or shape == self.hShape
                shape.paint(p)
        if self.current:
            self.current.paint(p)
            self.line.paint(p)
        if self.selectedShapesCopy:
            for s in self.selectedShapesCopy:
                s.paint(p)

        if (self.fillDrawing() and self._createMode == 'polygon' and
                self.current is not None and len(self.current.points) >= 2):
            drawing_shape = self.current.copy()
            drawing_shape.addPoint(self.line[1])
            drawing_shape.fill = True
            drawing_shape.fill_color.setAlpha(64)
            drawing_shape.paint(p)

        p.end()

    def pixmap(self):
        if self.image_wapper:
            return self.image_wapper.getQImage()
        return None

    def isVisible(self, shape):
        return self.visible.get(shape, True)

    def closeEnough(self, p1, p2):
        return utils.distance(p1 - p2) < (self.epsilon / self.scale)

    def outOfPixmap(self, p):
        w, h = self.pixmap().width(), self.pixmap().height()
        return not (0 <= p.x() <= w - 1 and 0 <= p.y() <= h - 1)

    def transformPos(self, point):
        return point / self.scale - self.offsetToCenter()

    def offsetToCenter(self):
        pixmap = self.pixmap()
        s = self.scale
        area = super(Canvas, self).size()
        w, h = pixmap.width() * s, pixmap.height() * s
        aw, ah = area.width(), area.height()
        x = (aw - w) / (2 * s) if aw > w else 0
        y = (ah - h) / (2 * s) if ah > h else 0
        return QtCore.QPoint(x, y)

    def sizeHint(self):
        return self.minimumSizeHint()

    def minimumSizeHint(self):
        if self.pixmap():
            return self.scale * self.pixmap().size()

        return super(Canvas, self).minimumSizeHint()

    def leaveEvent(self, ev):
        self.restoreCursor()

    def focusOutEvent(self, ev):
        self.restoreCursor()

    def enterEvent(self, ev):
        self.overrideCursor(self._curCursor)

    def overrideCursor(self, cursor):
        old_cursor = QApplication.overrideCursor()
        if old_cursor == None or old_cursor != cursor:
            QApplication.restoreOverrideCursor()
            QApplication.setOverrideCursor(cursor)
            self._curCursor = cursor

    @staticmethod
    def restoreCursor():
        QApplication.restoreOverrideCursor()
