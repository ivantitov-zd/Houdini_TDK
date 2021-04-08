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
    from PyQt5.QtWidgets import QDialog, QVBoxLayout
except ImportError:
    from PySide2.QtWidgets import QDialog, QVBoxLayout

from .view import NetworkStatsView
from .model import NetworkStatsModel


class NetworkStatsWindow(QDialog):
    def __init__(self, parent=hou.qt.mainWindow()):
        super(NetworkStatsWindow, self).__init__(parent)

        self.setWindowTitle('TDK: Network Statistics')

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        stats_model = NetworkStatsModel()

        self._stats_view = NetworkStatsView()
        self._stats_view.setModel(stats_model)
        layout.addWidget(self._stats_view)

    def updateData(self, node):
        self._stats_view.model().updateData(node)
        self._stats_view.expandAll()


def showStatsForNode(node, **kwargs):
    window = NetworkStatsWindow()
    window.setWindowTitle('TDK: Network Statistics: ' + node.path())
    window.updateData(node)
    window.show()
