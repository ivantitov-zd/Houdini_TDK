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
    from PyQt5.QtCore import QModelIndex, pyqtSignal as Signal, QSize, QEvent
    from PyQt5.QtGui import Qt, QKeySequence
    from PyQt5.QtWidgets import QListView, QAbstractItemView, QApplication, QFileDialog, QAction
except ImportError:
    from PySide2.QtCore import QModelIndex, Signal, QSize, QEvent
    from PySide2.QtGui import Qt, QKeySequence
    from PySide2.QtWidgets import QListView, QAbstractItemView, QApplication, QFileDialog, QAction

from .delegate import IconListDelegate


class IconListView(QListView):
    # Signals
    itemDoubleClicked = Signal(QModelIndex)

    def __init__(self):
        super(IconListView, self).__init__()

        self.setViewMode(QListView.IconMode)
        self.setItemDelegate(IconListDelegate())

        self.setUniformItemSizes(True)
        self.setSpacing(10)
        self.setStyleSheet('QListView::item { padding: 5px; }')

        self.setResizeMode(QListView.Adjust)
        self.viewport().installEventFilter(self)
        self.setDragDropMode(QAbstractItemView.NoDragDrop)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

        # Item Double Clicked
        self._item_double_clicked_signal_enabled = False
        self.doubleClicked.connect(self.__emitItemDoubleClicked)

    def scrollToCurrent(self):
        if self.currentIndex().isValid():
            self.scrollTo(self.currentIndex(), QAbstractItemView.PositionAtCenter)

    def setIconSize(self, size):
        super(IconListView, self).setIconSize(QSize(size, size))
        self.verticalScrollBar().setSingleStep(int(size / 2.5))
        self.scrollToCurrent()

    def resizeEvent(self, event):
        super(IconListView, self).resizeEvent(event)
        self.scrollToCurrent()

    def zoomIn(self, amount=8):
        size = min(self.iconSize().width() + amount, 128)
        self.setIconSize(size)

    def zoomOut(self, amount=8):
        size = max(self.iconSize().width() - amount, 48)
        self.setIconSize(size)

    def eventFilter(self, watched, event):
        if watched == self.viewport() and event.type() == QEvent.Wheel:
            if event.modifiers() == Qt.ControlModifier:
                if event.delta() > 0:
                    self.zoomIn()
                else:
                    self.zoomOut()
                return True
        return False

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.ZoomIn):
            self.zoomIn()
        elif event.matches(QKeySequence.ZoomOut):
            self.zoomOut()
        else:
            super(IconListView, self).keyPressEvent(event)

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
