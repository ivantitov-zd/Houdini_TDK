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
except ImportError:
    from PySide2.QtWidgets import QWidget, QGridLayout, QLabel, QCheckBox, QSpacerItem, QSizePolicy
    from PySide2.QtGui import QIntValidator

from .. import ui

WARNING_PIXMAP = ui.icon('NETVIEW_warning_badge', 16).pixmap(16)


class MainOptionsWidget(QWidget):
    def __init__(self):
        super(MainOptionsWidget, self).__init__()

        layout = QGridLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        self.obfuscate_network_toggle = QCheckBox('Obfuscate network')
        self.obfuscate_network_toggle.setChecked(True)
        layout.addWidget(self.obfuscate_network_toggle, 0, 0, 1, -1)

        self.obfuscate_python_toggle = QCheckBox('Obfuscate Python code')
        self.obfuscate_python_toggle.setChecked(False)
        self.obfuscate_python_toggle.setDisabled(True)
        layout.addWidget(self.obfuscate_python_toggle, 1, 0)

        warning_icon_size = self.obfuscate_python_toggle.sizeHint().height() - 2

        self.obfuscate_python_warn_icon = QLabel()
        self.obfuscate_python_warn_icon.setFixedSize(warning_icon_size, warning_icon_size)
        self.obfuscate_python_warn_icon.setPixmap(WARNING_PIXMAP)
        self.obfuscate_python_warn_icon.setToolTip('Not available in this release')
        layout.addWidget(self.obfuscate_python_warn_icon, 1, 1)

        self.obfuscate_vex_toggle = QCheckBox('Obfuscate VEX code')
        self.obfuscate_vex_toggle.setChecked(True)
        layout.addWidget(self.obfuscate_vex_toggle, 2, 0)

        self.obfuscate_vex_warn_icon = QLabel()
        self.obfuscate_vex_warn_icon.setFixedSize(warning_icon_size, warning_icon_size)
        self.obfuscate_vex_warn_icon.setPixmap(WARNING_PIXMAP)
        self.obfuscate_vex_warn_icon.setToolTip('Currently only minification is supported')
        layout.addWidget(self.obfuscate_vex_warn_icon, 2, 1)

        self.install_toggle = QCheckBox('Install new HDA')
        self.install_toggle.setChecked(True)
        layout.addWidget(self.install_toggle, 3, 0, 1, -1)

        self.replace_node_toggle = QCheckBox('Replace source node')
        self.replace_node_toggle.setChecked(True)
        self.install_toggle.toggled.connect(self.replace_node_toggle.setEnabled)
        layout.addWidget(self.replace_node_toggle, 4, 0, 1, -1)

        self.spacer = QSpacerItem(0, 0, QSizePolicy.Ignored, QSizePolicy.Expanding)
        layout.addItem(self.spacer, 5, 0, 1, -1)
