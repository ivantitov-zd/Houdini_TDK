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

from .delegate import BackupListDelegate


class BackupListView(QTreeView):
    def __init__(self):
        super(BackupListView, self).__init__()

        header = self.header()
        header.setSectionResizeMode(QHeaderView.Stretch)

        self.setUniformRowHeights(True)

        self.setItemDelegate(BackupListDelegate())
        self.setAlternatingRowColors(True)
        self.setRootIsDecorated(False)

        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)

    def hasSelection(self):
        """Returns True if selection model has selected items, False otherwise."""
        return self.selectionModel().hasSelection()

    def selectedIndex(self):
        """
        Returns a single selected index.

        Raises IndexError if no selection.
        """
        return self.selectionModel().selectedIndexes()[0]
