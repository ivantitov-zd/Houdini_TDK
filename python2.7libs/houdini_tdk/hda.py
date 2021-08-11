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

from __future__ import print_function

import os

from lxml import etree

import hou

from .utils import removePath


def findDefinitionInFile(file_path, type_name):
    for definition in hou.hda.definitionsInFile(file_path):
        if definition.nodeTypeName() == type_name:
            return definition
    raise hou.OperationFailed('Definition not found in OTL.')


class SourceType:
    Custom = 0
    Subnetwork = 1
    Python = 2
    VEX = 3


def dialogScriptForInlineVEX(node, name, label):
    # Auto
    template = '# Dialog script for {} automatically generated\n\n'.format(name)

    # Open brace
    template += '{'

    # Main
    template += '''
    name\t{name}
    script\t{name}
    label\t"{label}"
'''.format(name=name, label=label)

    # Outer code
    outer_code = node.parm('outercode').eval()
    if outer_code:
        template += '    outercode {\n'
        for line in outer_code.splitlines(False):
            line = line.replace('"', '\\"')
            template += '\t"{}"'.format(line)
        template += '\n    }\n\n'

    # Code
    code = node.parm('code').rawValue()
    if code:
        template += '    code {\n'
        for line in code.splitlines(False):
            line = line.replace('"', '\\"')
            template += '\t"{}"'.format(line)
        template += '\n    }\n\n'

    io_types = []  # Used for signatures below

    # Inputs
    for input_type, input_name in zip(node.inputDataTypes(), node.inputNames()):
        if input_type == 'undef':
            break
        template += '    input\t{0}\t{1}\t"{1}"\n'.format(input_type, input_name)
        template += '    inputflags\t{}\t0\n'.format(input_name)
        io_types.append(input_type)

    # Outputs
    for n in range(1, 65):
        num = str(n)
        output_type = node.parm('outtype' + num).eval()
        if output_type == 'undef':
            break
        output_name = node.parm('outname' + num).eval()
        output_label = node.parm('outlabel' + num).eval()
        template += '    output\t{}\t{}\t"{}"\n'.format(output_type, output_name, output_label)
        io_types.append(output_type)

    # Signatures
    template += '    signature\t"Default Inputs"\tdefault\t{ ' + ' '.join(io_types) + ' }\n'

    template += '\n'

    # Parameters
    # Todo with help of ParmTemplateGroup

    # Closing brace
    template += '\n}'
    return template


def makeHDA(
        source,
        label,
        name=None,
        namespace=None,
        icon=None,
        tab_sections=None,
        version='1.0',
        location='$HOUDINI_USER_PREF_DIR/otls',
        inherit_network=True,
        inherit_parm_template_group=True,
        color=None,
        shape=None
):
    location = hou.expandString(location)
    if not os.path.exists(location):
        raise IOError

    new_type_name = ''

    if namespace:
        new_type_name += namespace.replace(' ', '_')
        new_type_name += '::'

    if name:
        new_type_name += name.replace(' ', '_')
    else:
        new_type_name += label.replace(' ', '_').lower()

    new_type_name += '::'

    if version:
        new_type_name += version
    else:
        new_type_name += '1.0'

    source_type = SourceType.Custom
    source_def = None
    if isinstance(source, hou.Node):
        if source.type().category() == hou.objNodeTypeCategory():
            if source.type().name() == 'subnet':
                source_def = hou.nodeType(hou.objNodeTypeCategory(), 'tdk::template').definition()
                source_type = SourceType.Subnetwork
            elif source.type().name() == 'pythonscript':
                source_def = hou.nodeType(hou.objNodeTypeCategory(), 'tdk::template_python').definition()
                source_type = SourceType.Python
        elif source.type().category() == hou.sopNodeTypeCategory():
            if source.type().name() == 'subnet':
                source_def = hou.nodeType(hou.sopNodeTypeCategory(), 'tdk::template').definition()
                source_type = SourceType.Subnetwork
            elif source.type().name() == 'python':
                source_def = hou.nodeType(hou.sopNodeTypeCategory(), 'tdk::template_python').definition()
                source_type = SourceType.Python
        elif source.type().category() == hou.vopNodeTypeCategory():
            if source.type().name() == 'subnet':
                source_def = hou.nodeType(hou.vopNodeTypeCategory(), 'tdk::template').definition()
                source_type = SourceType.Subnetwork
            elif source.type().name() == 'inline':
                source_def = hou.nodeType(hou.vopNodeTypeCategory(), 'tdk::template_script').definition()
                source_type = SourceType.VEX

        if source_def is None:
            source_def = source.type().definition()
    elif isinstance(source, hou.NodeType):
        source_def = source.definition()
    elif isinstance(source, hou.HDADefinition):
        source_def = source

    if source_def is None:
        raise TypeError('Invalid source type')

    new_hda_file_name = new_type_name.replace(':', '_').replace('.', '_') + '.hda'
    new_hda_file_path = os.path.join(location, new_hda_file_name).replace('\\', '/')
    source_def.copyToHDAFile(new_hda_file_path, new_type_name)

    new_def = findDefinitionInFile(new_hda_file_path, new_type_name)

    if isinstance(source, hou.Node):
        input_count = len(source.inputs())
        last_used_indirect_input_number = 0
        for indirect_input in source.indirectInputs():
            if indirect_input.outputs():
                # Bug reported: SubnetIndirectInput.number() returns index instead of number
                last_used_indirect_input_number = max(last_used_indirect_input_number, indirect_input.number() + 1)
        new_def.setMaxNumInputs(max(1, input_count, last_used_indirect_input_number))

        if source_type == SourceType.Python:
            code = source.parm('python').eval()
            new_def.addSection('PythonCook', code)

        if inherit_network and source_type not in (SourceType.Python, SourceType.VEX):
            new_def.updateFromNode(source)

        if inherit_parm_template_group:
            if source_type == SourceType.VEX:
                ds_section = new_def.sections()['DialogScript']
                script = dialogScriptForInlineVEX(source, new_type_name, label)
                ds_section.setContents(script)
            else:
                parm_template_group = source.parmTemplateGroup()
                if source_type == SourceType.Python:
                    parm_template_group.remove('python')
                hou.hda.installFile(new_hda_file_path)
                new_def.setParmTemplateGroup(parm_template_group)
                hou.hda.uninstallFile(new_hda_file_path)

    new_def.setDescription(label)

    if icon:
        new_def.setIcon(icon)

    if tab_sections and tab_sections.strip():
        sections = (section.strip() for section in tab_sections.split(','))
        try:
            tools = new_def.sections()['Tools.shelf']
            content = tools.contents()
            parser = etree.XMLParser(remove_blank_text=True, resolve_entities=False, strip_cdata=False)
            root = etree.fromstring(content.encode('utf-8'), parser)

            tool = root.find('tool')
            for submenu in tool.findall('toolSubmenu'):
                tool.remove(submenu)

            for section in sections:
                submenu = etree.Element('toolSubmenu')
                submenu.text = section
                tool.append(submenu)

            tools.setContents(etree.tostring(root, encoding='utf-8', pretty_print=True))
        except KeyError:
            pass

    extra_file_options = new_def.extraFileOptions()
    if new_def.hasSection('PreFirstCreate') and extra_file_options.get('PreFirstCreate/IsPython'):
        pre_first_create_section = new_def.sections()['PreFirstCreate']
    else:
        pre_first_create_section = new_def.addSection('PreFirstCreate')
        new_def.setExtraFileOption('PreFirstCreate/IsExpr', False)
        new_def.setExtraFileOption('PreFirstCreate/IsScript', True)
        new_def.setExtraFileOption('PreFirstCreate/IsPython', True)

    if color is not None:
        set_default_color_code = ('\n# Generated by TDK (https://github.com/anvdev/Houdini_TDK)\n'
                                  'kwargs[\'type\'].setDefaultColor(hou.Color({}))\n').format(color.getRgbF()[:3])

        content = pre_first_create_section.contents()
        content += set_default_color_code
        pre_first_create_section.setContents(content)

    if shape is not None:
        set_default_shape_code = ('\n# Generated by TDK (https://github.com/anvdev/Houdini_TDK)\n'
                                  'kwargs[\'type\'].setDefaultShape(\'{}\')\n').format(shape)

        content = pre_first_create_section.contents()
        content += set_default_shape_code
        pre_first_create_section.setContents(content)

    return new_def


def copyHDA(source, path, type_name=None, label=None, preserve_source=True):
    if isinstance(source, hou.Node):
        source_def = source.type().definition()
    elif isinstance(source, hou.NodeType):
        source_def = source.definition()
    elif isinstance(source, hou.HDADefinition):
        source_def = source
    else:
        raise TypeError('Invalid source type')

    try:
        hou.hda.definitionsInFile(path)
    except hou.OperationFailed:
        if os.path.exists(path) and os.path.isdir(path):
            if not type_name:
                type_name = source_def.nodeTypeName()

            path = os.path.join(path, type_name.replace(':', '_').replace('.', '_') + '.hda')
        else:
            if not path.endswith('.hda'):
                path = path + '.hda'

    source_def.copyToHDAFile(path, type_name, label)

    if not preserve_source:
        source_def.destroy()


def moveHDA(source, path):
    copyHDA(source, path, preserve_source=False)


def repackHDA(library_path, expand=True):
    if not os.path.exists(library_path):
        return

    library_dir, name = os.path.split(library_path)
    temp_repack_path = os.path.join(library_dir, 'temp_' + name)

    try:
        if expand:
            hou.hda.expandToDirectory(library_path, temp_repack_path)
        else:
            hou.hda.collapseFromDirectory(temp_repack_path, library_path)

        backup_library_path = os.path.join(library_dir, 'temp_' + name + '_backup')
        os.rename(library_path, backup_library_path)
    except hou.OperationFailed:
        return
    except OSError:
        removePath(temp_repack_path)
        return

    try:
        os.rename(temp_repack_path, library_path)
        removePath(backup_library_path)
    except OSError:
        os.rename(backup_library_path, library_path)
        removePath(temp_repack_path)
        return

    hou.hda.reloadFile(library_path)


def expandHDA(library_path):
    return repackHDA(library_path)


def collapseHDA(library_path):
    return repackHDA(library_path, expand=False)
