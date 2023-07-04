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


# ngSkinTools1 modules
if utils.IS_NG1:
    import ngSkinTools.influenceMapping
    import ngSkinTools.mllInterface
    import ngSkinTools.selectionState
    import ngSkinTools.ui.components.influencePrefixSuffixSelector
    import ngSkinTools.ui.events
    import ngSkinTools.ui.layerDataModel
    import ngSkinTools.ui.mainwindow
    import ngSkinTools.ui.tabMirror
    import ngSkinTools.ui.uiWrappers


class NgControlV1(MirrorBase):

    VERSION = "ngSkinTools1"
    VAR_PREFIX = "ngSkinToolsMirror_mirroringOptions"
    IGNORE_PREFIX = "ngSkinToolsInfluencePrefixSuffixSelector"

    def __init__(self, parent=None):
        super(NgControlV1, self).__init__(parent)

        self.info = PrintStatus()
        self.progressStatus = False

        _ui = ngSkinTools.ui
        _infComp = _ui.components.influencePrefixSuffixSelector
        self.mll1 = ngSkinTools.mllInterface.MllInterface()
        self.infPrefixSuffixSelector = _infComp.InfluencePrefixSuffixSelector()

        cmds.radioCollection()

        self.mirrorWidth = 0.1
        self.mirrorWeights = True
        self.mirrorMask = True
        self.mirrorDq = True
        self.mirrorDirection = 1
        self.mirrorDistanceError = 0.001
        self.mirrorIgnorePrefixMode = 1

    def __str__(self):
        return self.VERSION

    def setSkinMesh(self, geo):
        self.mll1.setCurrentMesh(geo)

        if not self.mll1.getLayersAvailable():
            self.parent.displayBar.errorNoSkinLayer(geo)
            return None

    def getNumberOfLayers(self, geos):
        """Get the number of layers existing in the geo

        :param
            geos: list
        :return: int
        """
        numberOfAllLayers = 0
        for geo in geos:
            self.setSkinMesh(geo)
            layers = self.mll1.ngSkinLayerCmd(q=True, listLayers=True)
            numLayers = len(layers) / 3
            numberOfAllLayers = numberOfAllLayers + numLayers
        return numberOfAllLayers

    def addTagName(self, mesh, suffix="NoMirror"):
        """Add a tag name to the selected layer name to avoid mirroring during operations.

        :param
            suffix: str
                Tag name which adds to the layer name
        """
        # get a layer name with layer id
        self.setSkinMesh(mesh)
        layerId = self.mll1.getCurrentLayer()
        layerName = self.mll1.getLayerName(layerId)

        # skip if layer name has a tag name
        if suffix in layerName:
            return

        # generate a tag name
        taggedName = "{}_{}".format(layerName, suffix)

        # set a new layer name to selected-layer
        self.mll1.setLayerName(layerId, taggedName)

        # update the list layer
        ngSkinTools.ui.events.LayerEvents.nameChanged.emit()

    def setConfigureMapper(self):
        """InfluenceMapping

        :return: dict
            mapper data
        """
        mll = ngSkinTools.selectionState.mll
        mapper = ngSkinTools.influenceMapping.InfluenceMapping()
        mapper.mirrorMode = True
        mapper.manualOverrides = mll.getManualMirrorInfluences()
        mapper.sourceInfluences = mll.listInfluenceInfo()
        axis = mll.getMirrorAxis()
        mapper.distanceMatchRule.mirrorAxis = 0 if axis is None else 'xyz'.index(axis)
        mapper.distanceMatchRule.maxThreshold = self.mirrorDistanceError

        def parseCommaValue(values):
            return [value.strip() for value in values.split(",")]

        mapper.calculate()
        self.mll1.configureInfluencesMirrorMapping(mapper.mapping)
        return mapper

    def mirror(self, geo, numberOfAllLayers):
        """The weights of the mesh will be mirrored across all layers.
        """
        self.preProcess(geo)

        with self.mll1.batchUpdateContext():
            trigger = True
            for i, (layerId, layerName, _) in enumerate(self.mll1.listLayers(), 1):
                # display the current progress on the screen
                currentNum = float(i)
                progressVal = 100.0 * (currentNum / numberOfAllLayers)
                self.parent.progressBar.setValue(progressVal)

                # ignore a mirror function towards the name tagged
                for noMirror in self.noMirrorList:
                    if noMirror in layerName:
                        self.info.setMessage("Ignore a mirror: {}".format(layerName))
                        trigger = False
                        continue

                # mirror weights
                if trigger:
                    self.mll1.mirrorLayerWeights(layerId,
                                                 mirrorWidth=self.mirrorWidth,
                                                 mirrorLayerWeights=self.mirrorWeights,
                                                 mirrorLayerMask=self.mirrorMask,
                                                 mirrorDualQuaternion=self.mirrorDq,
                                                 mirrorDirection=self.mirrorDirection)
                trigger = True
        ngSkinTools.ui.events.LayerEvents.influenceListChanged.emit()

        self.postProcess()

