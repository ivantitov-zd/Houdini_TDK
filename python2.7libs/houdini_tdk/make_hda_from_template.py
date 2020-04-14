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

from .find_icon import FindIconDialog


def makeNewHDAFromTemplateNode(template_node, label, name=None, namespace=None, icon=None,
                               sections=None, version='1.0', location='$HOUDINI_USER_PREF_DIR/otls'):
    template_node_type = template_node.type()
    if template_node_type.name() != 'tdk::template':
        raise TypeError

    location = hou.expandString(location)
    if not os.path.exists(location) or not os.path.isdir(location):
        raise IOError

    new_type_name = ''

    if namespace:
        new_type_name += namespace.replace(' ', '_').lower() + '::'

    if name:
        new_type_name += name.replace(' ', '_').lower()
    else:
        new_type_name += label.replace(' ', '_').lower()

    new_type_name += '::'

    if version:
        new_type_name += version
    else:
        new_type_name += '1.0'

    template_def = template_node_type.definition()

    new_hda_file_name = new_type_name.replace(':', '_').replace('.', '_') + '.hda'
    new_hda_file_path = os.path.join(location, new_hda_file_name).replace('\\', '/')
    template_def.copyToHDAFile(new_hda_file_path, new_type_name)

    new_def = hou.hda.definitionsInFile(new_hda_file_path)[0]

    new_def.setDescription(label)

    if icon:
        new_def.setIcon(icon)

    tools = new_def.sections()['Tools.shelf']
    content = tools.contents()
    sections = sections or 'Digital Assets'
    try:
        content = content[:content.index('<toolSubmenu>') + len('<toolSubmenu>')] + \
                  sections + content[content.index('</toolSubmenu>'):]
        tools.setContents(content)
    except ValueError:
        pass

    return new_def


class IconField(QWidget):
    def __init__(self):
        super(IconField, self).__init__()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.edit = QLineEdit()
        layout.addWidget(self.edit)

        self.pick_icon_button = QPushButton()
        self.pick_icon_button.setToolTip('Pick icon')
        self.pick_icon_button.setFixedSize(24, 24)
        self.pick_icon_button.setIcon(hou.qt.Icon('OBJ_hlight', 16, 16))
        self.pick_icon_button.clicked.connect(self._pickIcon)
        layout.addWidget(self.pick_icon_button)

    def text(self):
        return self.edit.text()

    def _pickIcon(self):
        icon = FindIconDialog.getIconName(self, 'Pick Icon')
        if icon:
            self.edit.setText(icon.replace('.svg', ''))


class LocationField(QWidget):
    def __init__(self, contents=''):
        super(LocationField, self).__init__()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.edit = QLineEdit(contents)
        layout.addWidget(self.edit)

        self.pick_location_button = QPushButton()
        self.pick_location_button.setToolTip('Pick location')
        self.pick_location_button.setFixedSize(24, 24)
        self.pick_location_button.setIcon(hou.qt.Icon('BUTTONS_chooser_folder', 16, 16))
        self.pick_location_button.clicked.connect(self._pickLocation)
        layout.addWidget(self.pick_location_button)

    def text(self):
        return self.edit.text()

    def path(self):
        return hou.expandString(self.edit.text())

    def _pickLocation(self):
        path = QFileDialog.getExistingDirectory(self, 'Pick Location', self.path())
        if path:
            path = hou.text.collapseCommonVars(path, ['$HOUDINI_USER_PREF_DIR', '$HIP', '$JOB'])
            self.edit.setText(path)


class MakeHDAFromTemplateDialog(QDialog):
    def __init__(self, node, parent=None):
        super(MakeHDAFromTemplateDialog, self).__init__(parent)

        # Data
        self.node = node

        self.setWindowTitle('TDK: HDA from Template')
        self.setWindowIcon(hou.qt.Icon('NODEFLAGS_template', 16, 16))
        self.resize(400, 250)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)

        form_layout = QFormLayout()
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(4)
        main_layout.addLayout(form_layout)

        self.location_field = LocationField('$HOUDINI_USER_PREF_DIR/otls')
        form_layout.addRow('Location', self.location_field)

        self.label_field = QLineEdit()
        self.label_field.textChanged.connect(self._onLabelChanged)
        form_layout.addRow('Label', self.label_field)

        self.name_field = QLineEdit()
        self.name_field.textChanged.connect(self._onNameChanged)
        form_layout.addRow('Name', self.name_field)

        self.author_field = QLineEdit()
        self.author_field.textChanged.connect(self._onAuthorChanged)
        form_layout.addRow('Author', self.author_field)

        self.sections = QLineEdit()
        self.sections.textChanged.connect(self._onSectionsChanged)
        form_layout.addRow('Sections', self.sections)

        self.icon_field = IconField()
        form_layout.addRow('Icon', self.icon_field)

        self.version_field = QLineEdit('1.0')
        form_layout.addRow('Version', self.version_field)

        self.install_toggle = QCheckBox('Install new HDA')
        self.install_toggle.setChecked(True)
        form_layout.addWidget(self.install_toggle)

        self.replace_node = QCheckBox('Replace template node')
        self.replace_node.setChecked(True)
        form_layout.addWidget(self.replace_node)
        self.install_toggle.toggled.connect(self.replace_node.setEnabled)

        buttons_layout = QHBoxLayout()
        main_layout.addLayout(buttons_layout)

        spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Ignored)
        buttons_layout.addSpacerItem(spacer)

        ok_button = QPushButton('OK')
        ok_button.clicked.connect(self._onOk)
        buttons_layout.addWidget(ok_button)

        cancel_button = QPushButton('Cancel')
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)

        self.__label_changed = False
        self.__name_changed = False
        self.__author_changed = False
        self.__sections_changed = False

        user_name = hou.userName()
        self.author_field.setText(user_name)
        self._onAuthorChanged(user_name)

    def _onLabelChanged(self, label):
        self.__label_changed = True
        if not self.__name_changed:
            self.name_field.blockSignals(True)
            self.name_field.setText(label.lower().replace(' ', '_'))
            self.name_field.blockSignals(False)

    def _onNameChanged(self, name):
        self.__name_changed = True
        if not self.__label_changed:
            self.label_field.blockSignals(True)
            self.label_field.setText(name.replace('_', ' ').title())
            self.label_field.blockSignals(False)

    def _onAuthorChanged(self, author):
        self.__author_changed = True
        if not self.__sections_changed:
            self.sections.blockSignals(True)
            self.sections.setText(author.replace('_', ' ').title())
            self.sections.blockSignals(False)

    def _onSectionsChanged(self, sections):
        self.__sections_changed = True
        if not self.__author_changed:
            self.author_field.blockSignals(True)
            if ',' in sections:
                section = sections.split(',')[0].strip()
            else:
                section = sections.strip()
            self.author_field.setText(section.replace('_', ' ').title())
            self.author_field.blockSignals(False)

    def _onOk(self):
        if self.node:
            definition = makeNewHDAFromTemplateNode(self.node,
                                                    self.label_field.text(),
                                                    self.name_field.text(),
                                                    self.author_field.text(),
                                                    self.icon_field.text(),
                                                    self.sections.text(),
                                                    self.version_field.text(),
                                                    self.location_field.path())
            if self.install_toggle.isChecked():
                hou.hda.installFile(definition.libraryFilePath())
                if self.replace_node.isChecked():
                    self.node.changeNodeType(definition.nodeTypeName(),
                                             keep_network_contents=False)
        self.accept()


def showMakeHDAFromTemplateDialog(**kwargs):
    if 'node' in kwargs:
        nodes = kwargs['node'],
    else:
        nodes = hou.selectedNodes()
    if not nodes:
        raise hou.Error('No node selected')
    elif len(nodes) > 1:
        raise hou.Error('Too much nodes selected')
    elif nodes[0].type().name() != 'tdk::template':
        raise hou.Error('Node is not TDK Template')
    window = MakeHDAFromTemplateDialog(nodes[0], hou.qt.mainWindow())
    window.show()
