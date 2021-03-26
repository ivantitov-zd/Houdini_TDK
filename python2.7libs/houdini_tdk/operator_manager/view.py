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

from .delegate import OperatorManagerLibraryDelegate


class OperatorManagerView(QTreeView):
    def __init__(self):
        super(OperatorManagerView, self).__init__()

        header = self.header()
        header.setSectionsMovable(False)
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.hide()

        self.setUniformRowHeights(True)
        self.setIconSize(QSize(16, 16))

        self.setItemDelegate(OperatorManagerLibraryDelegate())
        # self.setAlternatingRowColors(True)  # Todo: Disabled due to a bug that clipping delegate's text

        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

    def hasSelection(self):
        """Returns True if selection model has selected items, False otherwise."""
        return self.selectionModel().hasSelection()

    def isSingleSelection(self):
        """Returns True if selection contains only one row."""
        return self.hasSelection() and len(self.selectionModel().selectedRows(0)) == 1

    def isMultipleSelection(self):
        """Returns True if selection contains more than one row."""
        return self.hasSelection() and len(self.selectionModel().selectedRows(0)) > 1

    def selectedIndex(self):
        """
        Returns a single selected index.
        Should be used only when isSingleSelection is True.

        Raised IndexError if no selection.
        """
        return self.selectionModel().selectedIndexes()[0]

    def indexDepth(self, index):
        """Returns level of nesting of the index. Root has level 0."""
        depth = 0
        while index.isValid():
            index = index.parent()
            depth += 1
        return depth

    def deselectDifferingDepth(self, target_index):
        """Remove items with differing level of nesting from the selection model."""
        selection_model = self.selectionModel()
        target_depth = self.indexDepth(target_index)
        for index in selection_model.selectedIndexes():
            depth = self.indexDepth(index)
            if depth != target_depth:
                selection_model.select(index, QItemSelectionModel.Deselect)

    def deselectDifferringParent(self, target_index):
        raise NotImplementedError
