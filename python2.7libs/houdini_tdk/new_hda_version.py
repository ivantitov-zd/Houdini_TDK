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


class NewVersionDialog(QWidget):
    def __init__(self, node, parent=None):
        super(NewVersionDialog, self).__init__(parent, Qt.Window)

        self.setWindowTitle('New HDA Version')

        # Data
        self.node = node
        hda_name = node.type().name()
        self.split_count = hda_name.count('::')
        if self.split_count == 2:
            self.curr_version = hda_name.split('::')[-1]
        elif self.split_count == 1 and hda_name[-1].isdigit():
            self.curr_version = hda_name.split('::')[-1]
        else:
            self.curr_version = '1.0'
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
        values = [int(value) for value in self.curr_version.split('.')]
        values[self.comp_slider.value()] += 1
        self.next_version = '.'.join(str(value) for value in values)
        self.next_version_label.setText('Next Version ' + self.next_version)

    def _increment(self):
        node_type = self.node.type()
        name = node_type.name()
        definition = node_type.definition()
        if self.split_count == 2:
            new_name = '::'.join(name.split('::')[:2]) + '::' + self.next_version
        elif self.split_count == 1 and name[-1].isdigit():
            new_name = '::'.join(name.split('::')[0]) + '::' + self.next_version
        else:
            new_name = name + '::' + self.next_version
        file = definition.libraryFilePath()
        ext = os.path.splitext(file)[-1]
        new_file_name = new_name.replace(':', '_').replace('.', '_') + ext
        new_file = os.path.join(os.path.dirname(file), new_file_name).replace('\\', '/')
        definition.copyToHDAFile(new_file, new_name)
        hou.hda.installFile(new_file)
        self.node.changeNodeType(new_name, keep_network_contents=False)
        hou.ui.setStatusMessage('HDA version successfully incremented',
                                hou.severityType.ImportantMessage)


def incrementHdaVersion(**kwargs):
    nodes = hou.selectedNodes()
    if not nodes:
        raise hou.Error('No node selected')
    elif len(nodes) > 1:
        raise hou.Error('Too much nodes selected')
    window = NewVersionDialog(nodes[0], hou.qt.mainWindow())
    window.show()
