"""
Tool Development Kit for SideFX Houdini
Copyright (C) 2021  Ivan Titov

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from __future__ import print_function

try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *

    Signal = pyqtSignal
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *

from .node_shape import NodeShape


class NodeShapePreview(QWidget):
    def __init__(self, parent=None):
        super(NodeShapePreview, self).__init__(parent)

        self._shape = None
        self._path = None

    def recacheShape(self, spacing=1):
        rect = self.rect().adjusted(spacing, spacing, -spacing, -spacing)
        self._path = self._shape.fittedInRect(rect).painterPath()
        self.repaint()

    def setShape(self, shape_name):
        if not shape_name:
            self._shape = None
            self.repaint()
            return

        shape = NodeShape.fromName(shape_name)

        if not shape.isValid():
            self._shape = None
            self.repaint()
            return

        self._shape = shape.copy()
        self.recacheShape()
        self.repaint()

    def paintEvent(self, event):
        if not self._shape:
            return

        if not self._path:
            self._path = self._shape.painterPath()

        p = QPainter(self)

        p.eraseRect(event.rect())

        rect_width = event.rect().width()
        if rect_width < 800:
            p.setRenderHint(QPainter.Antialiasing)
            if rect_width < 400:
                p.setRenderHint(QPainter.HighQualityAntialiasing)

        p.setBrush(p.pen().color().darker())
        p.drawPath(self._path)
        p.end()
