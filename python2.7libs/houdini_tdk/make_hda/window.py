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
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *

    Signal = pyqtSignal
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *

import hou

from .. import ui
from .. import hda
from ..widgets import InputField, LocationField, IconField, ColorField, NodeShapeField
from ..notification import notify
from ..icon_list import standardIconExists
from ..utils import houdiniColorFromQColor, qColorFromHoudiniColor


class MakeHDADialog(QDialog):
    def __init__(self, parent=hou.qt.mainWindow()):
        super(MakeHDADialog, self).__init__(parent)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

        self.resize(400, 250)

        main_layout = QGridLayout(self)
        main_layout.setContentsMargins(8, 4, 6, 4)
        main_layout.setSpacing(4)

        self.location_field_label = QLabel('Location')
        main_layout.addWidget(self.location_field_label, 0, 0)

        self.location_field = LocationField()
        main_layout.addWidget(self.location_field, 0, 1)

        self.use_source_file_toggle = QCheckBox('Use source file')
        self.use_source_file_toggle.toggled.connect(self.location_field.setDisabled)
        main_layout.addWidget(self.use_source_file_toggle, 1, 0, 1, -1)

        self.label_field_label = QLabel('Label')
        main_layout.addWidget(self.label_field_label, 2, 0)

        self.label_field = InputField()
        self.label_field.textChanged.connect(self._onLabelChanged)
        main_layout.addWidget(self.label_field, 2, 1)

        self.name_field_label = QLabel('Name')
        main_layout.addWidget(self.name_field_label, 3, 0)

        self.name_field = InputField()
        self.name_field.textChanged.connect(self._onNameChanged)
        main_layout.addWidget(self.name_field, 3, 1)

        self.namespace_field_label = QLabel('Namespace')
        main_layout.addWidget(self.namespace_field_label, 4, 0)

        self.namespace_field = InputField()
        self.namespace_field.textChanged.connect(self._onNamespaceChanged)
        main_layout.addWidget(self.namespace_field, 4, 1)

        self.sections_label = QLabel('Sections')
        main_layout.addWidget(self.sections_label, 5, 0)

        self.sections = InputField()
        self.sections.textChanged.connect(self._onSectionsChanged)
        main_layout.addWidget(self.sections, 5, 1)

        self.version_field_label = QLabel('Version')
        main_layout.addWidget(self.version_field_label, 6, 0)

        self.version_field = InputField('1.0')
        main_layout.addWidget(self.version_field, 6, 1)

        self.icon_field_label = QLabel('Icon')
        main_layout.addWidget(self.icon_field_label, 7, 0)

        self.icon_field = IconField()
        main_layout.addWidget(self.icon_field, 7, 1)

        self.color_field_label = QLabel('Color')
        main_layout.addWidget(self.color_field_label, 8, 0)

        self.color_field = ColorField()
        main_layout.addWidget(self.color_field, 8, 1)

        self.shape_field_label = QLabel('Shape')
        main_layout.addWidget(self.shape_field_label, 9, 0)

        self.shape_field = NodeShapeField()
        main_layout.addWidget(self.shape_field, 9, 1)

        self.inherit_network_toggle = QCheckBox('Inherit network')
        self.inherit_network_toggle.setChecked(True)
        main_layout.addWidget(self.inherit_network_toggle, 10, 0, 1, -1)

        self.inherit_parm_template_group_toggle = QCheckBox('Inherit parameters')
        self.inherit_parm_template_group_toggle.setChecked(True)
        main_layout.addWidget(self.inherit_parm_template_group_toggle, 11, 0, 1, -1)

        self.install_toggle = QCheckBox('Install new HDA')
        self.install_toggle.setChecked(True)
        main_layout.addWidget(self.install_toggle, 12, 0, 1, -1)

        self.replace_node_toggle = QCheckBox('Replace template node')
        self.replace_node_toggle.setChecked(True)
        self.install_toggle.toggled.connect(self.replace_node_toggle.setEnabled)
        main_layout.addWidget(self.replace_node_toggle, 13, 0, 1, -1)

        self.open_type_properties_toggle = QCheckBox('Open type properties')
        self.open_type_properties_toggle.setChecked(True)
        self.install_toggle.toggled.connect(self.open_type_properties_toggle.setEnabled)
        main_layout.addWidget(self.open_type_properties_toggle, 14, 0, 1, -1)

        spacer = QSpacerItem(0, 0, QSizePolicy.Ignored, QSizePolicy.Expanding)
        main_layout.addItem(spacer, 15, 0, 1, -1)

        buttons_layout = QHBoxLayout()
        main_layout.addLayout(buttons_layout, 16, 0, 1, -1)

        spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Ignored)
        buttons_layout.addSpacerItem(spacer)

        self.ok_button = QPushButton('OK')
        self.ok_button.clicked.connect(self.accept)
        buttons_layout.addWidget(self.ok_button)

        self.cancel_button = QPushButton('Cancel')
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_button)

        self._label_changed = False
        self._name_changed = False
        self._author_changed = False
        self._sections_changed = False

    def setWindowTitle(self, text):
        super(MakeHDADialog, self).setWindowTitle('TDK: ' + text)

    def setAllFieldsHidden(self, hide=True):
        self.location_field_label.setHidden(hide)
        self.location_field.setHidden(hide)
        self.label_field_label.setHidden(hide)
        self.label_field.setHidden(hide)
        self.name_field_label.setHidden(hide)
        self.name_field.setHidden(hide)
        self.namespace_field_label.setHidden(hide)
        self.namespace_field.setHidden(hide)
        self.sections_label.setHidden(hide)
        self.sections.setHidden(hide)
        self.icon_field_label.setHidden(hide)
        self.icon_field.setHidden(hide)
        self.version_field_label.setHidden(hide)
        self.version_field.setHidden(hide)
        self.color_field_label.setHidden(hide)
        self.color_field.setHidden(hide)
        self.shape_field_label.setHidden(hide)
        self.shape_field.setHidden(hide)

    def setAllOptionsHidden(self, hide=True):
        self.inherit_network_toggle.setHidden(hide)
        self.inherit_parm_template_group_toggle.setHidden(hide)
        self.install_toggle.setHidden(hide)
        self.replace_node_toggle.setHidden(hide)
        self.open_type_properties_toggle.setHidden(hide)

    def setAllFieldsDisabled(self, disable=True):
        self.location_field.setDisabled(disable)
        self.label_field.setDisabled(disable)
        self.name_field.setDisabled(disable)
        self.namespace_field.setDisabled(disable)
        self.sections.setDisabled(disable)
        self.icon_field.setDisabled(disable)
        self.version_field.setDisabled(disable)
        self.color_field.setDisabled(disable)
        self.shape_field.setDisabled(disable)

    def setAllOptionsDisabled(self, disable=True):
        self.inherit_network_toggle.setDisabled(disable)
        self.inherit_parm_template_group_toggle.setDisabled(disable)
        self.install_toggle.setDisabled(disable)
        self.replace_node_toggle.setDisabled(disable)
        self.open_type_properties_toggle.setDisabled(disable)

    def setAllOptionsChecked(self, check=True):
        self.inherit_network_toggle.setChecked(check)
        self.inherit_parm_template_group_toggle.setChecked(check)
        self.install_toggle.setChecked(check)
        self.replace_node_toggle.setChecked(check)
        self.open_type_properties_toggle.setChecked(check)

    def fillFromNodeType(self, node_type, inherit_meta=False):
        tdk_template_used = node_type.name().startswith('tdk::template')

        _, namespace, name, version = node_type.nameComponents()

        # Label
        if inherit_meta:
            label = node_type.description()
            self.label_field.setText(label)

        # Namespace
        if inherit_meta:
            self.namespace_field.setText(namespace)
        else:
            if tdk_template_used:
                namespace = hou.userName()
            else:
                namespace = namespace or hou.userName()
            namespace = namespace.replace('_', ' ').title()
            self.namespace_field.setText(namespace)

        # Version
        if inherit_meta:
            self.version_field.setText(version)
        else:
            self.version_field.setText('1.0')

        # Sections
        if inherit_meta:
            pass

        # Icon
        if not tdk_template_used:
            icon_name = node_type.icon()
            if standardIconExists(icon_name):
                self.icon_field.setText(icon_name)

        # Color
        if inherit_meta:
            color = qColorFromHoudiniColor(node_type.defaultColor())
            self.color_field.setColor(color)

        # Shape
        if inherit_meta:
            shape = node_type.defaultShape()
            self.shape_field.setShape(shape)

    def fillFromDefinition(self, definition, inherit_meta=False):
        self.fillFromNodeType(definition.nodeType(), inherit_meta)

    def fillFromNode(self, node, inherit_meta=False):
        self.fillFromNodeType(node.type(), inherit_meta)

        tdk_template_used = node.type().name().startswith('tdk::template')

        # Label
        if tdk_template_used or not inherit_meta:
            label = node.name()
            label = label.replace('_', ' ').title()
            self.label_field.setText(label)

        # Color
        if not inherit_meta:
            color = qColorFromHoudiniColor(node.color())
            self.color_field.setColor(color)

        # Shape
        if not inherit_meta and 'nodeshape' in node.userDataDict():
            shape = node.userData('nodeshape')
            self.shape_field.setShape(shape)

    def fillFromSource(self, source, inherit_meta=False):
        if isinstance(source, hou.Node):
            self.fillFromNode(source, inherit_meta)
        elif isinstance(source, hou.NodeType):
            self.fillFromNodeType(source, inherit_meta)
        elif isinstance(source, hou.HDADefinition):
            self.fillFromDefinition(source, inherit_meta)
        else:
            raise TypeError('<source> can be hou.Node, hou.NodeType or hou.HDADefinition.')

    def _onLabelChanged(self, label):
        self._label_changed = True
        if not self._name_changed:
            self.name_field.blockSignals(True)
            self.name_field.setText(label.lower().replace(' ', '_'))
            self.name_field.blockSignals(False)

    def _onNameChanged(self, name):
        self._name_changed = True
        if not self._label_changed:
            self.label_field.blockSignals(True)
            self.label_field.setText(name.replace('_', ' ').title())
            self.label_field.blockSignals(False)

    def _onNamespaceChanged(self, author):
        self._author_changed = True
        if not self._sections_changed:
            self.sections.blockSignals(True)
            self.sections.setText(author.replace('_', ' ').title())
            self.sections.blockSignals(False)

    def _onSectionsChanged(self, sections):
        self._sections_changed = True
        if not self._author_changed:
            self.namespace_field.blockSignals(True)
            if ',' in sections:
                section = sections.split(',')[0].strip()
            else:
                section = sections.strip()
            self.namespace_field.setText(section.replace('_', ' ').title())
            self.namespace_field.blockSignals(False)

    @staticmethod
    def makeHDA(source):
        window = MakeHDADialog()
        window.setWindowTitle('Make HDA')
        window.setWindowIcon(ui.icon('NODEFLAGS_template', 32))

        if isinstance(source, hou.Node):
            if source.type().category() in (hou.objNodeTypeCategory(), hou.sopNodeTypeCategory()):
                if source.type().name() in ('pythonscript', 'python'):
                    window.inherit_network_toggle.setHidden(True)
                    window.inherit_parm_template_group_toggle.setHidden(True)
            elif source.type().category() == hou.vopNodeTypeCategory() and source.type().name() == 'inline':
                window.inherit_network_toggle.setHidden(True)
                window.inherit_parm_template_group_toggle.setHidden(True)
        elif isinstance(source, hou.NodeType):
            window.setAllOptionsHidden()
            window.setAllOptionsChecked(False)
            window.install_toggle.show()
            window.install_toggle.setChecked(True)
            window.open_type_properties_toggle.show()
            window.open_type_properties_toggle.setChecked(True)
        elif isinstance(source, hou.HDADefinition):
            window.setAllOptionsHidden()
            window.setAllOptionsChecked(False)
            window.install_toggle.show()
            window.install_toggle.setChecked(True)
            window.open_type_properties_toggle.show()
            window.open_type_properties_toggle.setChecked(True)

        window.fillFromSource(source)

        if not window.exec_():
            return

        color = window.color_field.color()
        shape = window.shape_field.shape()
        definition = hda.makeHDA(source,
                                 window.label_field.text(),
                                 window.name_field.text(),
                                 window.namespace_field.text(),
                                 window.icon_field.text(),
                                 window.sections.text(),
                                 window.version_field.text(),
                                 window.location_field.path(),
                                 window.inherit_network_toggle.isChecked(),
                                 window.inherit_parm_template_group_toggle.isChecked(),
                                 color,
                                 shape)
        if window.install_toggle.isChecked():
            hou.hda.installFile(definition.libraryFilePath())

            if isinstance(source, hou.Node):
                node = source
            else:
                node = None

            if node and window.replace_node_toggle.isChecked():
                node = node.changeNodeType(definition.nodeTypeName(), keep_network_contents=False)
                node.setCurrent(True, True)

                if color:
                    definition.nodeType().setDefaultColor(houdiniColorFromQColor(color))

                if shape:
                    definition.nodeType().setDefaultShape(shape)

            if window.open_type_properties_toggle.isChecked():
                if node and window.replace_node_toggle.isChecked():
                    hou.ui.openTypePropertiesDialog(node)
                else:
                    hou.ui.openTypePropertiesDialog(definition.nodeType())

    @staticmethod
    def copyHDA(source):
        window = MakeHDADialog()
        window.setWindowTitle('Copy HDA')
        window.setWindowIcon(ui.icon('BUTTONS_copy', 32))

        window.setAllFieldsDisabled(True)
        window.location_field.setEnabled(True)
        window.use_source_file_toggle.hide()

        window.color_field_label.hide()
        window.color_field.hide()
        window.shape_field_label.hide()
        window.shape_field.hide()

        window.setAllOptionsDisabled()
        window.setAllOptionsHidden()
        window.install_toggle.show()
        window.install_toggle.setEnabled(True)
        window.install_toggle.setChecked(False)
        window.open_type_properties_toggle.show()

        window.fillFromSource(source)

        if not window.exec_():
            return

        hda.copyHDA(source, window.location_field.path())

    @staticmethod
    def moveHDA(source):
        window = MakeHDADialog()
        window.setWindowTitle('Move HDA')
        window.setWindowIcon(ui.icon('BUTTONS_move_to_right', 32))

        window.setAllFieldsDisabled(True)
        window.location_field.setEnabled(True)
        window.use_source_file_toggle.hide()

        window.color_field_label.hide()
        window.color_field.hide()
        window.shape_field_label.hide()
        window.shape_field.hide()

        window.setAllOptionsDisabled()
        window.setAllOptionsHidden()
        window.install_toggle.show()
        window.install_toggle.setEnabled(True)
        window.install_toggle.setChecked(False)
        window.open_type_properties_toggle.show()

        window.fillFromSource(source)

        if not window.exec_():
            return

        hda.moveHDA(source, window.location_field.path())


def showMakeHDADialog(**kwargs):
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

    node = nodes[0]
    has_definition = node.type().definition() is not None
    subnetwork = node.type().name() == 'subnet'
    python_source = node.type().category() in (hou.objNodeTypeCategory(), hou.sopNodeTypeCategory()) \
                    and node.type().name() in ('pythonscript', 'python')
    inline_vex = node.type().category() == hou.vopNodeTypeCategory() and node.type().name() == 'inline'

    if not (has_definition or subnetwork or python_source or inline_vex):
        notify('Node cannot be used as a template', hou.severityType.Error)
        return

    MakeHDADialog.makeHDA(nodes[0])
