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
import subprocess
import sys
import webbrowser
import shutil


def openFileLocation(file_path):
    """
    Opens default explorer and goes to the file_path directory.
    In Windows OS also selects the file.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError

    if sys.platform.startswith('win'):
        # Windows Explorer requires backslashes
        subprocess.call('explorer /select,"{0}"'.format(file_path.replace('/', '\\')))
    else:
        webbrowser.open('file://' + os.path.dirname(file_path))


def removePath(path):
    if os.path.isfile(path):
        os.remove(path)
    else:
        shutil.rmtree(path, True)
