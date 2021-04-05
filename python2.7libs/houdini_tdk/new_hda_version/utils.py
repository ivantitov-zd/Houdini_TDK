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


def incrementHDAVersion(node, component, use_original_file):
    node_type = node.type()
    type_name = node_type.name()

    new_type_name = nextVersionTypeName(type_name, component)

    definition = node_type.definition()
    file_path = definition.libraryFilePath()
    if use_original_file:
        new_file_path = file_path
    else:
        ext = os.path.splitext(file_path)[-1]
        new_file_name = new_type_name.replace(':', '_').replace('.', '_') + ext
        new_file_path = os.path.join(os.path.dirname(file_path), new_file_name).replace('\\', '/')

    definition.copyToHDAFile(new_file_path, new_type_name)

    hou.hda.installFile(new_file_path)
    new_definition = hou.hda.definitionsInFile(new_file_path)[0]  # Todo: fix potential bug

    new_definition.updateFromNode(node)

    node.changeNodeType(new_type_name, keep_network_contents=False)
