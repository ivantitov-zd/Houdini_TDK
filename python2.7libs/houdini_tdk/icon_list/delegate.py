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
    from PyQt5.QtWidgets import QStyledItemDelegate, QStyle
    from PyQt5.QtCore import Qt, QSize
    from PyQt5.QtGui import QColor
except ImportError:
    from PySide2.QtWidgets import QStyledItemDelegate, QStyle
    from PySide2.QtCore import Qt, QSize
    from PySide2.QtGui import QColor


class IconListDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        selected = option.state & QStyle.State_Selected

        if selected or option.state & QStyle.State_HasFocus:
            option.state = option.state & ~QStyle.State_Selected
            painter.save()
            painter.setBrush(QColor(36, 36, 36) if selected else Qt.transparent)
            painter.setPen(QColor(185, 134, 32))
            adjust = painter.pen().width()
            painter.drawRect(option.rect.adjusted(0, 0, -adjust, -adjust))
            painter.restore()

        super(IconListDelegate, self).paint(painter, option, index)
