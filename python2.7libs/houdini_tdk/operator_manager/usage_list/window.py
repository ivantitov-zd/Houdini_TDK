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

import hou
import nodegraphview

from ...widgets import InputField
from ...fuzzy_proxy_model import FuzzyProxyModel
from .view import UsageListView
from .model import UsageListModel


class UsageListWindow(QWidget):
    def __init__(self, parent=hou.qt.mainWindow()):
        super(UsageListWindow, self).__init__(parent, Qt.Window)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

        self._node_type = None

        self.updateWindowTitle()
        self.setWindowIcon(hou.qt.Icon('BUTTONS_history', 32, 32))
        self.resize(400, 600)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        self.filter_field = InputField()
        layout.addWidget(self.filter_field)

        self.model = UsageListModel(self)

        self.fuzzy_proxy_model = FuzzyProxyModel(self)
        self.fuzzy_proxy_model.setSourceModel(self.model)
        self.filter_field.textChanged.connect(self.fuzzy_proxy_model.setPattern)

        self.view = UsageListView()
        self.view.setModel(self.fuzzy_proxy_model)
        header = self.view.header()
        header.setSectionResizeMode(0, QHeaderView.Interactive)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        self.view.selectionModel().selectionChanged.connect(self._selectNode)
        layout.addWidget(self.view)

    def updateWindowTitle(self):
        title = 'TDK: Usages'
        if self._node_type:
            title += ': ' + self._node_type.nameWithCategory()
        self.setWindowTitle(title)

    def setNodeType(self, node_type):
        self.model.setNodeType(node_type)
        self._node_type = node_type
        self.updateWindowTitle()

    def _selectNode(self):
        """Shows and selects node in network editor."""
        if not self.view.hasSelection():
            return

        editor = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)
        if editor is None:  # No active network editor found
            return

        index = self.view.selectedIndex()
        if not index.isValid():
            return

        node = index.data(Qt.UserRole + 1)
        if not node.exists():
            editor.flashMessage('STATUS_error', 'Node was deleted', 2)
            return

        with hou.undos.disabler():
            here = editor.pwd().path()
            if here != node.parent().path():
                nodegraphview.changeNetwork(editor, node.parent())

            nodes = (node,)
            nodegraphview.modifySelection(None, editor, nodes)
            nodegraphview.frameItems(editor, nodes)
