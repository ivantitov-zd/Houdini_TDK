"""
Tool Development Kit for SideFX Houdini
Copyright (C) 2020  Ivan Titov

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

from __future__ import print_function

import os

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


def versionByTypeName(name):
    split_count = name.count('::')
    if split_count == 2:
        version = name.split('::')[-1]
    elif split_count == 1 and name[-1].isdigit():
        version = name.split('::')[-1]
    else:
        version = '1.0'
    return version


def nextVersion(version, component=0):
    if isinstance(version, basestring):
        values = [int(value) for value in version.split('.')]
    elif isinstance(version, (list, tuple)):
        values = version
    else:
        raise TypeError
    try:
        values[component] += 1
    except IndexError:
        values += [0] * (component - len(values)) + [1]
    values = values[:component + 1] + [0] * (len(values) - component - 1)
    return '.'.join(str(value) for value in values)


def nextVersionTypeName(name, component):
    next_version = nextVersion(versionByTypeName(name), component)
    split_count = name.count('::')
    if split_count == 2:
        new_type_name = '::'.join(name.split('::')[:2])
    elif split_count == 1 and name[-1].isdigit():
        new_type_name = name.split('::')[0]
    else:
        new_type_name = name
    new_type_name += '::' + next_version
    return new_type_name


def incrementHDAVersion(node, component):
    node_type = node.type()
    name = node_type.name()

    new_type_name = nextVersionTypeName(name, component)

    definition = node_type.definition()
    file = definition.libraryFilePath()
    ext = os.path.splitext(file)[-1]
    new_file_name = new_type_name.replace(':', '_').replace('.', '_') + ext
    new_file = os.path.join(os.path.dirname(file), new_file_name).replace('\\', '/')
    definition.copyToHDAFile(new_file, new_type_name)

    hou.hda.installFile(new_file)
    new_definition = hou.hda.definitionsInFile(new_file)[0]

    new_definition.updateFromNode(node)

    node.changeNodeType(new_type_name, keep_network_contents=False)


class NewVersionDialog(QDialog):
    def __init__(self, node, parent=None):
        super(NewVersionDialog, self).__init__(parent, Qt.Window)

        self.setWindowTitle('TDK: New HDA Version')
        self.setWindowIcon(hou.qt.Icon('BUTTONS_list_add', 16, 16))

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
        self.comp_slider = QSlider(Qt.Horizontal)
        self.comp_slider.setMaximum(max(3, self.src_version.count('.')))
        self.comp_slider.valueChanged.connect(self._updateDestFields)
        form_layout.addRow('Component', self.comp_slider)

        # Destination
        self.dst_name_label = QLabel()
        form_layout.addRow('Dest Name', self.dst_name_label)

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
        src_location = os.path.dirname(self.node.type().definition().libraryFilePath())
        dst_file_path = os.path.join(src_location, new_type_name.replace(':', '_').replace('.', '_')).replace('\\', '/') + '.hda'
        self.dst_file_path.setText(dst_file_path)

    def _increment(self):
        incrementHDAVersion(self.node, self.comp_slider.value())
        hou.ui.setStatusMessage('HDA version successfully incremented',
                                hou.severityType.ImportantMessage)
        self.close()


def showNewVersionDialog(**kwargs):
    if 'node' in kwargs:
        nodes = kwargs['node'],
    else:
        nodes = hou.selectedNodes()
    if not nodes:
        raise hou.Error('No node selected')
    elif len(nodes) > 1:
        raise hou.Error('Too much nodes selected')
    window = NewVersionDialog(nodes[0], hou.qt.mainWindow())
    window.show()
