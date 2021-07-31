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

import base64
import re
import string
import random

try:
    import hou
    from digitalassetsupport import create_instance
except ImportError:
    hou = None


def permutations(alphabet, exclude_at_start):
    """
    Yields an endless sequence of permutations with the given alphabet.
    Example for alphabet [AB]: A B AA AB BA BB AAA AAB ABA ABB BAA ...
    """
    alphabet_length = len(alphabet)
    assert alphabet_length == len(set(alphabet))
    index = 0
    while True:
        chars = []
        index += 1
        n = index
        while n > 0:
            n, r = divmod(n - 1, alphabet_length)
            chars.insert(0, alphabet[r])
        if chars[0] in exclude_at_start:
            index += alphabet_length ** (len(chars) - 1) - 1
            continue
        yield ''.join(chars)


def obfuscateVEX(code):
    # Remove inline comments
    # Fixme: Escaped quotes
    prev_open_quote = None
    in_quotes = False
    prev_char = None
    index = -1
    while index < len(code) - 1:
        index += 1
        char = code[index]
        if char in ('"', '\''):
            if char == prev_open_quote or char:
                if in_quotes and char != prev_open_quote:
                    continue
                in_quotes = not in_quotes
                if in_quotes and char != prev_open_quote:
                    prev_open_quote = char
        elif not in_quotes:
            if char == '/' and prev_char == '/':
                try:
                    line_end = code.index('\n', index)
                except ValueError:
                    code = code[:index - 1]
                    break
                code = code[:index - 1] + code[line_end:]
            prev_char = char
    # Remove redundant whitespaces at the beginning of lines
    code = re.sub(r'^\s+', '', code, flags=re.MULTILINE)
    # Remove redundant whitespaces at the end of lines
    code = re.sub(r'\s+$', '', code, flags=re.MULTILINE)
    # Remove newlines where possible (excluding preprocessor directives)
    code = re.sub(r'(?P<keep>^[^#].*?)\n+', r'\g<keep> ', code, flags=re.MULTILINE)
    return code


obfuscateOpenCL = obfuscateVEX  # Todo: Split in the future


def obfuscatePython(code):
    # Remove inline comments
    prev_open_quote = None
    in_quotes = False
    index = -1
    while index < len(code) - 1:
        index += 1
        char = code[index]
        if char in ('"', '\''):
            if char == prev_open_quote or char:
                if in_quotes and char != prev_open_quote:
                    continue
                in_quotes = not in_quotes
                if in_quotes and char != prev_open_quote:
                    prev_open_quote = char
        elif not in_quotes:
            if char == '#':
                try:
                    line_end = code.index('\n', index)
                except ValueError:
                    code = code[:index]
                    break
                code = code[:index] + code[line_end:]
    # Remove repeated newlines
    code = re.sub(r'\n+', r'\n', code)
    return code


def packCode(code, python=False):
    code = base64.b64encode(code)
    if python:
        code = 'exec(__import__(\'base64\').b64decode(\'{}\'))'.format(code)
    else:
        code = '`pythonexprs(\'__import__("base64").b64decode("{}")\')`'.format(code)
    return code


def obfuscateNodeParms(node):
    if not isinstance(node, hou.Node):
        node = hou.node(node)

    for parm in node.parms():
        template = parm.parmTemplate()
        if template.dataType() == hou.parmData.String:
            tags = template.tags()
            if 'editorlang' in tags:
                lang = tags['editorlang'].lower()
                if lang == 'vex':
                    code = parm.rawValue()
                    code = obfuscateVEX(code)
                    code = packCode(code)
                    parm.set(code)
                elif lang == 'opencl':
                    code = parm.rawValue()
                    code = obfuscateOpenCL(code)
                    code = packCode(code)
                    parm.set(code)
                elif lang == 'python':
                    code = parm.rawValue()
                    code = obfuscatePython(code)
                    code = packCode(code, python=True)
                    parm.set(code)


def obfuscateNetwork(root_node):
    if not isinstance(root_node, hou.Node):
        root_node = hou.node(root_node)

    nodes = root_node.allNodes()
    next(nodes)  # Skip source node
    nodes = tuple(node for node in nodes if not node.isInsideLockedHDA())
    nodes = tuple(random.sample(nodes, len(nodes)))
    new_node_labels = permutations(alphabet=string.ascii_letters + string.digits + '-_.',
                                   exclude_at_start=string.digits + '-.')
    for node, new_name in zip(nodes, new_node_labels):
        node.setName(new_name)
        obfuscateNodeParms(node)


def getVOPScriptCode(source):
    pass


def obfuscateVOPScript(node):
    """
    Creates subnet node from VOP script HDA and new HDA from it.
    Tries to keep the exact signature, but only single output signature supported.
    """
    if not isinstance(node, hou.Node):
        node = hou.node(node)

    root_node = node.parent()

    subnet_node = root_node.createNode('subnet')

    internal_node_names = random.sample(string.ascii_letters, 3)

    subinput_node = subnet_node.node('subinput1')  # Fixme: Find instead of picking by name
    subinput_node.setName(internal_node_names.pop())

    inline_node = subnet_node.createNode('inline', internal_node_names.pop())
    inline_node.parm('code').set('$length = length($vec);')
    inline_node.parm('includes').set('')
    inline_node.parm('outercode').set('')

    input_index = -1
    for data_type, name, label in zip(node.inputDataTypes(), node.inputNames(), node.inputLabels()):
        input_index += 1
        if data_type == 'undef':
            break

        const_node = subnet_node.createInputNode(input_index, 'constant')
        const_node.parm('constname').set(name)
        const_node.parm('consttype').set(data_type)
        # Fixme: Destroy utility nodes after work done

        inline_node.setInput(input_index, subinput_node)

    suboutput_node = subnet_node.node('suboutput1')  # Fixme: Find instead of picking by name
    suboutput_node.setName(internal_node_names.pop())

    output_num = 0
    for data_type, name, label in zip(node.outputDataTypes(), node.outputNames(), node.outputLabels()):
        output_num += 1
        if data_type == 'undef':
            break

        inline_node.parm('outtype' + str(output_num)).set(data_type)
        inline_node.parm('outname' + str(output_num)).set(name)
        inline_node.parm('outlabel' + str(output_num)).set(label)

        suboutput_node.setInput(output_num, inline_node)

    obfuscateNetwork(subnet_node)

    # Todo: Assemble new HDA (embedded? use TDK template?)
    # Todo: Transfer parm template group


def obfuscatePythonOP(node):
    # Todo: Code from PythonCook minify, obfuscate and move gzipped to new random binary section
    # Todo: Replace code in PythonCook with base64 encoded unpacking code
    pass


def obfuscate(source):
    if isinstance(source, hou.HDADefinition):
        if not source.isInstalled():
            hou.hda.installFile(source.libraryFilePath())
            source.setIsPreferred(True)
        source_type = source.nodeType()
    elif isinstance(source, hou.NodeType):
        source_type = source
    elif isinstance(source, hou.Node):
        source_type = source.type()
    else:
        raise TypeError('Invalid source type.')

    if source_type.source() == hou.nodeTypeSource.Subnet:
        node, secondary_node = create_instance(source_type)
        node.allowEditingOfContents()
        obfuscateNetwork(node)
    elif source_type.source() == hou.nodeTypeSource.Internal:
        if source_type.hasSectionData('PythonCook'):
            obfuscatePythonOP(source_type)
        elif source_type.category() == hou.vopNodeTypeCategory():
            pass
