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
from maya import cmds, mel

# Local modules
from rig_tools.tool.ngSkinHelperTool.util import utils
from rig_tools.tool.ngSkinHelperTool.tabInternal.convertBase import ConvertBase

import ngSkinTools.mllInterface

import ngSkinTools2.mllInterface
import ngSkinTools2.api as ngst_api


# ----------------------------------------------------------------- GLOBALS --#
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class NgControlV1(ConvertBase):
    VERSION = "ngSkinTools1"
    NODES = ('ngSkinLayerDisplay', 'ngSkinLayerData')

    def __init__(self, parent):
        super(NgControlV1, self).__init__()

        self.target = None
        self.parent = parent
        self.progressStatus = False

        self.mll2 = ngSkinTools2.mllInterface.MllInterface()

    def __str__(self):
        return self.VERSION

    def getLayerInfluences(self, layerId):
        command = "ngSkinLayer -id {0} -q -listLayerInfluences -activeInfluences {1}"
        influences = mel.eval(command.format(layerId, self.target)) or []
        return zip(influences[0::2], map(int, influences[1::2]))

    def getLayerWeights(self, layerId, infl):
        command = "ngSkinLayer -id {0:d} -paintTarget {1} -q -w {2:s}"
        return mel.eval(command.format(layerId, infl, self.target))

    def cleanup(self):
        """Delete V1 data from provided list of nodes. Must be a v1 compatible target
        :type selection: list[string]
        """
        self._cleanup(self.NODES)

    def copyLayer(self, oldLayerId, newLayer, state=None):
        """
        :type oldLayerId: int
        :type newLayer: ngSkinTools2.api.layers.Layer
        """
        newLayer.opacity = mel.eval("ngSkinLayer -id {0:d} -q -opacity {1:s}".format(oldLayerId, self.target))
        newLayer.enabled = mel.eval("ngSkinLayer -id {0:d} -q -enabled {1:s}".format(oldLayerId, self.target))

        newLayer.set_weights(ngst_api.NamedPaintTarget.MASK, self.getLayerWeights(oldLayerId, "mask"))
        newLayer.set_weights(ngst_api.NamedPaintTarget.DUAL_QUATERNION, self.getLayerWeights(oldLayerId, "dq"))

        for inflPath, inflId in self.getLayerInfluences(oldLayerId):
            log.debug("importing influence %s for layer %s", inflPath, oldLayerId)
            weights = self.getLayerWeights(oldLayerId, inflId)
            newLayer.set_weights(inflId, weights)

    def convertProcess(self):
        if not self.has_v1():
            return False

        layers = ngst_api.init_layers(self.target)
        layerList = cmds.ngSkinLayer(self.target, q=True, listLayers=True)
        layerList = [layerList[i: i + 3] for i in range(0, len(layerList), 3)]

        layerDict = {}
        for layerId, layerName, layerParent in layerList:
            layerDict[int(layerId)] = [layerName, layerParent]
        layerSortedId = sorted(layerDict.keys())

        with ngst_api.suspend_updates(self.target):
            for i, layId in enumerate(layerSortedId, 1):
                # display the current progress on the screen
                currentNum = float(i)
                progressVal = 100.0 * (currentNum / len(layerList))
                self.parent.progressBar.setValue(progressVal)

                layerId = int(layId)
                layerName = layerDict[layId][0]

                # crate new layer
                newLayer = layers.add(name=layerName, forceEmpty=True)
                self.copyLayer(layerId, newLayer)

            for layId in layerSortedId:
                layerParent = layerDict[layId][1]
                if layerParent is 0:
                    continue
                self.mll2.setLayerParent(int(layId), layerParent)
