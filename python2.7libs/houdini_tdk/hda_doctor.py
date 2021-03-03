"""
Tool Development Kit for SideFX Houdini
Copyright (C) 2021  Ivan Titov

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

import getpass

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

WARNING_ICON = hou.qt.Icon('STATUS_warning', 16, 16)
WEAK_WARNING_ICON = QIcon(WARNING_ICON.pixmap(QSize(16, 16), QIcon.Disabled, QIcon.On))
ERROR_ICON = hou.qt.Icon('STATUS_error', 16, 16)

DEFINITION_ICON = hou.qt.Icon('MISC_digital_asset', 16, 16)
PARAMETERS_ICON = hou.qt.Icon('PANETYPES_parameters', 16, 16)
NETWORK_ICON = hou.qt.Icon('PANETYPES_network', 16, 16)


class Scope:
    Any = 0b1111
    DefinitionName = 1
    Definition = 2
    Parameters = 4
    Network = 8


class SeverityType:
    Any = 0b111
    WeakWarning = 1
    Warning = 2
    Error = 4


class FixVariant:
    def __init__(self, text, description):
        self.text = text
        self.description = description


class Inspection(object):
    _inspections = []

    @staticmethod
    def addInspection(inspection):
        Inspection._inspections.append(inspection)

    @staticmethod
    def allInspections():
        return tuple(Inspection._inspections)

    @staticmethod
    def inspections(scope=Scope.Any, severity=SeverityType.Any):
        for inspection in Inspection._inspections:
            if inspection.scope() & scope and inspection.severity() & severity:
                yield inspection

    @classmethod
    def name(cls):
        raise NotImplementedError

    @classmethod
    def description(cls):
        raise NotImplementedError

    @classmethod
    def scope(cls):
        raise NotImplementedError

    @classmethod
    def severity(cls):
        raise NotImplementedError

    @classmethod
    def inspect(cls, definition):
        raise NotImplementedError

    @classmethod
    def canBeFixedAutomatically(cls):
        return False

    @classmethod
    def canBeFixed(cls):
        return cls.canBeFixedAutomatically()

    @classmethod
    def fixVariants(cls, definition):
        raise NotImplementedError

    @classmethod
    def fix(cls, definition, variant=0, user_value=None):
        raise NotImplementedError


def registerInspection(cls):
    Inspection.addInspection(cls)
    return cls


class HDANameInspection(Inspection):
    @classmethod
    def scope(cls):
        return Scope.DefinitionName

    @classmethod
    def inspect(cls, namespace, name, version):
        raise NotImplementedError

    @classmethod
    def fixVariants(cls, namespace, name, version):
        raise NotImplementedError

    @classmethod
    def fix(cls, namespace, name, version, variant=0, user_value=None):
        raise NotImplementedError


class ParmInspection(Inspection):
    @classmethod
    def scope(cls):
        return Scope.Parameters

    @classmethod
    def inspect(cls, parm):
        raise NotImplementedError

    @classmethod
    def fixVariants(cls, parm):
        raise NotImplementedError

    @classmethod
    def fix(cls, parm, variant=0, user_value=None):
        raise NotImplementedError


@registerInspection
class DefNamespaceMissing(HDANameInspection):
    @classmethod
    def name(cls):
        return 'Missing HDA namespace'

    @classmethod
    def description(cls):
        return 'This inspection detects missing HDA namespace.'

    @classmethod
    def severity(cls):
        return SeverityType.Warning

    @classmethod
    def inspect(cls, namespace, name, version):
        return not namespace.strip()

    @classmethod
    def canBeFixed(cls):
        return True

    @staticmethod
    def _namespaceFromUserName():
        return getpass.getuser().replace(' ', '_').lower()

    @classmethod
    def fixVariants(cls, namespace, name, version):
        return [
            FixVariant(cls._namespaceFromUserName(), 'User name from OS.'),
            None
        ]

    @classmethod
    def fix(cls, namespace, name, version, variant=0, user_value=None):
        if variant == 0:
            namespace = cls._namespaceFromUserName()
        elif variant == 1 and user_value and isinstance(user_value, str):
            namespace = user_value
        else:
            raise ValueError

        fixed_name = '::'.join([namespace, name, version])
        return fixed_name


@registerInspection
class DefNamespaceWrongCase(HDANameInspection):
    @classmethod
    def name(cls):
        return 'Wrong HDA namespace case'

    @classmethod
    def description(cls):
        return 'This inspection detects wrong HDA namespace case.'

    @classmethod
    def severity(cls):
        return SeverityType.Warning

    @classmethod
    def inspect(cls, namespace, name, version):
        if not namespace:
            return

        for char in namespace:
            if char.isalpha() and char.isupper():
                return True

        return False

    @classmethod
    def canBeFixedAutomatically(cls):
        return True

    @classmethod
    def fixVariants(cls, namespace, name, version):
        return [
            FixVariant(namespace.lower(), 'Case lowered.')
        ]

    @classmethod
    def fix(cls, namespace, name, version, variant=0, user_value=None):
        if variant == 0:
            namespace = cls._userName()
        elif variant == 1 and user_value and isinstance(user_value, str):
            namespace = user_value
        else:
            raise ValueError  # Todo: reflect current inspection in message

        fixed_name = '::'.join([namespace, name, version])
        return fixed_name


@registerInspection
class DefNameWrongCase(HDANameInspection):
    @classmethod
    def name(cls):
        return 'Wrong HDA name case'

    @classmethod
    def description(cls):
        return 'This inspection detects wrong HDA name case.'

    @classmethod
    def severity(cls):
        return SeverityType.Warning

    @classmethod
    def inspect(cls, namespace, name, version):
        if not name:
            return

        for char in name:
            if char.isalpha() and char.isupper():
                return True

        return False

    @classmethod
    def canBeFixedAutomatically(cls):
        return True

    @classmethod
    def fixVariants(cls, namespace, name, version):
        return [
            FixVariant(name.lower(), 'Case lowered.')
        ]

    @classmethod
    def fix(cls, namespace, name, version, variant=0, user_value=None):
        return '::'.join([namespace, name.lower(), version])


@registerInspection
class DefVersionMissing(HDANameInspection):
    @classmethod
    def name(cls):
        return 'Missing HDA version'

    @classmethod
    def description(cls):
        return 'This inspection detects missing HDA version.'

    @classmethod
    def severity(cls):
        return SeverityType.WeakWarning

    @classmethod
    def inspect(cls, namespace, name, version):
        return not version.strip()

    @classmethod
    def canBeFixedAutomatically(cls):
        return True

    @classmethod
    def fixVariants(cls, definition):
        return [
            FixVariant('Set 1.0', 'Default first version.'),
            None
        ]

    @classmethod
    def fix(cls, namespace, name, version, variant=0, user_value=None):
        if variant == 0:
            version = '1.0'
        elif variant == 1 and user_value:
            version = user_value
        else:
            raise ValueError

        return '::'.join([namespace, name, version])


@registerInspection
class DefVersionWrongCase(HDANameInspection):
    @classmethod
    def name(cls):
        return 'Wrong HDA version case'

    @classmethod
    def description(cls):
        return 'Version has characters with wrong case.'

    @classmethod
    def severity(cls):
        return SeverityType.Warning

    @classmethod
    def inspect(cls, namespace, name, version):
        if not version:
            return

        for char in version:
            if char.isalpha() and char.isupper():
                return True

        return False

    @classmethod
    def canBeFixedAutomatically(cls):
        return True

    @classmethod
    def fixVariants(cls, namespace, name, version):
        return [
            FixVariant(version.lower(), 'Case lowered.'),
            None
        ]

    @classmethod
    def fix(cls, namespace, name, version, variant=0, user_value=None):
        return '::'.join([namespace, name, version.lower()])


@registerInspection
class DefLabelMissing(Inspection):
    @classmethod
    def name(cls):
        return 'Missing HDA label'

    @classmethod
    def description(cls):
        return 'This inspection detects missing HDA label.'

    @classmethod
    def scope(cls):
        return Scope.Definition

    @classmethod
    def severity(cls):
        return SeverityType.Warning

    @classmethod
    def inspect(cls, definition):
        return not definition.description().strip()

    @classmethod
    def canBeFixedAutomatically(cls):
        return True

    @staticmethod
    def _newLabelFromHDAName():
        node_type = definition.nodeType()
        _, _, name, _ = node_type.nameComponents()
        return name.replace('_', ' ').title()

    @classmethod
    def fixVariants(cls, definition):
        return [
            FixVariant(cls._newLabelFromHDAName(), 'Label from HDA name.'),
            None
        ]

    @classmethod
    def fix(cls, definition, variant=0, value=None):
        if variant == 0:
            definition.setDescription(cls._newLabelFromHDAName())
        elif variant == 1 and value:  # Todo: Simplify
            definition.setDescription(value)
        else:
            raise ValueError


@registerInspection
class DefIconMissing(Inspection):
    @classmethod
    def name(cls):
        return 'Missing HDA icon'

    @classmethod
    def description(cls):
        return 'This inspection detects missing HDA icon.'

    @classmethod
    def scope(cls):
        return Scope.Definition

    @classmethod
    def severity(cls):
        return SeverityType.WeakWarning

    @classmethod
    def inspect(cls, definition):
        return not bool(definition.icon().strip())

    @classmethod
    def canBeFixed(cls):
        return True

    @classmethod
    def fixVariants(cls, definition):
        return [
            None
        ]

    @classmethod
    def fix(cls, definition, variant=0, user_value=None):
        if user_value:
            definition.setIcon(user_value)
        else:
            raise ValueError


class InspectionsModel(QAbstractItemModel):
    def __init__(self, parent=None):
        super(InspectionsModel, self).__init__(parent)

        self._data = ()
        self.updateData()

    def updateData(self):
        self.beginResetModel()
        self._data = Inspection.allInspections()
        self.endResetModel()

    def parent(self, index):
        return QModelIndex()

    def columnCount(self, parent):
        return 2

    def headerData(self, section, orientation, role):
        if orientation != Qt.Horizontal:
            return

        if role == Qt.DisplayRole:
            return ('Name', 'Description')[section]
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

    def rowCount(self, parent):
        if not parent.isValid():
            return len(self._data)
        else:
            return 0

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            inspection = self._data[row]
            return self.createIndex(row, column, inspection)
        else:
            return QModelIndex()

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemNeverHasChildren

    def data(self, index, role):
        if not index.isValid():
            return

        inspection = self._data[index.row()]

        if index.column() == 0:
            if role == Qt.DisplayRole:
                return inspection.name()
            elif role == Qt.CheckStateRole:
                return Qt.Checked
            elif role == Qt.DecorationRole:
                return {
                    SeverityType.WeakWarning: WEAK_WARNING_ICON,
                    SeverityType.Warning: WARNING_ICON,
                    SeverityType.Error: ERROR_ICON
                }[inspection.severity()]
        elif index.column() == 1:
            if role == Qt.DisplayRole:
                return inspection.description()


class InspectionsView(QTreeView):
    def __init__(self):
        super(InspectionsView, self).__init__()

        header = self.header()
        header.setSectionsMovable(False)
        header.setSectionResizeMode(QHeaderView.ResizeToContents)

        self.setUniformRowHeights(True)

        self.setRootIsDecorated(False)


class AnalysesModel(QAbstractItemModel):
    def __init__(self, parent=None):
        super(AnalysesModel, self).__init__(parent)

        self._data = ([], {}, {})

    def updateData(self, node):
        self.beginResetModel()

        self._data = [], {}, {}
        parts, parms, nodes = self._data

        node_type = node.type()
        definition = node_type.definition()
        if not definition:
            self.endResetModel()
            return
        _, namespace, name, version = node_type.nameComponents()

        for inspection in Inspection.inspections(Scope.DefinitionName):
            if inspection.inspect(namespace, name, version):
                parts.append(inspection)

        for inspection in Inspection.inspections(Scope.Definition):
            if inspection.inspect(definition):
                parts.append(inspection)

        for inspection in Inspection.inspections(Scope.Parameters):
            for parm in node.parms():
                if inspection.inspect(parm):
                    if inspection in parms:
                        parms[inspection].append(parm)
                    else:
                        parms[inspection] = []

        # for inspection in Inspection.inspections(Scope.Network):
        #     pass

        self.endResetModel()

    def hasChildren(self, parent):
        if not parent.isValid():
            return True

        if isinstance(parent.internalPointer(), (list, dict)):
            return True

        return False

    def parent(self, index):
        if not index.isValid():  # Root
            return QModelIndex()

        if isinstance(index.internalPointer(), (list, dict)):
            return QModelIndex()
        else:
            data = index.internalPointer()
            if data in self._data[0]:
                return self.createIndex(0, 0, self._data[0])
            elif data in self._data[1]:
                return self.createIndex(1, 0, self._data[1])
            elif data in self._data[2]:
                return self.createIndex(2, 0, self._data[2])
            else:
                return QModelIndex()

    def columnCount(self, parent):
        return 1

    def rowCount(self, parent):
        if not parent.isValid():  # Level 1
            return 3

        if not parent.parent().isValid():  # Level 2
            row = parent.row()
            if 0 <= row <= 2:
                return len(self._data[row])
            else:
                return 0

        return 0

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():  # Level 1
            return self.createIndex(row, column, self._data[row])
        else:  # Level 2
            data = parent.internalPointer()
            if parent.row() == 0:
                return self.createIndex(row, column, self._data[parent.row()][row])
            elif parent.row() == 1:
                return self.createIndex(row, column,
                                        self._data[parent.row()][tuple(self._data[parent.row()].keys())[row]])
            elif isinstance(data, list):
                return self.createIndex(row, column, data[row])
            else:
                return self.createIndex(row, column, data.keys()[row])

    def flags(self, index):
        if isinstance(index.internalPointer(), Inspection):
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable  # | Qt.ItemIsUserCheckable
        else:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def data(self, index, role):
        if not index.isValid():  # Root
            return

        column = index.column()
        row = index.row()
        data = index.internalPointer()

        if column == 0:
            if isinstance(data, (list, dict)):
                if role == Qt.DisplayRole:
                    return ('Definition', 'Parameters', 'Network')[row]
                elif role == Qt.ToolTipRole:
                    return (
                        'HDA definition-related inspections.',
                        'Parameters-related inspections.',
                        'Nodes-related inspections.'
                    )[row]
                elif role == Qt.DecorationRole:
                    return (DEFINITION_ICON, PARAMETERS_ICON, NETWORK_ICON)[row]
            else:
                if role == Qt.DisplayRole:
                    return data.name()
                elif role == Qt.ToolTipRole:
                    return data.description()
                elif role == Qt.DecorationRole:
                    return {
                        SeverityType.WeakWarning: WEAK_WARNING_ICON,
                        SeverityType.Warning: WARNING_ICON,
                        SeverityType.Error: ERROR_ICON
                    }[data.severity()]
                elif role == Qt.CheckStateRole:
                    return Qt.Checked


class AnalysesView(QTreeView):
    def __init__(self):
        super(AnalysesView, self).__init__()

        header = self.header()
        header.setSectionsMovable(False)
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.hide()

        self.setUniformRowHeights(True)

        self.setRootIsDecorated(False)


class HDADoctorWindow(QWidget):
    def __init__(self, parent=None):
        super(HDADoctorWindow, self).__init__(parent, Qt.Window)

        self.setWindowTitle('HDA Doctor Beta')
        self.setWindowIcon(hou.qt.Icon('SOP_polydoctor', 32, 32))
        self.resize(600, 600)

        # Layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)

        node_layout = QHBoxLayout()
        node_layout.setContentsMargins(0, 0, 0, 0)
        node_layout.setSpacing(4)
        main_layout.addLayout(node_layout)

        # Node Field
        node_field = hou.qt.InputField(hou.qt.InputField.StringType, 1, 'Node')
        node_layout.addWidget(node_field)

        choose_node_button = hou.qt.NodeChooserButton()
        choose_node_button.nodeSelected.connect(lambda node: node_field.setValue(node.path()))
        node_layout.addWidget(choose_node_button)

        # Tabs
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)

        self.analyses_view = AnalysesView()
        self.analyses_model = AnalysesModel()
        choose_node_button.nodeSelected.connect(self.updateData)
        self.analyses_view.setModel(self.analyses_model)
        tab_widget.addTab(self.analyses_view, hou.qt.Icon('VOP_usdprimvarreader', 16, 16), 'Analyses')

        inspections_view = InspectionsView()
        model = InspectionsModel()
        inspections_view.setModel(model)
        tab_widget.addTab(inspections_view, hou.qt.Icon('STATUS_warning', 16, 16), 'Inspections')

    def updateData(self, node):
        self.analyses_model.updateData(node)
        self.analyses_view.expandAll()
