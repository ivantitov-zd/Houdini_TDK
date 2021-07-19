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

import os

try:
    from PyQt5.QtGui import Qt
    from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLabel, QCheckBox, QSpacerItem, QSizePolicy,
                                 QPushButton)
except ImportError:
    from PySide2.QtGui import Qt
    from PySide2.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLabel, QCheckBox, QSpacerItem, QSizePolicy,
                                   QPushButton)

import hou

from ..notification import notify
from ..widgets import Slider
from .utils import versionByTypeName, nextVersionTypeName, incrementHDAVersion


class NewVersionDialog(QDialog):
    def __init__(self, node, parent=None):
        super(NewVersionDialog, self).__init__(parent, Qt.Window)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

        self.setWindowTitle('TDK: New HDA Version')
        self.setWindowIcon(hou.qt.Icon('BUTTONS_multi_insertbefore', 32, 32))

        # Data
        self.node = node
        self.src_version = versionByTypeName(node.type().name())

        # Layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)

        form_layout = QFormLayout()
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(4)
        form_layout.setHorizontalSpacing(8)
        main_layout.addLayout(form_layout)

        # Source
        src_node_label = QLabel(node.path())
        form_layout.addRow('Source Node', src_node_label)

        src_name_label = QLabel(self.node.type().name())
        form_layout.addRow('Source Name', src_name_label)

        # Component
        self.comp_slider = Slider(Qt.Horizontal)
        self.comp_slider.setMaximum(max(3, self.src_version.count('.')))
        self.comp_slider.valueChanged.connect(self._updateDestFields)
        form_layout.addRow('Component', self.comp_slider)

        # Destination
        self.dst_name_label = QLabel()
        form_layout.addRow('Dest Name', self.dst_name_label)

        self.use_original_file_toggle = QCheckBox('Use original file')
        self.use_original_file_toggle.stateChanged.connect(self._updateDestFields)
        form_layout.addWidget(self.use_original_file_toggle)

        self.dst_file_path = QLabel()
        form_layout.addRow('Dest File Path', self.dst_file_path)

        self._updateDestFields()

        spacer = QSpacerItem(0, 0, QSizePolicy.Ignored, QSizePolicy.Expanding)
        main_layout.addSpacerItem(spacer)

        increment_button = QPushButton('Increment')
        increment_button.clicked.connect(self._increment)
        main_layout.addWidget(increment_button)

    def _updateDestFields(self):
        new_type_name = nextVersionTypeName(self.node.type().name(), self.comp_slider.value())
        self.dst_name_label.setText(new_type_name)

        hda_file_path = self.node.type().definition().libraryFilePath()

        if self.use_original_file_toggle.isChecked():
            dst_file_path = hda_file_path
        else:
            src_location = os.path.dirname(hda_file_path)
            dst_file_name = new_type_name.replace(':', '_').replace('.', '_') + '.hda'
            dst_file_path = os.path.join(src_location, dst_file_name).replace('\\', '/')
        self.dst_file_path.setText(dst_file_path)

    def _increment(self):
        incrementHDAVersion(self.node, self.comp_slider.value(), self.use_original_file_toggle.isChecked())
        notify('HDA version successfully incremented')
        self.accept()


def showNewVersionDialog(**kwargs):
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

    window = NewVersionDialog(nodes[0], hou.qt.mainWindow())
    window.show()
