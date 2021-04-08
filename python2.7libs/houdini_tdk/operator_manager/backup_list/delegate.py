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
    from PyQt5.QtWidgets import QStyledItemDelegate
    from PyQt5.QtCore import Qt
except ImportError:
    from PySide2.QtWidgets import QStyledItemDelegate
    from PySide2.QtCore import Qt


class BackupListDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        if index.column() == 1:
            option.textElideMode = Qt.ElideLeft
        else:
            option.textElideMode = Qt.ElideNone
        super(BackupListDelegate, self).paint(painter, option, index)
