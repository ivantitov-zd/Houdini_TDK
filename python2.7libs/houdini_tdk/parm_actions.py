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


def isParmTuple(parms=None, locked_parms=None, **kwargs):
    if not parms and not locked_parms:
        raise ValueError('No parameters given.')

    parm_count = 0

    if parms is not None:
        parm_count += len(parms)

    if locked_parms is not None:
        parm_count += len(locked_parms)

    return parm_count > 1


def parmName(parms=None, locked_parms=None, **kwargs):
    all_parms = (parms or ()) + (locked_parms or ())

    if not all_parms:
        raise ValueError('No parameters given.')

    if isParmTuple(parms, locked_parms):
        names = tuple(parm.name() for parm in all_parms)
        return os.path.commonprefix(names)
    else:
        return all_parms[0].name()


def parmLabel(parms=None, locked_parms=None, **kwargs):
    all_parms = (parms or ()) + (locked_parms or ())

    if not all_parms:
        raise ValueError('No parameters given.')

    return all_parms[0].description()


def parmAccessCode(parms=None, locked_parms=None, **kwargs):
    name = parmName(parms, locked_parms)
    if isParmTuple(parms, locked_parms):
        return '.parmTuple(\'{}\')'.format(name)
    else:
        return '.parm(\'{}\')'.format(name)


def parmValue(parms=None, locked_parms=None, **kwargs):
    all_parms = (parms or ()) + (locked_parms or ())

    if not all_parms:
        raise ValueError('No parameters given.')

    if isParmTuple(parms, locked_parms):
        return all_parms[0].tuple().eval()
    else:
        return all_parms[0].eval()


def parmSetupCode(parms=None, locked_parms=None, **kwargs):
    name = parmName(parms, locked_parms)
    value = parmValue(parms, locked_parms)
    if isParmTuple(parms, locked_parms):
        return '.parmTuple(\'{}\').set({})'.format(name, value)
    else:
        return '.parm(\'{}\').set({})'.format(name, value)


def isParmMenu(parms=None, locked_parms=None, **kwargs):
    all_parms = (parms or ()) + (locked_parms or ())

    if not all_parms:
        raise ValueError('No parameters given.')

    try:
        all_parms[0].menuItems()
        return True
    except hou.OperationFailed:
        return False


def parmMenuValues(parms=None, locked_parms=None, **kwargs):
    if isParmTuple(parms, locked_parms):
        return

    all_parms = (parms or ()) + (locked_parms or ())

    try:
        values = all_parms[0].menuItems()
        return str(values)
    except hou.OperationFailed:
        return


def parmMenuLabels(parms=None, locked_parms=None, **kwargs):
    if isParmTuple(parms, locked_parms):
        return

    all_parms = (parms or ()) + (locked_parms or ())

    try:
        values = all_parms[0].menuLabels()
        return str(values)
    except hou.OperationFailed:
        return
