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
import tempfile
from datetime import datetime
import struct
import hashlib
from itertools import cycle

import hou

from .obfuscation import obfuscate
from .. import hda

definition = kwargs['definition']  # Context-related kwargs
# TDK_Security should be replaced with random character
if not definition.hasSection('TDK_Security'):
    raise hou.OperationFailed

security_data_section = definition.sections().get('TDK_Security')
security_data = security_data_section.contents(hou.compressionType.Gzip)
(
    use_password,
    stored_password_hash,
    retries,
    start_date,
    end_date
) = struct.unpack('=b32shll', security_data)

if not (start_date <= datetime.utcnow().toordinal() <= end_date):
    raise hou.PermissionError  # Todo: Add message

if use_password:
    _, user_password = hou.readInput('Password:')  # Todo: Use custom dialog to replace chars with asterisks
    user_password_hash = hashlib.sha256(user_password).digest()
    if user_password_hash != stored_password_hash:
        raise hou.PermissionError  # Todo: Add message


def crypt(data, password):
    key = hashlib.sha256(password.encode('utf-8')).digest()
    return bytes(a ^ b for a, b in zip(data, cycle(key)))


def injectPasswordPrompt(target, password):
    pass


def injectTimeLimit(target, options, password=None):
    pass


def protect(source, file_path):
    if isinstance(source, hou.HDADefinition):
        source_def = source
    elif isinstance(source, hou.NodeType):
        source_def = source.definition()
    elif isinstance(source, hou.Node):
        source_def = source.type().definition()
    else:
        raise TypeError('Invalid source type.')

    temp_path = tempfile.mkstemp('.hda', 'temp_')
    source_def.copyToHDAFile(temp_path)
    temp_def = hda.findDefinitionInFile(temp_path, source_def.typeName())

    obfuscate(temp_def)
    injectPasswordPrompt(temp_def, None)
    injectTimeLimit(temp_def, None)

    options = temp_def.options()
    options.setCompressContents(True)
    # Used undocumented signature
    temp_def.save(file_path, options=options, create_backup=False, compile_contents=True, black_box=True)

    # Cleanup
    hou.hda.uninstallFile(temp_path)
    os.unlink(temp_path)
    return hda.findDefinitionInFile(file_path, source_def.typeName())
