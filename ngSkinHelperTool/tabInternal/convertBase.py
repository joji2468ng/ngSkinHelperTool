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

# Third party
from maya import cmds

# Local modules
from rig_tools.tool.ngSkinHelperTool.util import utils

# ngSkinTools1 modules
if utils.IS_NG1:
    import ngSkinTools.ui.events
    import ngSkinTools.mllInterface

# ngSkinTools2 modules
if utils.IS_NG2:
    from ngSkinTools2.api.session import session

# ----------------------------------------------------------------- GLOBALS --#
logger = logging.getLogger("import v1")


class ConvertBase(object):

    __has_v1 = None
    DOCK_NAME_V1 = 'ngSkinToolsMainWindow_dock'
    DOCK_NAME_V2 = 'ngSkinTools2_mainWindow'

    def __init__(self, parent=None, target=None):
        self.progressStatus = False
        self.parent = parent
        self.target = target

        self.layerIdMap = {0: None}

    def isProgressStatus(self):
        if self.progressStatus:
            return False
        return True

    def toggleVisibilityInfomationBar(self):
        if self.progressStatus:
            self.parent.progressBar.setVisible(True)
        else:
            self.parent.progressBar.setVisible(False)

    def isWindowExist(self, dockName):
        if not cmds.workspaceControl(dockName, q=True, exists=True):
            return False
        else:
            return True

    def preProcess(self, mesh):
        self.progressStatus = self.isProgressStatus()

        # prepare for the convert process
        self.target = mesh

        # show the progress bar
        self.toggleVisibilityInfomationBar()

        # set value
        self.parent.progressBar.setValue(0)

    def postProcess(self):
        # hide information bar
        self.progressStatus = False
        self.toggleVisibilityInfomationBar()

        # delete a ngSkinData
        self.cleanup()

        if self.isWindowExist(self.DOCK_NAME_V1):
            # update targe selection for one
            ngSkinTools.ui.events.MayaEvents.nodeSelectionChanged.emit()

        if self.isWindowExist(self.DOCK_NAME_V2):
            # update targe selection for two
            session.events.targetChanged.emitIfChanged()

    def has_v1(self):
        if self.__has_v1 is not None:
            return self.__has_v1

        self.__has_v1 = False
        try:
            cmds.loadPlugin('ngSkinTools')
            self.__has_v1 = True
        except:
            pass

        return self.__has_v1

    def _cleanup(self, nodes):
        hist = cmds.listHistory(self.target) or []
        skinClusters = [i for i in hist if cmds.nodeType(i) in ('skinCluster')]
        cmds.delete(
            [
                i
                for skinCluster in skinClusters
                for i in cmds.listHistory(skinCluster, future=True, levels=1)
                if cmds.nodeType(i) in nodes
            ]
        )

    def cleanup(self):
        pass

    def convertProcess(self):
        pass

    def convert(self, mesh):
        self.preProcess(mesh)

        self.convertProcess()

        self.postProcess()

