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

# ngSkinTools2 modules
import ngSkinTools2.mllInterface
from ngSkinTools2.api.session import session
from ngSkinTools2.api import layers


class NgLayerControlV2(object):

    def __init__(self, treeWidget, parent):
        self.tree = treeWidget
        self.mll2 = ngSkinTools2.mllInterface.MllInterface()
        self.parent = parent
        self.progressStatus = False

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

        if not utils.hasLayerData(mesh, version=2):
            layerData = layers.init_layers(mesh)
        else:
            layerData = layers.Layers(mesh)

        for i in range(num):
            # display the current progress on the screen
            currentNum = float(i)
            progressVal = 100.0 * (currentNum / num)
            self.parent.progressBar.setValue(progressVal)

            topItemInt = num - (i + 1)
            topItem = self.tree.topLevelItem(topItemInt)
            topItemData = topItem.data(0, QtCore.Qt.UserRole)

            layer = layerData.add(name=topItemData["name"])
            layer.effects.configure_mirror(everything=True)
            layerId = layers.as_layer_id(layer)

            # Create each children of top-item layers
            self.createSubTreeLayers(mesh, topItem, layerId)

        self.postProcess()

        # Update the layers widget
        session.events.targetChanged.emitIfChanged()
        session.events.layerListChanged.emitIfChanged()

    def createSubTreeLayers(self, mesh, treeWidgetItem, parentId):
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

            layerData = layers.Layers(mesh)
            layer = layerData.add(name=childItemData["name"], parent=parentId)
            layer.effects.configure_mirror(everything=True)
            childId = layers.as_layer_id(layer)

            if not childItem.childCount() == 0:
                self.createSubTreeLayers(mesh, childItem, childId)
