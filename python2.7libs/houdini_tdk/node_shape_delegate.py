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


class NodeShapeDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super(NodeShapeDelegate, self).__init__(parent)

    def sizeHint(self, option, index):
        return QSize(64, 64)

    def paint(self, painter, option, index):
        shape = index.data(Qt.UserRole)

        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.HighQualityAntialiasing)

        painter.eraseRect(option.rect)
        painter.fillRect(option.rect, Qt.red)

        super(NodeShapeDelegate, self).paint(painter, option, index)

        top_left = option.rect.topLeft()
        painter.save()
        painter.setTransform(QTransform.fromTranslate(top_left.x() + 60, top_left.y() + 30))
        painter.drawPath(shape)
        painter.restore()
