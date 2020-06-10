import hou

from PySide2.QtCore import QTimer


def _removeNotification(timer, target_message, target_severity):
    """ Works in Houdini 18.0.472+ only. """
    try:
        current_message, _ = hou.ui.statusMessage()
    except AttributeError:
        return

    if target_severity == hou.severityType.Error:
        target_message = 'Error:       ' + target_message
    elif target_severity == hou.severityType.Warning:
        target_message = 'Warning:     ' + target_message
    elif target_severity == hou.severityType.Fatal:
        target_message = 'Fatal error: ' + target_message

    if current_message == target_message:
        hou.ui.setStatusMessage('')

    timer.stop()


def notify(message, severity_type=hou.severityType.ImportantMessage, duration=2.5):
    hou.ui.setStatusMessage(message, severity_type)

    if duration:
        timer = QTimer()
        timer.timeout.connect(lambda: _removeNotification(timer, message, severity_type))
        timer.start(int(duration * 1000))
