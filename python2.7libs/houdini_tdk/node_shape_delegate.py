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

from houdini_tdk.node_shape_list_model import NodeShapeListModel

qInstallMessageHandler(lambda *args: None)


class NodeShapeDelegate(QStyledItemDelegate):
    def sizeHint(self, option, index):
        grid_width = self.parent().gridSize().width()
        if grid_width > 100:
            ratio = grid_width / 105.0
            width = 100 * ratio
        else:
            width = 100
        return QSize(width, 70)

    def paint(self, painter, option, index):
        painter.save()

        painter.eraseRect(option.rect)

        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.HighQualityAntialiasing)

        pen_width = painter.pen().width()
        inner_rect = option.rect.adjusted(pen_width, pen_width, -pen_width, -pen_width)
        spacing = pen_width * 4
        inner_rect_spaced = inner_rect.adjusted(spacing, spacing, -spacing, -spacing)

        if option.state & QStyle.State_Selected:
            painter.drawRect(inner_rect)

        if inner_rect_spaced.width() > 30:
            metrics = painter.fontMetrics()
            text_height = metrics.height()
            text = metrics.elidedText(index.data(Qt.DisplayRole), Qt.ElideRight, inner_rect_spaced.width())
            painter.drawText(inner_rect, Qt.AlignHCenter | Qt.AlignBottom, text)
        else:
            text_height = 0

        if inner_rect_spaced.width() > 10:
            shape = index.data(NodeShapeListModel.ShapeRole)
            painter.setBrush(painter.pen().color().darker())
            icon_rect = inner_rect_spaced.adjusted(0, 0, 0, -text_height)
            painter.drawPath(shape.fittedInRect(icon_rect).painterPath())

        painter.restore()
