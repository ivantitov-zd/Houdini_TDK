"""
Tool Development Kit for SideFX Houdini
Copyright (C) 2021 Ivan Titov

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
            row_rect.setRight(option.widget.width())

            icon_rect = QRectF(option.rect)
            icon_rect.setRight(45)

            text_rect = QRectF(row_rect)
            text_rect.setLeft(45)
            text_rect.setRight(row_rect.right() - 30)

            selection_rect = QRectF(row_rect)
            selection_rect.setLeft(icon_rect.right())

            painter.save()
            option.rect = icon_rect.toRect()
            super(OperatorManagerLibraryDelegate, self).paint(painter, option, index)
            painter.restore()

            if option.state & QStyle.State_Selected:
                painter.fillRect(selection_rect, option.palette.highlight())

            metrics = painter.fontMetrics()
            text = metrics.elidedText(index.data(TextRole), Qt.ElideMiddle, text_rect.width())

            painter.drawText(text_rect, Qt.AlignVCenter | Qt.AlignLeft, text)

            painter.restore()
        else:
            super(OperatorManagerLibraryDelegate, self).paint(painter, option, index)
