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
    from PyQt5.QtCore import Qt
except ImportError:
    from PySide2.QtWidgets import QDialog, QVBoxLayout
    from PySide2.QtCore import Qt

import hou

from ..notification import notify
from .view import NetworkStatsView
from .model import NetworkStatsModel


class NetworkStatsWindow(QDialog):
    def __init__(self, parent=None):
        super(NetworkStatsWindow, self).__init__(parent)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

        self.setWindowTitle('TDK: Network Statistics')
        self.resize(300, 500)

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


def showStatsForNode(**kwargs):
    if 'node' in kwargs:
        nodes = kwargs['node'],
    else:
        nodes = hou.selectedNodes()

    if not nodes:
        notify('No node selected', hou.severityType.Error)
        return
    elif len(nodes) > 1:
        notify('Too much nodes selected', hou.severityType.Error)
        return

    node = nodes[0]
    if not node.isNetwork():
        notify('Node not a network', hou.severityType.Error)
        return

    window = NetworkStatsWindow(hou.qt.mainWindow())
    window.setWindowTitle('TDK: Network Stats: ' + node.path())
    window.updateData(node)
    window.show()
