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
    from PyQt5.QtWidgets import (QDialog, QGridLayout, QLabel, QTabWidget, QSpacerItem, QSizePolicy, QFrame,
                                 QHBoxLayout, QPushButton)
    from PyQt5.QtCore import Qt
except ImportError:
    from PySide2.QtWidgets import (QDialog, QGridLayout, QLabel, QTabWidget, QSpacerItem, QSizePolicy, QFrame,
                                   QHBoxLayout, QPushButton)
    from PySide2.QtCore import Qt

import hou

from .. import ui
from ..widgets import FilePathField
from .main_options_widget import MainOptionsWidget
from .password_options_widget import PasswordOptionsWidget
from .time_limit_options_widget import TimeLimitOptionsWidget


class MakeBlackBoxWindow(QDialog):
    def __init__(self, parent=hou.qt.mainWindow()):
        super(MakeBlackBoxWindow, self).__init__(parent)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

        self.setWindowTitle('TDK: Make black box HDA')
        self.setWindowIcon(ui.icon('COMMON_stash', 32))
        self.resize(400, 300)

        main_layout = QGridLayout(self)
        main_layout.setContentsMargins(6, 6, 6, 6)
        main_layout.setSpacing(4)

        self._output_path_label = QLabel('Output')
        main_layout.addWidget(self._output_path_label, 0, 0)

        self._path_field = FilePathField(formats='Houdini Digital Assets (*.hda)')
        main_layout.addWidget(self._path_field, 0, 1, 1, -1)

        self._tabs = QTabWidget()
        main_layout.addWidget(self._tabs, 1, 0, 1, -1)

        self._main_options_widget = MainOptionsWidget()
        self._tabs.addTab(self._main_options_widget, 'Main')

        self._password_options_widget = PasswordOptionsWidget()
        self._tabs.addTab(self._password_options_widget, 'Password')

        self._time_limit_options_widget = TimeLimitOptionsWidget()
        self._tabs.addTab(self._time_limit_options_widget, 'Time limit')

        spacer = QSpacerItem(0, 0, QSizePolicy.Ignored, QSizePolicy.Expanding)
        main_layout.addItem(spacer, 2, 0, 1, -1)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        main_layout.addWidget(line, 3, 0, 1, -1)

        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(4)
        main_layout.addLayout(buttons_layout, 4, 0, 1, -1)

        spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Ignored)
        buttons_layout.addSpacerItem(spacer)

        self._ok_button = QPushButton('OK')
        self._ok_button.clicked.connect(self.accept)
        buttons_layout.addWidget(self._ok_button)

        self._cancel_button = QPushButton('Cancel')
        self._cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self._cancel_button)
