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
import maya.cmds as cmds

# Custom moduels
from rig_tools.tool.ngSkinHelperTool.tabInternal.assignWeightsBase import RegionWeightFactory

# ngSkinTools1 modules
import ngSkinTools.mllInterface

from rig_tools.core import geometry
from rig_tools.util import context


class RegionWeight(RegionWeightFactory):

    def __init__(self, layerName, geo=None, components=None, joints=None, mll=None):
        super(RegionWeight, self).__init__(layerName, geo, components, joints, mll)

    def _getLayerNameId(self):
        """Retrieves the layer ID associated with a specific layer name for the specified geometry.

        :return: The layer ID if found, otherwise None.
        """
        # Create an instance of the Layers class for the specified geometry.
        layers = self.mll.ngSkinLayerCmd(q=True, listLayers=True)

        layerId = None
        # Iterate over each layer object in the list of layers.
        for i in range(0, len(layers), 3):
            layerName = layers[i:i+3][1]
            if not self.layerName == layerName:
                continue
            # If the layer name matches, assign the layer ID to the layerId variable.
            layerId = layers[i:i + 3][0]
        return layerId

    def setupLayer(self):
        """Sets up the layer by creating it if it doesn't exist
        and setting it as the current layer.

        :return: None
        """
        # Get the layer ID associated with the specified layer name.
        layerId = self._getLayerNameId()
        if not layerId:
            # If the layer ID is not found, create the layer with the specified layer name.
            layerId = self.mll.createLayer(self.layerName, forceEmpty=True)

        return layerId

    def _getInfluences(self):
        influences = {}
        for ii in self.mll.listInfluenceInfo():
            infPath = cmds.ls(ii.path)[0]
            influences[infPath] = ii.logicalIndex
        return influences

    def run(self):
        """Runs the main execution of the script. Adds missing joints, sets up the layer,
        retrieves influence information, finds the joint closest to each component,
        and sets influence weights for eaqch vertex accordingly.

        :return: None
        """
        # Prepare for the main process
        layerId = self.setupLayer()
        self.addMissingJoints()

        # Retrieve influence information by creating a dictionary that maps influence paths to their logical indices.
        influences = self._getInfluences()
        closestMap = self._findJointClosestToComp()
        numberOfVertices = cmds.polyEvaluate(self.geo, vertex=True)

        # Perform the following steps within an undo context to enable undo functionality.
        with context.UndoContext():
            for jnt, vertexList in closestMap.items():
                # Get the logical index of the current joint from the influences dictionary.
                influenceIndex = influences[jnt]

                # Create a weight list with zeros for all vertices.
                weights = [0] * numberOfVertices

                # Set the weight to 1.0 for each vertex in the vertex list.
                for vtx in vertexList:
                    i = geometry.componentToIndex(vtx)
                    weights[i] = 1.0

                # Set the influence weights for the current joint
                self.mll.setInfluenceWeights(layerId, influenceIndex, weights, True)


class FaceRegionWeights:

    def __init__(self, geo=None, components=None, joints=None):
        """Class for setting region weights on a face geometry.

        Args:
            geo (str): The name of the face geometry.
            components (list, optional): List of components (vertices) to set region weights on.
            joints (list, optional): List of joint names to be used for setting region weights.
        """
        self.geo = geo
        self.components = components
        self.joints = joints
        self.mll = ngSkinTools.mllInterface.MllInterface()

    def postProcess(self):
        # update all influences in the list
        pass

    def setSquint(self):
        factory = RegionWeight(
            'Squints',
            self.geo,
            self.components,
            self.joints or cmds.ls("L_bind_squint??_JNT"),
            self.mll
        )
        factory.run()

    def setEyelid(self):
        factory = RegionWeight(
            'Lids',
            self.geo,
            self.components,
            self.joints or cmds.ls("L_bind_???Lid_*JNT"),
            self.mll
        )
        factory.run()

    def setSocket(self):
        factory = RegionWeight(
            'Sockets',
            self.geo,
            self.components,
            self.joints or cmds.ls("L_bind_???Socket_*JNT"),
            self.mll
        )
        factory.run()

    def setLip(self):
        factory = RegionWeight(
            'Lip',
            self.geo,
            self.components,
            self.joints or cmds.ls("?_bind_???Lip_*JNT"),
            self.mll
        )
        factory.run()

    def setLipScale(self):
        factory = RegionWeight(
            'LipScale',
            self.geo,
            self.components,
            self.joints or cmds.ls("?_bind_???LipScale_*JNT"),
            self.mll
        )
        factory.run()

    def setBrow(self):
        factory = RegionWeight(
            'Brow',
            self.geo,
            self.components,
            self.joints or cmds.ls("?_bindBrow_*JNT"),
            self.mll
        )
        factory.run()

    def setBrowTwist(self):
        factory = RegionWeight(
            'BrowTwist',
            self.geo,
            self.components,
            self.joints or cmds.ls("?_bindBrowTwist_*JNT"),
            self.mll
        )
        factory.run()
