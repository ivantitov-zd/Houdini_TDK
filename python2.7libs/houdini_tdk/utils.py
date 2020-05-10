import os
import subprocess
import sys
import webbrowser


def openFileLocation(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError

    if not os.path.isfile(file_path):
        raise IsADirectoryError

    if sys.platform.startswith('win'):
        subprocess.call('explorer /select,"{0}"'.format(file_path.replace('/', '\\')))
    else:
        webbrowser.open('file://' + os.path.dirname(file_path))
