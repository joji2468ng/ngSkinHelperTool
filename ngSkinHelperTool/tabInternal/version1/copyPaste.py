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
# Built-in
from builtins import zip
import json
import logging

# Third Party
from maya import cmds

# Reelfx modules
from rig_tools.tool import ngSkinUtils, ngSkinUtils2

from rig_tools.tool.ngSkinHelperTool.util import utils
from rig_tools.tool.ngSkinHelperTool.tabInternal.copyPasteBase import CopyPasteInfluence


# ngSkinTools1 modules
import ngSkinTools.mllInterface
import ngSkinTools.utilities.weightsClipboard
import ngSkinTools.ui.events


class NgSkinControlV1(CopyPasteInfluence):
    VERSION = "ngSkinTools1"

    def __init__(self):
        super(NgSkinControlV1, self).__init__()

        self.mll1 = ngSkinTools.mllInterface.MllInterface()

    def __str__(self):
        return self.VERSION

    def getInfluenceData(self):
        self.mll1.setCurrentMesh(self.mesh)
        listInfInfo = self.mll1.listInfluenceInfo()
        infPaths = [ii.path.rsplit('|', 1)[-1] for ii in listInfInfo]
        infIndexes = [ii.logicalIndex for ii in listInfInfo]

        infIndetKey = dict(list(zip(infIndexes, infPaths)))
        infNameKey = dict(list(zip(infPaths, infIndexes)))
        return infIndetKey, infNameKey

    def getLayerData(self):
        layerDict = {}

        layers = self.mll1.listLayers()
        for i in layers:
            layerDict[i["name"]] = i["id"]
        return layerDict

    def getUsedInfluenceData(self, indentKey, nameKey):
        infData = self.mll1.listLayerInfluences(self.srcLayerID)
        infName = [inf[0] for inf in infData]
        infId = [inf[1] for inf in infData]
        return infName, infId

    def copyWeights(self, srcInfID):
        # copy or cut weights from a specific joint on the source layer
        func = ngSkinTools.utilities.weightsClipboard
        weightClip = func.WeightsClipboard(self.mll1)
        weightClip.layer = self.srcLayerID
        weightClip.influence = srcInfID

        # operation starts
        if self.operation is "cut":
            weightClip.cut()
        else:
            weightClip.copy()

        if self.mask:
            maskWeight = self.mll1.getLayerMask(self.srcLayerID)
        else:
            maskWeight = None

        return weightClip, maskWeight

    def pasteWeights(self, weightClip, maskWeight, dstInfID):
        # paste weights to the destination layer with a copied weights
        weightClip.layer = self.dstLayerID
        weightClip.influence = dstInfID
        if self.operation == "cut" or self.operation == "replace":
            weightClip.pasteReplace()
        elif self.operation == "add":
            weightClip.pasteAdd()
        elif self.operation == "subtract":
            weightClip.pasteSubstract()

        # apply mask weighs if checked
        if maskWeight:
            self.mll1.setLayerMask(self.dstLayerID, maskWeight)

        # update all influences in the list
        ngSkinTools.ui.events.LayerEvents.influenceListChanged.emit()

    def getCurrentLayer(self):
        mesh = utils.getNgSkinnedMesh(mode=1)[0]
        if mesh is None:
            return None, None

        self.setSelectedGeo(mesh)
        self.mll1.setCurrentMesh(mesh)
        layerId = self.mll1.getCurrentLayer()
        if layerId < 0:
            return None, None
        layerName = self.mll1.getLayerName(layerId)
        return layerName, layerId
