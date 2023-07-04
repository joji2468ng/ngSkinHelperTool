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

# ngSkinTools2 modules
import ngSkinTools2.mllInterface
from ngSkinTools2.api import layers
from ngSkinTools2.api.session import session


class NgSkinControlV2(CopyPasteInfluence):
    VERSION = "ngSkinTools2"

    def __init__(self):
        super(NgSkinControlV2, self).__init__()
        self.mll2 = ngSkinTools2.mllInterface.MllInterface()

    def __str__(self):
        return self.VERSION

    def getInfluenceData(self):
        self.mll2.setCurrentMesh(self.mesh)
        listInfInfo = json.loads(self.mll2.ngSkinLayerCmd(q=True, influenceInfo=True))
        infPaths = [inf["path"].split("|")[-1] for inf in listInfInfo]
        infIndexes = [inf["index"] for inf in listInfInfo]

        infIndexKey = dict(list(zip(infIndexes, infPaths)))
        infNameKey = dict(list(zip(infPaths, infIndexes)))
        return infIndexKey, infNameKey

    def getLayerData(self):
        layerDict = {}
        layers = self.mll2.listLayers()
        for i in layers:
            layerDict[i["name"]] = i["id"]
        return layerDict

    def getUsedInfluenceData(self, indentKey, nameKey):
        srcLayer = layers.Layer(self.mesh, self.srcLayerID)
        infId = srcLayer.get_used_influences()
        infName = [indentKey[idInt] for idInt in infId]
        return infName, infId

    def copyWeights(self, srcInfID):
        # copy or cut weights from a specific joint on the source layer
        srcLayer = layers.Layer(self.mesh, self.srcLayerID)

        operation = self._getPasteOperation()
        weightClip = ngSkinTools2.api.copy_paste_weights
        if operation is "cut":
            weightClip.cut_weights(srcLayer, [srcInfID])
        else:
            weightClip.copy_weights(srcLayer, [srcInfID])

        maskWeight = None
        if self.mask:
            maskWeight = srcLayer.get_weights("mask")
        return weightClip, maskWeight

    def pasteWeights(self, weightClip, maskWeight, dstInfID):
        operation = self._getPasteOperation()
        dstLayer = layers.Layer(self.mesh, self.dstLayerID)

        # paste weights to the destination layer with a copied weights
        weightClip.paste_weights(dstLayer, operation, influences=[dstInfID])

        # apply mask weighs if checked
        if maskWeight:
            self.mll2.setLayerMask(self.dstLayerID, maskWeight)

        # update all influences in the list
        session.events.influencesListUpdated.emit()

    def _getPasteOperation(self):
        operation = None
        func = ngSkinTools2.api.copy_paste_weights
        if self.operation == "replace":
            operation = func.PasteOperation.replace
        elif self.operation == "add":
            operation = func.PasteOperation.add
        elif self.operation == "subtract":
            operation = func.PasteOperation.subtract
        elif self.operation == "cut":
            operation = self.op
        return operation

    def getCurrentLayer(self):
        mesh = utils.getNgSkinnedMesh(mode=1)[0]
        if mesh is None:
            return None, None

        self.setSelectedGeo(mesh)
        self.mll2.setCurrentMesh(mesh)
        layerId = self.mll2.getCurrentLayer()
        if layerId < 0:
            return None, None

        lay = layers.Layer.load(mesh, layerId)
        layerName = lay.name
        return layerName, layerId