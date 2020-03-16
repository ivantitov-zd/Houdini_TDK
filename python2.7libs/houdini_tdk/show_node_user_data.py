"""
Tool Development Kit for SideFX Houdini
Copyright (C) 2020  Ivan Titov

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

import hou


class UserDataModel(QAbstractListModel):
    def __init__(self, parent=None):
        super(UserDataModel, self).__init__(parent)

        # Data
        self.__data = {}
        self.__keys = ()

    def updateDataFromNode(self, node, cached=False):
        self.beginResetModel()
        if cached:
            self.__data = node.cachedUserDataDict()
        else:
            self.__data = node.userDataDict()
        self.__keys = tuple(self.__data.keys())
        self.endResetModel()

    def rowCount(self, parent):
        return len(self.__data)

    def data(self, index, role):
        key = self.__keys[index.row()]
        if role == Qt.DisplayRole:
            return key
        elif role == Qt.UserRole:
            return self.__data[key]


class UserDataListView(QListView):
    def __init__(self):
        super(UserDataListView, self).__init__()

        self.setAlternatingRowColors(True)


class UserDataWindow(QWidget):
    def __init__(self, node, parent=None):
        super(UserDataWindow, self).__init__(parent, Qt.Window)

        self.setWindowTitle('Node User Data: ' + node.path())

        # Layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Key List
        self.user_data_model = UserDataModel()

        self.user_data_list = UserDataListView()
        self.user_data_list.setMaximumWidth(120)
        self.user_data_list.setModel(self.user_data_model)
        selection_model = self.user_data_list.selectionModel()
        selection_model.currentChanged.connect(self._readData)
        layout.addWidget(self.user_data_list)

        # Data View
        self.user_data_view = QTextEdit()
        layout.addWidget(self.user_data_view)

    def _readData(self):
        selection_model = self.user_data_list.selectionModel()
        value = selection_model.currentIndex().data(Qt.UserRole)
        self.user_data_view.setText(str(value))


def showNodeUserData(node=None, cached=False, **kwargs):
    if node is None:
        nodes = hou.selectedNodes()
        if not nodes:
            raise hou.Error('No node selected')
        elif len(nodes) > 1:
            raise hou.Error('Too much nodes selected')
        node = nodes[0]
    window = UserDataWindow(node, hou.qt.mainWindow())
    window.user_data_model.updateDataFromNode(node, cached)
    window.show()
