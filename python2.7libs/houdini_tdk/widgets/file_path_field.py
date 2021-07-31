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

from .. import ui
from .input_field import InputField


class FilePathField(QWidget):
    def __init__(self, initial_path='', formats='All (*.*)', new=True):
        super(FilePathField, self).__init__()

        self._formats = formats

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self._text_field = InputField(initial_path)
        layout.addWidget(self._text_field)

        self._pick_path_button = QPushButton()
        self._pick_path_button.setToolTip('Pick file path')
        self._pick_path_button.setFixedSize(24, 24)
        self._pick_path_button.setIcon(ui.icon('BUTTONS_chooser_file', 16))
        if new:
            self._pick_path_button.clicked.connect(self.pickNewFile)
        else:
            self._pick_path_button.clicked.connect(self.pickFile)
        layout.addWidget(self._pick_path_button)

    def text(self):
        return self._text_field.text()

    def setText(self, text):
        self._text_field.setText(text)

    def path(self):
        return hou.expandString(self._text_field.text())

    def setPath(self, path):
        if path is None:
            self._text_field.setText('')

        if not path:
            return

        path = hou.text.collapseCommonVars(path, ['$HOUDINI_USER_PREF_DIR', '$HIP', '$JOB'])
        self._text_field.setText(path)

    def pickFile(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Pick file path', self.path(), self._formats)
        if path:
            self.setPath(path)

    def pickNewFile(self):
        path, _ = QFileDialog.getSaveFileName(self, 'Pick file path', self.path(), self._formats)
        if path:
            self.setPath(path)
