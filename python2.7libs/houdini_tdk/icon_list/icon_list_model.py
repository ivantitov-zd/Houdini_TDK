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
    from PyQt5.QtCore import QAbstractListModel, QModelIndex
    from PyQt5.QtGui import Qt
except ImportError:
    from PySide2.QtCore import QAbstractListModel, QModelIndex
    from PySide2.QtGui import Qt

import hou


class IconListModel(QAbstractListModel):
    def __init__(self, parent=None):
        super(IconListModel, self).__init__(parent)

        self._icon_size = 64

        # Data
        ICON_INDEX_FILE = hou.expandString('$HFS/houdini/config/Icons/SVGIcons.index')
        self.__data = tuple(sorted(hou.loadIndexDataFromFile(ICON_INDEX_FILE).keys()))

    def iconSize(self):
        return self._icon_size

    def setIconSize(self, size):
        if size != self._icon_size:
            self._icon_size = size
            self.dataChanged.emit(self.index(0, 0), self.index(len(self.__data), 0), [Qt.DecorationRole])

    def hasChildren(self, parent):
        return not parent.isValid()

    def rowCount(self, parent):
        return len(self.__data)

    def data(self, index, role):
        if not index.isValid():
            return

        icon_name = self.__data[index.row()]

        if role == Qt.DisplayRole:
            label = icon_name.replace('.svg', '')  # VOP_wood.svg -> VOP_wood
            if '_' in label:
                label = ' '.join(label.split('_')[1:]).title()  # VOP_wood -> Wood
            return label
        elif role == Qt.DecorationRole:
            return hou.qt.Icon(icon_name, self._icon_size, self._icon_size)
        elif role == Qt.UserRole or role == Qt.ToolTipRole:
            return icon_name

    def indexByKey(self, key):
        for index, name in enumerate(self.__data):
            if name[:-4] == key:
                return self.index(index, 0)

        return QModelIndex()
