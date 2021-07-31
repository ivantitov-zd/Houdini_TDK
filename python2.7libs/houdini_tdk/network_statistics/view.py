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
    from PyQt5.QtWidgets import QTreeView, QHeaderView
except ImportError:
    from PySide2.QtWidgets import QTreeView, QHeaderView


class NetworkStatsView(QTreeView):
    def __init__(self):
        super(NetworkStatsView, self).__init__()

        header = self.header()
        header.setSectionsMovable(False)
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setResizeContentsPrecision(50)
        header.hide()

        self.setUniformRowHeights(True)

        self.setRootIsDecorated(False)
        self.setStyleSheet('QTreeView::branch { border-image: none; image: none; }')
        self.setItemsExpandable(False)
