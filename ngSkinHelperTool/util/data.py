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
import os.path
import json

# Maya module
import maya.cmds as cmds

from PySide2.QtWidgets import QFileDialog

# Local module
from rig_tools.tool.ngSkinHelperTool.util import common


class Data(object):
    """Base Data Object Class
    Contains functions to save and load standard rig data.
    """

    def __init__(self):
        """Data Object Class Initializer
        """
        # Initialize data
        self._data = {}

        # Initialize data type
        self.dataType = 'Data'

        # File filter
        self.fileFilter = "Json Files (*.json)"
        self.startingDirectory = common.getDataPath()

    def save(self, filePath, data, force=True):
        """Save data object to file.
        :param:
            filePath: str
                Target file path.
        :param:
            force:
                Force save if file already exists. (Overwrite).
        type force: bool
        """
        # Check directory Path
        dirpath = os.path.dirname(filePath)
        if not os.path.isdir(dirpath):
            os.makedirs(dirpath)

        # Check file Path
        if os.path.isfile(filePath) and not force:
            raise Exception('File "' + filePath + '" already exists! Use "force=True" to overwrite the existing file.')

        # Save file
        with open(filePath, 'w') as fp:
            json.dump(data, fp, indent=4)

        print('Saved ' + self.__class__.__name__ + ': "' + filePath + '"')

        return filePath

    def saveAs(self, data):
        """Save data object to file.
        Opens a file dialog, to allow the user to specify a file path. 
        """
        # Specify file Path
        filePath = cmds.fileDialog2(fileFilter=self.fileFilter,
                                    dialogStyle=2,
                                    fileMode=0,
                                    caption='Save As',
                                    startingDirectory=self.startingDirectory)

        if not filePath:
            return

        filePath = self.save(filePath[0], data, force=True)

        return filePath

    def load(self, filePath=None):
        """Load data object from file.

        :param:
            filePath: Target file path
        filePath: str
        """
        if not filePath:
            filePath = cmds.fileDialog2(fileFilter=self.fileFilter,
                                        dialogStyle=2,
                                        fileMode=1,
                                        caption='Load Data File',
                                        okCaption='Load',
                                        startingDirectory=self.startingDirectory)
            if not filePath:
                return None

            filePath = filePath[0]
        else:
            if not os.path.isfile(filePath):
                raise Exception('File "' + filePath + '" does not exist!')

        with open(filePath, 'r') as fp:
            data = json.load(fp)

        return data

    def reset(self):
        """Reset data object
        """
        self.__init__()

