import os.path, posixpath


def getIconPath(filename):
    return  os.path.join(os.path.dirname(__file__), filename).replace(os.sep, posixpath.sep)