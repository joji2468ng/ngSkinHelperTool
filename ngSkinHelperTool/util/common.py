"""
:newField description: Description
:newField revisions: Revisions
:newField departments: Departments
:newField applications: Applications

:Authors:
    Joji Nishimura

:Title
    ngSkinHelperTool

:Organization:
    Reel FX Creative Studios

:Departments:
    rigging

:Description:

:Revisions:
"""
# Build-in
import os


def getIconPath(fileName):
    """This function takes in the name of an icon and
    returns the file path of the icon in the system.

    :param fileName: str
    :return: str
        the file path of the icon
    """
    utilPath = os.path.dirname(os.path.abspath(__file__))
    toolPath = os.path.dirname(utilPath)
    iconPath = os.path.join(toolPath, "icon", fileName)
    return iconPath


def asList(arg):
    """Function takes a single argument arg and converts it to a list if it's not already a list.
    If arg is already a list, it returns arg unchanged,

    :param arg:
    :return:
    """
    if isinstance(arg, basestring):
        return [arg]
    else:
        try:
            return list(arg)
        except TypeError:
            return [arg]


def getDataPath(fileName=None):
    """Function that takes a string argument filename and returns the full file path of the file
    with that name in the data directory of the current package.

    :param fileName: str
    :return: str
        the full file path
    """
    utilPath = os.path.dirname(os.path.abspath(__file__))
    toolPath = os.path.dirname(utilPath)

    if fileName is None:
        return os.path.join(toolPath, "data")

    return os.path.join(toolPath, "data", fileName)
