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

from ...utils import openFileLocation
from .view import BackupListView
from .model import BackupListModel


class BackupListWindow(QWidget):
    def __init__(self, parent=hou.qt.mainWindow()):
        super(BackupListWindow, self).__init__(parent, Qt.Window)

        self._library_path = ''

        self.updateWindowTitle()
        self.setWindowIcon(hou.qt.Icon('BUTTONS_history', 32, 32))
        self.resize(400, 600)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        self.model = BackupListModel(self)

        self.view = BackupListView()
        self.view.setModel(self.model)
        layout.addWidget(self.view)

        # self._createActions()
        # self._createContextMenus()

    def updateWindowTitle(self):
        title = 'TDK: Backups'
        if self._library_path:
            title += ': ' + self._library_path
        self.setWindowTitle(title)

    def setLibrary(self, library_path):
        self.model.setLibrary(library_path)
        self._library_path = library_path
        self.updateWindowTitle()

    def _onOpenLocation(self):
        """Opens location of the selected backup HDA."""
        raise NotImplementedError

    def _onInstall(self):
        raise NotImplementedError

    def _onRestore(self):
        raise NotImplementedError

    def _onCompare(self):
        raise NotImplementedError

    def _createActions(self):
        raise NotImplementedError

    def _createContextMenus(self):
        raise NotImplementedError

    def _showContextMenu(self):
        raise NotImplementedError
