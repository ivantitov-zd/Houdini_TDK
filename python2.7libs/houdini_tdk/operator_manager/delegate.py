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

try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *

    Signal = pyqtSignal
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *

from .model import TextRole


class OperatorManagerLibraryDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        if isinstance(index.data(Qt.UserRole), basestring):
            if index.column() == 1:
                return

            painter.save()

            row_rect = QRectF(option.rect)
            row_rect.setLeft(45)
            row_rect.setRight(option.widget.width())

            icon_rect = QRectF(option.rect)
            icon_rect.setLeft(0)
            icon_rect.setRight(45)

            text_rect = QRectF(row_rect)
            text_rect.setRight(row_rect.right() - 30)

            additional_selection_rect = QRectF(row_rect)
            additional_selection_rect.setLeft(option.rect.right() + 1)

            painter.save()
            painter.setClipping(True)
            painter.setClipRect(icon_rect)
            super(OperatorManagerLibraryDelegate, self).paint(painter, option, index)
            painter.restore()

            if option.state & QStyle.State_Selected and index.column() == 0:
                painter.fillRect(additional_selection_rect, option.palette.highlight())

            metrics = painter.fontMetrics()
            text = metrics.elidedText(index.data(TextRole), Qt.ElideMiddle, text_rect.width(), Qt.TextSingleLine)

            text_image = QImage(text_rect.size().toSize(), QImage.Format_ARGB32_Premultiplied)
            text_image.fill(Qt.transparent)
            p = QPainter(text_image)
            p.setPen(option.palette.text().color())
            p.drawText(0, 0, text_rect.width(), text_rect.height(), Qt.AlignVCenter | Qt.AlignLeft, text)
            p.end()

            painter.drawImage(text_rect.topLeft(), text_image)

            painter.restore()
        else:
            super(OperatorManagerLibraryDelegate, self).paint(painter, option, index)
