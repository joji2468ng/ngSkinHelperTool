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

# Maya modules
from PySide2 import QtCore

# Local modules
from rig_tools.tool.ngSkinHelperTool.util import utils
from rig_tools.tool.ngSkinHelperTool.tabInternal import layerManagerBase


# ngSkinTools1 modules
import ngSkinTools.mllInterface
import ngSkinTools.ui.events


class NgLayerControlV1(object):

    def __init__(self, treeWidget, parent):
        self.tree = treeWidget
        self.parent = parent
        self.mll1 = ngSkinTools.mllInterface.MllInterface()
        self.progressStatus = False

        self.remapId = {}

    def isProgressStatus(self):
        if self.progressStatus:
            return False
        return True

    def toggleVisibilityInfomationBar(self):
        if self.progressStatus:
            self.parent.progressBar.setVisible(True)
        else:
            self.parent.progressBar.setVisible(False)

    def preProcess(self):
        self.progressStatus = self.isProgressStatus()

        # show the progress bar
        self.toggleVisibilityInfomationBar()

        # set value
        self.parent.progressBar.setValue(0)

    def postProcess(self):
        # hide information bar
        self.progressStatus = False
        self.toggleVisibilityInfomationBar()

    def createLayer(self, mesh):
        self.preProcess()

        num = self.tree.topLevelItemCount()
        if num == 0:
            return None

        for i in range(num):
            # display the current progress on the screen
            currentNum = float(i)
            progressVal = 100.0 * (currentNum / num)
            self.parent.progressBar.setValue(progressVal)

            topItemInt = num - (i + 1)
            topItem = self.tree.topLevelItem(topItemInt)
            topItemData = topItem.data(0, QtCore.Qt.UserRole)

            # Create top-item layers
            if not utils.hasLayerData(mesh, version=1):
                self.mll1.initLayers()
            topLayerId = self.mll1.createLayer(name=topItemData["name"])

            # Create each children of top-item layers
            self.createSubTreeLayers(topItem, topLayerId)

        self.postProcess()

        # Update the layers widget
        ngSkinTools.ui.events.MayaEvents.nodeSelectionChanged.emit()

    def createSubTreeLayers(self, treeWidgetItem, parentId):
        """Returns all QTreeWidgetItems in the subtree rooted at the given node.
        :param
            treeWidgetItem: QTreeWidgetItem
            sumNum: a total number of existing items in widget
        :return:
            list of each data, a total number of items
        """
        num = treeWidgetItem.childCount()
        for i in range(num - 1, -1, -1):
            childItem = treeWidgetItem.child(i)
            childItemData = childItem.data(0, QtCore.Qt.UserRole)

            childId = self.mll1.createLayer(name=childItemData["name"])
            self.mll1.setLayerParent(childId, parentId)

            if not childItem.childCount() == 0:
                self.createSubTreeLayers(childItem, childId)
