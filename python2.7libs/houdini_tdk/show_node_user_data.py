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

import json

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

from notification import notify


class UserDataItem:
    def __init__(self, key, data, cached):
        self.key = key
        self.data = data
        self.cached = cached


class UserDataModel(QAbstractListModel):
    DEFAULT_ICON = hou.qt.Icon('DATATYPES_file', 16, 16)
    CACHED_DATA_ICON = hou.qt.Icon('NETVIEW_time_dependent_badge', 16, 16)

    def __init__(self, parent=None):
        super(UserDataModel, self).__init__(parent)

        # Data
        self.__data = []

    def updateDataFromNode(self, node):
        self.beginResetModel()
        self.__data = []
        if node is not None:
            for key, data in node.userDataDict().items():
                self.__data.append(UserDataItem(key, data, False))

            for key, data in node.cachedUserDataDict().items():
                self.__data.append(UserDataItem(key, data, True))
        self.endResetModel()

    def indexByKey(self, key):
        for index, data in enumerate(self.__data):
            if data.key == key:
                return self.index(index, 0)

        return QModelIndex()

    def rowCount(self, parent):
        return len(self.__data)

    def data(self, index, role):
        item = self.__data[index.row()]
        if role == Qt.DisplayRole:
            return item.key
        elif role == Qt.DecorationRole:
            if item.cached:
                return UserDataModel.CACHED_DATA_ICON
            else:
                return UserDataModel.DEFAULT_ICON
        elif role == Qt.UserRole:
            return item.data


class UserDataListView(QListView):
    def __init__(self):
        super(UserDataListView, self).__init__()

        self.setAlternatingRowColors(True)


class UserDataWindow(QWidget):
    def __init__(self, parent=None):
        super(UserDataWindow, self).__init__(parent, Qt.Window)

        self.setWindowIcon(hou.qt.Icon('TOP_jsondata', 32, 32))

        # Layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)

        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # Key List
        self.user_data_model = UserDataModel()

        self.user_data_list = UserDataListView()
        self.user_data_list.setModel(self.user_data_model)
        self.user_data_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        selection_model = self.user_data_list.selectionModel()
        selection_model.currentChanged.connect(self._readData)
        splitter.addWidget(self.user_data_list)

        # Data View
        self.user_data_view = QTextEdit()
        splitter.addWidget(self.user_data_view)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)

        # Data
        self._current_key = None
        self._node = None

        # Update
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(4)
        main_layout.addLayout(bottom_layout)

        update_button = QPushButton()
        update_button.setToolTip('Update from Node')
        update_button.setFixedSize(24, 24)
        update_button.setIcon(hou.qt.Icon('NETVIEW_reload', 16, 16))
        update_button.clicked.connect(self.updateData)
        bottom_layout.addWidget(update_button)

        self.update_timer = QTimer(self)
        self.update_timer.setInterval(500)
        self.update_timer.timeout.connect(self.updateData)

        self.auto_update_toggle = QCheckBox('Auto Update')
        self.auto_update_toggle.setFixedWidth(100)
        self.auto_update_toggle.setChecked(True)
        self.auto_update_toggle.toggled.connect(self._switchTimer)
        bottom_layout.addWidget(self.auto_update_toggle, 0)

        bottom_layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Ignored))

        self.prettify_json_button = QPushButton()
        self.prettify_json_button.setToolTip('Prettify JSON')
        self.prettify_json_button.setFixedSize(24, 24)
        self.prettify_json_button.setIcon(hou.qt.Icon('TOP_jsondata', 16, 16))
        self.prettify_json_button.clicked.connect(self._prettifyJSON)
        bottom_layout.addWidget(self.prettify_json_button)

    def _updatePrettifyJSONButtonVisibility(self):
        text = self.user_data_view.toPlainText()
        try:
            data = json.loads(text)

            if text == json.dumps(data, indent=4):
                raise ValueError

            self.prettify_json_button.setVisible(True)
        except ValueError:
            self.prettify_json_button.setVisible(False)

    def _prettifyJSON(self):
        text = self.user_data_view.toPlainText()
        try:
            data = json.loads(text)
            text = json.dumps(data, indent=4)
            self.user_data_view.setPlainText(text)
        except ValueError:
            return

    def _readData(self):
        selection_model = self.user_data_list.selectionModel()
        index = selection_model.currentIndex()

        if not index.isValid():
            return

        self._current_key = index.data(Qt.DisplayRole)
        value = index.data(Qt.UserRole)
        self.user_data_view.setText(value)
        self._updatePrettifyJSONButtonVisibility()

    def _switchTimer(self):
        if self.update_timer.isActive():
            self.update_timer.stop()
        else:
            self.update_timer.start()

    # def _removeCallbacks(self):
    #     if self.node:
    #         node.removeEventCallback((hou.nodeEventType.CustomDataChanged,), self.updateData)

    def __del__(self):
        # self._removeCallbacks()
        self.update_timer.stop()

    def updateData(self, auto=True):
        if auto and not self.auto_update_toggle.isChecked():
            return

        if self._node:
            self.user_data_model.updateDataFromNode(self._node)

        new_index = self.user_data_model.indexByKey(self._current_key)
        if new_index.isValid():
            self.user_data_list.setCurrentIndex(new_index)

    def setCurrentNode(self, node):
        if self._node:
            self._removeCallbacks()

        self._node = node
        # node.addEventCallback((hou.nodeEventType.CustomDataChanged,), self.updateData)
        self.update_timer.start()
        self.updateData(False)
        self.setWindowTitle('TDK: Node User Data: ' + node.path())


def showNodeUserData(node=None, **kwargs):
    if node is None:
        nodes = hou.selectedNodes()
        if not nodes:
            notify('No node selected', hou.severityType.Error)
            return
        elif len(nodes) > 1:
            notify('Too much nodes selected', hou.severityType.Error)
            return
        node = nodes[0]

    window = UserDataWindow(hou.qt.mainWindow())
    window.setCurrentNode(node)
    window.show()
