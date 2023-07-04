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
import json

# Maya modules
import maya.OpenMaya as om
import maya.cmds as cmds

from rig_tools.tool.ngSkinHelperTool.util import utils
from rig_tools.tool.ngSkinHelperTool.tabInternal.mirrorHelperBase import MirrorBase, PrintStatus

# ngSkinTools2 modules
import ngSkinTools2.mllInterface
import ngSkinTools2.api
import ngSkinTools2.signal
from ngSkinTools2.api import mirror
from ngSkinTools2.api.session import session


class NgControlV2(MirrorBase):

    VERSION = "ngSkinTools2"

    def __init__(self, parent):
        super(NgControlV2, self).__init__(parent)

        self.parent = parent
        self.info = PrintStatus()

        self.mll2 = ngSkinTools2.mllInterface.MllInterface()

    def __str__(self):
        return self.VERSION

    def setSkinMesh(self, geo):
        self.mll2.setCurrentMesh(geo)

        if not self.mll2.getLayersAvailable():
            self.parent.displayBar.errorNoSkinLayer(geo)
            return None

        lay = ngSkinTools2.api.layers.Layers(geo)
        return lay

    def setConfigureMapper(self):
        pass

    def getNumberOfLayers(self, geos):
        """Get the number of layers existing in the geo

        :param
            geos: list
        :return: int
        """
        numberOfAllLayers = 0
        for geo in geos:
            self.setSkinMesh(geo)
            data = self.mll2.listLayers()
            ids = [i["id"] for i in data]
            numberOfAllLayers = numberOfAllLayers + len(ids)
        return numberOfAllLayers

    def addTagName(self, mesh, suffix="NoMirror"):
        """Add a tag name to the selected layer name to avoid mirroring during operations.

        :param
            suffix: str
                Tag name which adds to the layer name
        """
        # get a layer name with layer id
        _layers = self.setSkinMesh(mesh)
        layersObj = _layers.current_layer()

        # skip if layer name has a tag name
        if suffix in layersObj.name:
            return

        # generate a tag name
        taggedName = "{}_{}".format(layersObj.name, suffix)

        # set a new layer name to selected-layer
        layersObj.__edit__(name=taggedName)

        # update the list layer
        session.events.layerListChanged.emitIfChanged()

    def mirror(self, geo, numberOfAllLayers):
        """Mirror all layers on a selected mesh in ngSkinTools2
        """
        self.preProcess(geo)

        data = self.mll2.listLayers()

        trigger = True
        with ngSkinTools2.api.suspend_updates(geo):
            for i, lay in enumerate(data, 1):
                # display the current progress on the screen
                currentNum = float(i)
                progressVal = 100.0 * (currentNum / numberOfAllLayers)
                self.parent.progressBar.setValue(progressVal)

                for noMirror in self.noMirrorList:
                    if noMirror in lay["name"]:
                        trigger = False
                        continue

                if trigger:
                    cmds.ngst2Layers(geo,
                                     id=lay['id'],
                                     mirrorLayerWeights=mirror.MirrorOptions().mirrorWeights,
                                     mirrorLayerMask=mirror.MirrorOptions().mirrorMask,
                                     mirrorLayerDq=mirror.MirrorOptions().mirrorDq,
                                     mirrorDirection=mirror.MirrorOptions().direction,
                                     )

                trigger = True

        # update all influences in the list
        session.events.influencesListUpdated.emit()

        self.postProcess()


class MirrorLayerEffects(object):

    def __init__(self, selectType, parent):
        self.selectType = selectType
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

        # Update mirror layer effects on UI
        selection = cmds.ls(sl=True)
        cmds.select(cl=True)
        session.events.nodeSelectionChanged.emit()
        cmds.select(selection)
        session.events.nodeSelectionChanged.emit()

    def getAllLayers(self, geo):
        layers = self.setSkinMesh(geo)
        return layers.list()

    def getCurrentLayer(self, geo):
        layers = self.setSkinMesh(geo)
        return layers.current_layer()

    def setSkinMesh(self, geo):
        self.mll2.setCurrentMesh(geo)

        if not self.mll2.getLayersAvailable():
            self.parent.displayBar.errorNoSkinLayer(geo)
            return None

        lay = ngSkinTools2.api.layers.Layers(geo)
        return lay

    def setLayerEffects(self, status, everything=False, weight=False, dq=False, mask=False):
        geo = cmds.ls(sl=True)

        if not geo:
            return

        self.preProcess()

        data = None
        if self.selectType == "all":
            data = self.getAllLayers(geo[0])
        elif self.selectType == "current":
            data = self.getCurrentLayer(geo[0])
            data = [data]

        numberOfAllLayers = len(data)

        with ngSkinTools2.api.suspend_updates(geo):
            for i, layer in enumerate(data, 1):
                # display the current progress on the screen
                currentNum = float(i)
                progressVal = 100.0 * (currentNum / numberOfAllLayers)
                self.parent.progressBar.setValue(progressVal)

                if everything:
                    layer.effects.configure_mirror(everything=status)
                elif weight:
                    layer.effects.configure_mirror(mirror_weights=status)
                elif dq:
                    layer.effects.configure_mirror(mirror_dq=status)
                elif mask:
                    layer.effects.configure_mirror(mirror_mask=status)

        self.postProcess()
        return numberOfAllLayers
