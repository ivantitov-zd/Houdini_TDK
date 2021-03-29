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


class NodeShapeListView(QListView):
    # Signals
    itemDoubleClicked = Signal(QModelIndex)

    def __init__(self):
        super(NodeShapeListView, self).__init__()
        self.viewport().setContentsMargins(15, 15, 15, 15)
        self.setViewMode(QListView.IconMode)

        self.setUniformItemSizes(True)

        self.setResizeMode(QListView.Adjust)
        self.setDragDropMode(QAbstractItemView.NoDragDrop)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.verticalScrollBar().setSingleStep(30)

        self.setGridSize(QSize(100, 88))

        # Item Double Clicked
        self._item_double_clicked_signal_enabled = False
        self.doubleClicked.connect(self.__emitItemDoubleClicked)

    def resizeEvent(self, event):
        super(NodeShapeListView, self).resizeEvent(event)

        # Update grid size
        grid_size = self.gridSize()
        column_count = 7
        spacing = 5
        grid_size.setWidth(self.viewport().width() / column_count - spacing)
        self.setGridSize(grid_size)

    def doubleClickedSignalEnabled(self):
        return self._item_double_clicked_signal_enabled

    def enableDoubleClickedSignal(self, enable=True):
        self._item_double_clicked_signal_enabled = enable

    def __emitItemDoubleClicked(self):
        if not self._item_double_clicked_signal_enabled:
            return

        index = self.currentIndex()
        if index.isValid():
            self.itemDoubleClicked.emit(index)
