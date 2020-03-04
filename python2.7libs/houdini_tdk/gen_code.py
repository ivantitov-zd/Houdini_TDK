from __future__ import print_function

import hou


def generateCode(**kwargs):
    nodes = hou.selectedNodes()
    if not nodes:
        raise hou.Error('No node selected')
    code = ''
    for node in nodes:
        code += node.asCode()
    if code:
        hou.ui.copyTextToClipboard(code)
        hou.ui.setStatusMessage('Code was generated and copied',
                                hou.severityType.ImportantMessage)
