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

# Local modules
from rig_tools.tool.ngSkinHelperTool.util import utils
from rig_tools.tool.ngSkinHelperTool.tabInternal.convertBase import ConvertBase

if utils.NG1_VERSION:
    import ngSkinTools.mllInterface

# ngSkinTools2 modules
if utils.IS_NG2:
    import ngSkinTools2.api as ngst_api
    from ngSkinTools2.decorators import undoable
    from ngSkinTools2.log import getLogger
    from ngSkinTools2.api.session import session
    import ngSkinTools2.mllInterface


class NgControlV2(ConvertBase):

    VERSION = "ngSkinTools2"
    NODES = ('ngst2MeshDisplay', 'ngst2SkinLayerData')

    def __init__(self, parent):
        super(NgControlV2, self).__init__()

        # self.target = None
        self.parent = parent

        self.mll1 = ngSkinTools.mllInterface.MllInterface()
        self.mll2 = ngSkinTools2.mllInterface.MllInterface()

        self.mask = ngSkinTools2.mllInterface.NamedPaintTarget.MASK
        self.dq = ngSkinTools2.mllInterface.NamedPaintTarget.DUAL_QUATERNION

    def __str__(self):
        return self.VERSION

    def cleanup(self):
        self._cleanup(self.NODES)

    def copyLayer(self, oldLayerId, newLayerId, state=None):
        _layer = ngst_api.layers.Layer(self.target, oldLayerId, state=state)
        infl = _layer.get_used_influences()
        opacity = _layer.__get_state__("opacity")
        enabled = _layer.__get_state__("enabled")
        maskWeights = _layer.get_weights(self.mask)
        dqWeights = _layer.get_weights(self.dq)

        for inf in infl:
            weights = _layer.get_weights(inf)
            self.mll1.setInfluenceWeights(newLayerId, inf, weights)

        self.mll1.setLayerOpacity(newLayerId, opacity)
        self.mll1.setLayerEnabled(newLayerId, enabled)
        self.mll1.setInfluenceWeights(newLayerId, "mask", maskWeights)
        self.mll1.setInfluenceWeights(newLayerId, "dq", dqWeights)

    def convertProcess(self):
        # create init layer for v1
        self.mll1.setCurrentMesh(self.target)
        self.mll1.initLayers()

        # get layer data of version2 on the target
        self.mll2.setCurrentMesh(self.target)
        layerList = self.mll2.listLayers()

        layerDict = {}
        for i in layerList:
            layerDict[i["id"]] = i
        layerSortedId = sorted(layerDict.keys())

        # get list layers
        with self.mll1.batchUpdateContext():
            for i, layId in enumerate(layerSortedId, 1):
                # display the current progress on the screen
                currentNum = float(i)
                progressVal = 100.0 * (currentNum / len(layerList))
                self.parent.progressBar.setValue(progressVal)

                layerId = int(layId)
                layerName = layerDict[layId]["name"]

                # create new layer then parent it to the right place
                newLayerId = self.mll1.createLayer(layerName, forceEmpty=True)
                self.copyLayer(layerId, newLayerId, state=layerDict[layId])

            for layId in layerSortedId:
                layerParent = layerDict[layId]["parentId"]
                if layerParent is None:
                    continue
                self.mll1.setLayerParent(int(layId), layerParent)