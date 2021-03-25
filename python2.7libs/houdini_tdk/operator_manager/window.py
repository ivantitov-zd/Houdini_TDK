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

import hou

from ..widgets import FilterField
from ..fuzzy_filter_proxy_model import FuzzyFilterProxyModel
from .model import OperatorManagerFilesModel
from .view import OperatorManagerView


class OperatorManagerWindow(QWidget):
    def __init__(self, parent=hou.qt.mainWindow()):
        super(OperatorManagerWindow, self).__init__(parent, Qt.Window)

        self.setWindowTitle('TDK: Operator Manager')
        self.setWindowIcon(hou.qt.Icon('MISC_digital_asset', 32, 32))
        self.resize(400, 600)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        self.filter_field = FilterField()
        layout.addWidget(self.filter_field)

        self.model = OperatorManagerFilesModel(self)
        self.model.updateData()

        # self.proxy_model = FuzzyFilterProxyModel(self)
        # self.proxy_model.setSourceModel(self.model)

        self.view = OperatorManagerView()
        self.view.setModel(self.model)
        layout.addWidget(self.view)
