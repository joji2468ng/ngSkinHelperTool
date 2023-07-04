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
import logging

# Maya modules
import maya.OpenMaya as om

from rig_tools.tool.ngSkinHelperTool.util import utils


# ----------------------------------------------------------------- GLOBALS --#
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class MirrorBase(object):
    """Mirror all ngSkinlayers weights on the specified geo

    :param geoList: str
        Name of skinned mesh.
    """

    noMirrorList = ("NO_MIRROR", "NoMirror", "No_Mirror", "noMirror")

    def __init__(self, parent):
        self.parent = parent

        self.progressStatus = False

    def toggleVisibilityInfomationBar(self):
        if self.progressStatus:
            self.parent.progressBar.setVisible(True)
        else:
            self.parent.progressBar.setVisible(False)

    def setSkinMesh(self, geo):
        pass

    def setConfigureMapper(self):
        pass

    def isProgressStatus(self):
        if self.progressStatus:
            return False
        return True

    def preProcess(self, geo):
        self.progressStatus = self.isProgressStatus()

        # prepare for the mirror process
        self.setSkinMesh(geo)
        self.setConfigureMapper()

        # show the progress bar
        self.toggleVisibilityInfomationBar()

        # set value
        self.parent.progressBar.setValue(0)

    def postProcess(self):
        # hide information bar
        self.progressStatus = False
        self.toggleVisibilityInfomationBar()


class PrintStatus(object):

    def __init__(self):
        self.info = om.MGlobal.displayInfo

    def _getSpecialSymbol(self):
        return ">>>>"

    def setSpacing(self):
        self.info("")

    def setMessage(self, msg):
        self.info(msg)

