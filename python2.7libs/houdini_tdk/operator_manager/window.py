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

from ..widgets import FilterField
from ..fuzzy_proxy_model import FuzzyProxyModel
from ..utils import openFileLocation
from .model import OperatorManagerLibraryModel, TextRole
from .view import OperatorManagerView

ICON_SIZE = 16


def repackHDA(library_path):
    if not os.path.exists(library_path):
        return

    library_dir, name = os.path.split(library_path)
    temp_repack_path = os.path.join(library_dir, 'temp_' + name.replace('.', '_'))

    try:
        if os.path.isfile(library_path):
            hou.hda.expandToDirectory(library_path, temp_repack_path)
        else:
            hou.hda.collapseFromDirectory(temp_repack_path, library_path)

        backup_library_path = os.path.join(library_dir, 'temp_' + name + '_backup')
        os.rename(library_path, backup_library_path)
    except hou.OperationFailed:
        return
    except OSError:
        os.remove(temp_repack_path)
        return

    try:
        os.rename(temp_repack_path, library_path)
        os.remove(backup_library_path)
    except OSError:
        os.rename(backup_library_path, library_path)
        os.remove(temp_repack_path)
        return

    hou.hda.reloadFile(library_path)


class OperatorManagerWindow(QWidget):
    def __init__(self, parent=hou.qt.mainWindow()):
        super(OperatorManagerWindow, self).__init__(parent, Qt.Window)

        self.setWindowTitle('TDK: Operator Manager')
        self.setWindowIcon(hou.qt.Icon('MISC_digital_asset', 32, 32))
        self.resize(400, 600)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        self.filter_field = FilterField()
        self.filter_field.textChanged.connect(self._onFilterChange)
        layout.addWidget(self.filter_field)

        self.model = OperatorManagerLibraryModel(self)
        self.model.updateData()

        self.filter_proxy_model = FuzzyProxyModel(self, TextRole, TextRole)
        self.filter_proxy_model.setDynamicSortFilter(True)
        # Order is dictated by the weights of the fuzzy match function (bigger = better)
        self.filter_proxy_model.sort(0, Qt.DescendingOrder)
        self.filter_proxy_model.setSourceModel(self.model)

        self.view = OperatorManagerView()
        self.view.setModel(self.filter_proxy_model)
        layout.addWidget(self.view)

        self.__createActions()
        self.__createContextMenus()

    def _onFilterChange(self, pattern):
        """Delivers pattern from filter field to filter proxy model."""
        # Pre-collapse all to speed up live filtering
        self.view.collapseAll()
        self.filter_proxy_model.setPattern(pattern)
        if pattern:
            self.view.expandAll()

    def _onExpand(self):
        """ Expands selected items."""
        for index in self.view.selectedIndexes():
            self.view.expand(index)

    def _onCollapse(self):
        """Collapses selected items."""
        for index in self.view.selectedIndexes():
            self.view.collapse(index)

    def _onExpandAll(self):
        """Expands all items."""
        self.view.expandAll()

    def _onCollapseAll(self):
        """Collapses all items."""
        self.view.collapseAll()

    def _onOpenLocation(self):
        """
        Opens location of the selected library or library of the selected node type.
        Currently, supported single selection only. Multiple selection is ignored.
        """
        if self.view.isSingleSelection():
            index = self.view.selectedIndex()
            openFileLocation(index.data(Qt.UserRole))

    def _onInstall(self):
        """
        Uninstall all node types containing in the selected library from the current Houdini session.
        Currently, supported single selection only. Multiple selection is ignored.
        """
        if self.view.isSingleSelection():
            index = self.view.selectedIndex()
            library_path = index.data(Qt.UserRole)
            hou.hda.installFile(library_path)
            # Todo: Change item state to installed

    def _onUninstall(self):
        """
        Uninstall all node types containing in the selected library from the current Houdini session.
        Currently, supported single selection only. Multiple selection is ignored.
        """
        if self.view.isSingleSelection():
            index = self.view.selectedIndex()
            library_path = index.data(Qt.UserRole)
            hou.hda.uninstallFile(library_path)
            # Todo: Change item state to uninstalled

    def _onReload(self):
        """
        Reload the contents of an HDA file, loading any updated digital asset definitions inside it.
        Currently, supported single selection only. Multiple selection is ignored.
        """
        if self.view.isSingleSelection():
            index = self.view.selectedIndex()
            library_path = index.data(Qt.UserRole)
            hou.hda.reloadFile(library_path)

    def _onReloadAll(self):
        """Reload the HDA files and update node type definitions in the current Houdini session."""
        hou.hda.reloadAllFiles(False)
        self.view.model().updateData()

    def _onRescanAndReloadAll(self):
        """
        Reload the HDA files and update node type definitions in the current Houdini session.
        Houdini will check the hda directories for any new hda files and load them too.
        """
        hou.hda.reloadAllFiles(True)
        self.view.model().updateData()

    def _onMergeWithLibrary(self):
        raise NotImplementedError

    def _onConvertToPacked(self):
        if self.view.isSingleSelection():
            index = self.view.selectedIndex()
            library_path = index.data(Qt.UserRole)
            repackHDA(library_path)

    def _onConvertToUnpacked(self):
        """
        Expands the contents of the HDA file in into the directory.
        Currently, supported single selection only. Multiple selection is ignored.
        """
        if self.view.isSingleSelection():
            index = self.view.selectedIndex()
            library_path = index.data(Qt.UserRole)
            repackHDA(library_path)

    def _onShowBackups(self):
        raise NotImplementedError

    def _onOpenTypeProperties(self):
        """
        Opens Type Properties window for the selected definition node type.
        Currently, supported single selection only. Multiple selection is ignored.
        """
        if self.view.isSingleSelection():
            index = self.view.selectedIndex()
            definition = index.data(Qt.UserRole)
            hou.ui.openTypePropertiesDialog(definition.nodeType())

    def _onChangeInstancesTo(self):
        raise NotImplementedError
        if self.view.isSingleSelection():
            index = self.view.selectedIndex()
            definition = index.data(Qt.UserRole)
            target_node_type = None  # Todo
            for node in definition.type().instances():
                node.changeNodeType(target_node_type)

    def _onRunHDADoctor(self):
        raise NotImplementedError

    def _onFindUsages(self):
        raise NotImplementedError

    def _onFindDependencies(self):
        raise NotImplementedError

    def _onShowNetworkStatistics(self):
        raise NotImplementedError

    def _onCreateInstance(self):
        """
        Creates instance of the selected node type definition and select it.
        Currently, supported single selection only. Multiple selection is ignored.
        """
        if not self.view.isSingleSelection():
            return

        network = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)
        if network is None:  # No active network editor found
            return

        index = self.view.selectedIndex()
        definition = index.data(Qt.UserRole)

        root_node = network.pwd()

        if definition.nodeTypeCategory() != root_node.childTypeCategory():
            return  # Todo: Switch to corresponding network if possible

        instance_node = root_node.createNode(definition.nodeTypeName(), exact_type_name=True)
        instance_node.setCurrent(True, True)

        rect = network.visibleBounds()
        instance_node.setPosition(rect.center())

    def _onCreateNewHDA(self):
        raise NotImplementedError

    def _onCreateNewVersion(self):
        raise NotImplementedError

    def _onCreateBlackBox(self):
        raise NotImplementedError

    def _onCopy(self):
        raise NotImplementedError

    def _onMove(self):
        raise NotImplementedError

    def _onRename(self):
        raise NotImplementedError

    def _onAddAlias(self):
        raise NotImplementedError

    def _onDelete(self):
        raise NotImplementedError

    def _onHide(self):
        raise NotImplementedError

    def _onDeprecate(self):
        raise NotImplementedError

    def _onCompare(self):
        raise NotImplementedError

    def __createActions(self):
        self._expand_action = QAction('Expand')
        self._expand_action.triggered.connect(self._onExpand)

        self._collapse_action = QAction('Collapse')
        self._collapse_action.triggered.connect(self._onCollapse)

        self._expand_all_action = QAction('Expand all')
        self._expand_all_action.triggered.connect(self._onExpandAll)

        self._collapse_all_action = QAction('Collapse all')
        self._collapse_all_action.triggered.connect(self._onCollapseAll)

        self._open_location_action = QAction(hou.qt.Icon('BUTTONS_folder', ICON_SIZE, ICON_SIZE), 'Open location')
        self._open_location_action.triggered.connect(self._onOpenLocation)

        self._install_library_action = QAction('Install')
        self._install_library_action.triggered.connect(self._onInstall)

        self._uninstall_library_action = QAction('Uninstall')
        self._uninstall_library_action.triggered.connect(self._onUninstall)

        self._reload_library_action = QAction(hou.qt.Icon('MISC_loading', ICON_SIZE, ICON_SIZE), 'Reload')
        self._reload_library_action.triggered.connect(self._onReload)

        self._reload_all_libraries_action = QAction(hou.qt.Icon('MISC_loading', ICON_SIZE, ICON_SIZE), 'Reload all')
        self._reload_all_libraries_action.triggered.connect(self._onReloadAll)

        self._rescan_and_reload_all_action = QAction(hou.qt.Icon('MISC_loading', ICON_SIZE, ICON_SIZE),
                                                     'Rescan and reload all')
        self._rescan_and_reload_all_action.triggered.connect(self._onRescanAndReloadAll)

        self._merge_with_library_action = QAction('Merge with library')
        self._merge_with_library_action.triggered.connect(self._onMergeWithLibrary)

        self._convert_to_packed_action = QAction(hou.qt.Icon('DESKTOP_otl', ICON_SIZE, ICON_SIZE),
                                                 'Convert to packed format')
        self._convert_to_packed_action.triggered.connect(self._onConvertToPacked)

        self._convert_to_unpacked_action = QAction(hou.qt.Icon('DESKTOP_expanded_otl', ICON_SIZE, ICON_SIZE),
                                                   'Convert to unpacked format')
        self._convert_to_unpacked_action.triggered.connect(self._onConvertToUnpacked)

        self._show_backups_action = QAction(hou.qt.Icon('BUTTONS_history', ICON_SIZE, ICON_SIZE), 'Show backups...')
        self._show_backups_action.triggered.connect(self._onShowBackups)

        self._open_type_properties_action = QAction(hou.qt.Icon('BUTTONS_gear_mini', ICON_SIZE, ICON_SIZE),
                                                    'Open type properties...')
        self._open_type_properties_action.triggered.connect(self._onOpenTypeProperties)

        self._change_instances_to_action = QAction('Change instances to...')
        self._change_instances_to_action.triggered.connect(self._onChangeInstancesTo)

        self._run_hda_doctor_action = QAction(hou.qt.Icon('SOP_polydoctor', ICON_SIZE, ICON_SIZE), 'Run HDA Doctor...')
        self._run_hda_doctor_action.triggered.connect(self._onRunHDADoctor)

        self._find_usages_action = QAction(hou.qt.Icon('BUTTONS_search', ICON_SIZE, ICON_SIZE), 'Find usages...')
        self._find_usages_action.triggered.connect(self._onFindUsages)

        self._find_dependencies_action = QAction(hou.qt.Icon('PANETYPES_network', ICON_SIZE, ICON_SIZE),
                                                 'Find dependencies...')
        self._find_dependencies_action.triggered.connect(self._onFindDependencies)

        self._show_network_statistics_action = QAction(hou.qt.Icon('BUTTONS_info', ICON_SIZE, ICON_SIZE),
                                                       'Show network statistics...')
        self._show_network_statistics_action.triggered.connect(self._onShowNetworkStatistics)

        self._create_instance_action = QAction('Instance')
        self._create_instance_action.triggered.connect(self._onCreateInstance)

        self._create_new_hda_action = QAction(hou.qt.Icon('SOP_compile_begin', ICON_SIZE, ICON_SIZE), 'New HDA...')
        self._create_new_hda_action.triggered.connect(self._onCreateNewHDA)

        self._create_new_version_action = QAction(hou.qt.Icon('BUTTONS_multi_insertbefore', ICON_SIZE, ICON_SIZE),
                                                  'New version...')
        self._create_new_version_action.triggered.connect(self._onCreateNewVersion)

        self._create_black_box_action = QAction(hou.qt.Icon('NETVIEW_hda_locked_badge', ICON_SIZE, ICON_SIZE),
                                                'Black box...')
        self._create_black_box_action.triggered.connect(self._onCreateBlackBox)

        self._copy_action = QAction(hou.qt.Icon('BUTTONS_copy', ICON_SIZE, ICON_SIZE), 'Copy...')
        self._copy_action.triggered.connect(self._onCopy)

        self._move_action = QAction(hou.qt.Icon('BUTTONS_move_to_right', ICON_SIZE, ICON_SIZE), 'Move...')
        self._move_action.triggered.connect(self._onMove)

        self._rename_action = QAction(hou.qt.Icon('MISC_rename', ICON_SIZE, ICON_SIZE), 'Rename...')
        self._rename_action.triggered.connect(self._onRename)

        self._add_alias_action = QAction(hou.qt.Icon('BUTTONS_tag', ICON_SIZE, ICON_SIZE), 'Add alias...')
        self._add_alias_action.triggered.connect(self._onAddAlias)

        self._delete_action = QAction(hou.qt.Icon('BUTTONS_delete', ICON_SIZE, ICON_SIZE), 'Delete')
        self._delete_action.triggered.connect(self._onDelete)

        self._hide_action = QAction(hou.qt.Icon('BUTTONS_close', ICON_SIZE, ICON_SIZE), 'Hide')
        self._hide_action.triggered.connect(self._onHide)

        self._deprecate_action = QAction(hou.qt.Icon('BUTTONS_do_not', ICON_SIZE, ICON_SIZE), 'Deprecate')
        self._deprecate_action.triggered.connect(self._onDeprecate)

        self._compare_action = QAction(hou.qt.Icon('BUTTONS_restore', ICON_SIZE, ICON_SIZE), 'Compare...')
        self._compare_action.triggered.connect(self._onCompare)

    def __createContextMenus(self):
        self._library_menu = QMenu(self)

        self._library_menu.addAction(self._install_library_action)
        self._library_menu.addAction(self._uninstall_library_action)
        self._library_menu.addAction(self._reload_library_action)
        self._library_menu.addAction(self._reload_all_libraries_action)
        self._library_menu.addAction(self._rescan_and_reload_all_action)
        self._library_menu.addSeparator()
        self._library_menu.addAction(self._merge_with_library_action)
        self._library_menu.addAction(self._convert_to_packed_action)
        self._library_menu.addAction(self._convert_to_unpacked_action)
        self._library_menu.addSeparator()
        self._library_menu.addAction(self._open_location_action)
        self._library_menu.addAction(self._show_backups_action)
        self._library_menu.addSeparator()
        self._library_menu.addAction(self._expand_action)
        self._library_menu.addAction(self._collapse_action)
        self._library_menu.addAction(self._expand_all_action)
        self._library_menu.addAction(self._collapse_all_action)

        self._definition_menu = QMenu(self)

        self._definition_menu.addAction(self._open_type_properties_action)
        self._definition_menu.addAction(self._change_instances_to_action)

        self._definition_inspect_menu = QMenu('Inspect', self)
        self._definition_menu.addMenu(self._definition_inspect_menu)

        self._definition_inspect_menu.addAction(self._run_hda_doctor_action)
        self._definition_inspect_menu.addAction(self._find_usages_action)
        self._definition_inspect_menu.addAction(self._find_dependencies_action)
        self._definition_inspect_menu.addAction(self._show_network_statistics_action)
        self._definition_inspect_menu.addAction(self._compare_action)

        self._definition_create_menu = QMenu('Create', self)
        self._definition_menu.addMenu(self._definition_create_menu)

        self._definition_create_menu.addAction(self._create_instance_action)
        self._definition_create_menu.addAction(self._create_new_hda_action)
        self._definition_create_menu.addAction(self._create_new_version_action)
        self._definition_create_menu.addAction(self._create_black_box_action)

        self._definition_edit_menu = QMenu('Edit', self)
        self._definition_menu.addMenu(self._definition_edit_menu)

        self._definition_edit_menu.addAction(self._copy_action)
        self._definition_edit_menu.addSeparator()
        self._definition_edit_menu.addAction(self._move_action)
        self._definition_edit_menu.addAction(self._rename_action)
        self._definition_edit_menu.addAction(self._add_alias_action)
        self._definition_edit_menu.addSeparator()
        self._definition_edit_menu.addAction(self._delete_action)
        self._definition_edit_menu.addAction(self._hide_action)
        self._definition_edit_menu.addAction(self._deprecate_action)

        self.view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.view.customContextMenuRequested.connect(self.showContextMenu)

    def showContextMenu(self):
        index = self.view.currentIndex()

        if not index.isValid():
            return

        self.view.deselectDifferingDepth(index)

        if isinstance(index.data(Qt.UserRole), basestring):
            self._library_menu.exec_(QCursor.pos())
        else:
            icon = index.model().index(index.row(), 0, index.parent()).data(Qt.DecorationRole)
            self._create_instance_action.setIcon(icon)
            self._definition_menu.exec_(QCursor.pos())
