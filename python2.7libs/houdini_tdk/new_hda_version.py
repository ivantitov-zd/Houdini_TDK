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
    values[component] += 1
    values = values[:component + 1] + [0] * (len(values) - component - 1)
    return '.'.join(str(value) for value in values)


def incrementHDAVersion(node, component):
    node_type = node.type()
    name = node_type.name()
    version = nextVersion(versionByTypeName(name), component)
    split_count = name.count('::')
    definition = node_type.definition()
    if split_count == 2:
        new_type_name = '::'.join(name.split('::')[:2])
    elif split_count == 1 and name[-1].isdigit():
        new_type_name = name.split('::')[0]
    else:
        new_type_name = name
    new_type_name += '::' + version
    file = definition.libraryFilePath()
    ext = os.path.splitext(file)[-1]
    new_file_name = new_type_name.replace(':', '_').replace('.', '_') + ext
    new_file = os.path.join(os.path.dirname(file), new_file_name).replace('\\', '/')
    print(new_file)
    definition.copyToHDAFile(new_file, new_type_name)
    hou.hda.installFile(new_file)
    new_definition = hou.hda.definitionsInFile(new_file)[0]
    new_definition.updateFromNode(node)
    node.changeNodeType(new_type_name, keep_network_contents=False)


class NewVersionDialog(QWidget):
    def __init__(self, node, parent=None):
        super(NewVersionDialog, self).__init__(parent, Qt.Window)

        self.setWindowTitle('New HDA Version')

        # Data
        self.node = node
        self.curr_version = versionByTypeName(node.type().name())
        self.next_version = None

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Current
        curr_node_label = QLabel('Current Node ' + node.path())
        layout.addWidget(curr_node_label)

        curr_version_label = QLabel('Current Version ' + self.curr_version)
        layout.addWidget(curr_version_label)

        # Component
        self.comp_slider = QSlider(Qt.Horizontal)
        self.comp_slider.setMaximum(self.curr_version.count('.'))
        self.comp_slider.valueChanged.connect(self.updateNextVersion)
        layout.addWidget(self.comp_slider)

        # Next
        self.next_version_label = QLabel()
        self.updateNextVersion()
        layout.addWidget(self.next_version_label)

        spacer = QSpacerItem(0, 0, QSizePolicy.Ignored, QSizePolicy.Expanding)
        layout.addSpacerItem(spacer)

        increment_button = QPushButton('Increment')
        increment_button.clicked.connect(self._increment)
        layout.addWidget(increment_button)

    def updateNextVersion(self):
        self.next_version = nextVersion(self.curr_version, self.comp_slider.value())
        self.next_version_label.setText('Next Version ' + self.next_version)

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
