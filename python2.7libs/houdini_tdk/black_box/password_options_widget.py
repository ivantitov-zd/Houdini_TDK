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
    from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QCheckBox, QSpacerItem, QSizePolicy
    from PyQt5.QtGui import QIntValidator
    from PyQt5.QtCore import Qt
except ImportError:
    from PySide2.QtWidgets import QWidget, QGridLayout, QLabel, QCheckBox, QSpacerItem, QSizePolicy
    from PySide2.QtGui import QIntValidator
    from PySide2.QtCore import Qt

from ..widgets import InputField, Slider

MINIMUM_RETRIES = 0
MAXIMUM_RETRIES = 5
DEFAULT_RETRIES = 3


class PasswordOptionsWidget(QWidget):
    def __init__(self):
        super(PasswordOptionsWidget, self).__init__()

        layout = QGridLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        self.use_password_toggle = QCheckBox('Use password')
        self.use_password_toggle.setChecked(False)
        layout.addWidget(self.use_password_toggle, 0, 0, 1, -1)

        self.password_label = QLabel('Password')
        layout.addWidget(self.password_label, 1, 0)

        self.password_field = InputField()
        self.password_field.setAlignment(Qt.AlignCenter)
        self.password_field.setEchoMode(InputField.PasswordEchoOnEdit)
        self.password_field.setDisabled(True)
        self.use_password_toggle.toggled.connect(self.password_field.setEnabled)
        layout.addWidget(self.password_field, 1, 1, 1, -1)

        self.retries_label = QLabel('Number of retries')
        layout.addWidget(self.retries_label, 2, 0)

        self.retries_field = InputField(str(DEFAULT_RETRIES))
        self.retries_field.setValidator(QIntValidator(MINIMUM_RETRIES, MAXIMUM_RETRIES))
        self.retries_field.setAlignment(Qt.AlignCenter)
        self.retries_field.setMaximumWidth(60)
        self.retries_field.setDisabled(True)
        self.use_password_toggle.toggled.connect(self.retries_field.setEnabled)
        layout.addWidget(self.retries_field, 2, 1)

        self.retries_slider = Slider(MINIMUM_RETRIES, MAXIMUM_RETRIES, DEFAULT_RETRIES)
        self.retries_slider.setDisabled(True)
        self.use_password_toggle.toggled.connect(self.retries_slider.setEnabled)
        layout.addWidget(self.retries_slider, 2, 2, 1, -1)

        self.retries_field.textChanged.connect(lambda v: self.retries_slider.setValue(int(v or DEFAULT_RETRIES)))
        self.retries_slider.valueChanged.connect(lambda v: self.retries_field.setText(str(v)))

        self.spacer = QSpacerItem(0, 0, QSizePolicy.Ignored, QSizePolicy.Expanding)
        layout.addItem(self.spacer, 3, 0, 1, -1)
