import os
import subprocess
import sys
import webbrowser
import shutil


def openFileLocation(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError

    if not os.path.isfile(file_path):
        raise IsADirectoryError

    if sys.platform.startswith('win'):
        subprocess.call('explorer /select,"{0}"'.format(file_path.replace('/', '\\')))
    else:
        webbrowser.open('file://' + os.path.dirname(file_path))


def removePath(path):
    if os.path.isfile(path):
        os.remove(path)
    else:
        shutil.rmtree(path, True)
