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
    from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QFileDialog
except ImportError:
    from PySide2.QtWidgets import QWidget, QHBoxLayout, QPushButton, QFileDialog

import hou

from .input_field import InputField


class LocationField(QWidget):
    def __init__(self, initial_location=''):
        super(LocationField, self).__init__()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.text_field = InputField(initial_location)
        self.layout().addWidget(self.text_field)

        self.pick_button = QPushButton()
        self.pick_button.setToolTip('Pick location')
        self.pick_button.setFixedSize(24, 24)
        self.pick_button.setIcon(hou.qt.Icon('BUTTONS_chooser_folder', 16, 16))
        self.pick_button.clicked.connect(self.pickLocation)
        self.layout().addWidget(self.pick_button)

    def text(self):
        return self.text_field.text()

    def setText(self, text):
        self.text_field.setText(text)

    def path(self):
        return hou.expandString(self.text_field.text())

    def setPath(self, path):
        if path is None:
            self.text_field.setText('')

        if not path:
            return

        path = hou.text.collapseCommonVars(path, ['$HOUDINI_USER_PREF_DIR', '$HIP', '$JOB'])
        self.text_field.setText(path)

    def pickLocation(self):
        path = QFileDialog.getExistingDirectory(self, 'Pick Location', self.path())
        self.setPath(path)
