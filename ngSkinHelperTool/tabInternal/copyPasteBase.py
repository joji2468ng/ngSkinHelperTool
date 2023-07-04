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

        Provides an interface for copying specific influences from a source layer,
        then paste to a destination layer with one of the options among ["replace", "add", "subtract" or "cut"].

        Features:
        - Choosing option whether applying mask weights or not during a copy paste process.
        - Coping and paste with multi-replace tokens for an influence name in a destination layer.
        - Quickly accessing to the Preset Menu list that contains the pairs of search-replace strings
          for assigning them to a tableList widget.
        - Automatically detecting unused ngSkinLayers in the scene during opening the tool,
          the button that pops up on top of the window, can delete them by user.
          Existing many unused layer data in a scene might become a nightmare with a maya file size.
          it's going to be a huge file size.

:Revisions:
"""
# Built-in
from builtins import zip
import logging

# Third Party
from maya import cmds

# Reelfx modules

from rig_tools.tool.ngSkinHelperTool.util import utils


# ----------------------------------------------------------------- GLOBALS --#
log = logging.getLogger(__name__)


class CopyPasteInfluence(object):

    def __init__(self, **kwargs):
        """Copy and paste object.

        # To copy the layer data for the stumpLeg segment
        func = CopyPasteInfluence(layerNames=['UpperLeg','UpperLegBack'],
                                  mesh='body_REN',
                                  searchReplace=[['_JNT', 'Back_JNT']],
                                  mask=True,
                                  operation='replace')

        Args:
            layerNames (list):
                Both source and destination layer names to copy and paste the layer data.
            mesh (str):
                Name of a skinned mesh
            searchReplace (list):
                Token to replace a joint name. Multiple list possible.
                ex: [["_L", "_R"], ["1", "2"]]
                    result: joint1_L  >>> joint2_R

                you can put None into the searchReplace list if you don't want to replace name
            mask (bool):
                Copying and paste a mask weights or not.
            operation (str)
                One of the names of paste operation mode from ['replace', 'add', 'subtract', 'cut']
        """
        self.layerNames = kwargs.get('layerNames', kwargs.get('ln', None))
        self.mesh = kwargs.get('mesh', kwargs.get('m', None))
        self.searchReplace = kwargs.get('searchReplace', kwargs.get('sr', None))
        self.operation = kwargs.get('operation', kwargs.get('op', 'replace'))
        self.mask = kwargs.get('maskWeight', kwargs.get('mask', True))

        self.srcLayerID = None
        self.dstLayerID = None
        self.remapInfluences = {}
        self.layerWeights = {}
        self.missingInfluences = []
        self.numberOfMatched = 0

    def getInfluenceData(self):
        pass

    def getLayerData(self):
        pass

    def getUsedInfluenceData(self, indenKey, nameKey):
        pass

    def copyWeights(self, srcInfID):
        pass

    def pasteWeights(self, weightClip, maskWeight, dstInfID):
        pass

    def setSelectedGeo(self, mesh=None):
        if mesh is None:
            sel = cmds.ls(selection=True, type="transform")
            if sel:
                self.mesh = sel[0]
            else:
                self.mesh = None
        else:
            self.mesh = mesh

    def _getIdFromSpecificLayers(self):
        layerID = []
        layerDict = self._getLayerData()
        for lay in [self.srcLayer, self.tgtLayer]:
            idInt = layerDict.get(lay)
            if not idInt:
                log.error("No such layer: %s", lay)
                return
            layerID.append(idInt)
        return layerID[0], layerID[1]

    def _replaceName(self, target):
        if not self.searchReplace:
            return None

        for token in self.searchReplace:
            if token is None:
                return target
            target = target.replace(*token)
        return target

    def getNumberMatchedJoint(self, versionObj):
        indentKey, nameKey = versionObj.getInfluenceData()
        infNames, infIDs = versionObj.getUsedInfluenceData(indentKey, nameKey)
        remapData = versionObj.storeRemapData(infIDs, infNames, nameKey)
        return len(remapData.values())

    def setData(self, data=None):
        self.mesh = data['mesh']
        self.operation = data['method']
        self.searchReplace = data['token']
        self.mask = data['mask']

        layers = data['layer']
        if layers is None or len(layers) is not 2:
            cmds.error("There's no layers")
        self.srcLayerID = layers[0]
        self.dstLayerID = layers[1]

    def storeRemapData(self, infIdList, infNameList, nameKey):
        remapData = {}
        for usedSrcIdInt, usedSrcJnt in zip(infIdList, infNameList):
            dstJnt = self._replaceName(usedSrcJnt)

            if not dstJnt:
                continue

            try:
                dstJntID = nameKey[dstJnt]
                if dstJntID:
                    self.numberOfMatched += 1

            except KeyError:
                log.warning("%s is not an influence of %s", dstJnt, self.mesh)
                self.missingInfluences.append(dstJnt)
                continue
            remapData[usedSrcIdInt] = dstJntID
        self.searchReplace = None
        return remapData
