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

# ngSkinTools2 modules
import ngSkinTools2.mllInterface
from ngSkinTools2.api import layers, target_info, tools, plugin
from ngSkinTools2.api.session import session

from rig_tools.core import geometry
from rig_tools.util import context


class RegionWeight(RegionWeightFactory):

    def __init__(self, layerName, geo=None, components=None, joints=None, mll=None):
        super(RegionWeight, self).__init__(layerName, geo, components, joints, mll)

        # Create an instance of the Layers class for the specified geometry.
        self.lays = layers.Layers(self.geo)
        self.layerObj = None

    def setupLayer(self):
        """Retrieves the layer ID associated with a specific layer name for the specified geometry.

        :return: The layer ID if found, otherwise None.
        """
        # Find layer with matching name
        for layObj in self.lays.list():
            if self.layerName == layObj.name:
                self.layerObj = layObj
                return

        self.layerObj = self.lays.add(name=self.layerName)

    def _getInfluences(self):
        influences = {}
        for ii in target_info.list_influences(self.geo):
            path = cmds.ls(ii.path)[0]
            influences[path] = ii.logicalIndex
        return influences

    def postProcess(self):
        # fill transparency
        tools.fill_transparency(self.layerObj)

        # Set the current layer to the retrieved or created layer by passing the layer ID.
        self.layerObj.set_current()

        cmds.select(cl=True)

        # Update the layer list on UI
        selection = cmds.ls(self.geo)
        cmds.select(cl=True)
        session.events.nodeSelectionChanged.emit()
        cmds.select(selection)
        session.events.nodeSelectionChanged.emit()

    def run(self):
        """Runs the main execution of the script. Adds missing joints, sets up the layer,
        retrieves influence information, finds the joint closest to each component,
        and sets influence weights for each vertex accordingly.

        :return: None
        """
        # Prepare for the main process
        self.setupLayer()
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
                self.layerObj.set_weights(influenceIndex, weights)
        self.postProcess()


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
        self.mll = ngSkinTools2.mllInterface.MllInterface()

    def postProcess(self, layerId):
        tools.fill_transparency(layerId)

        # update all influences in the list
        session.events.targetChanged.emitIfChanged()
        session.events.currentLayerChanged.emitIfChanged()
        session.events.layerListChanged.emitIfChanged()
        session.events.influencesListUpdated.emit()

    def setSquint(self):
        factory = RegionWeight(
            'Squints',
            self.geo,
            self.components,
            self.joints or cmds.ls("L_bind_squint??_JNT"),
            self.mll
        )
        layerId = factory.run()
        self.postProcess(layerId)

    def setEyelid(self):
        factory = RegionWeight(
            'Lids',
            self.geo,
            self.components,
            self.joints or cmds.ls("L_bind_???Lid_*JNT"),
            self.mll
        )
        layerId = factory.run()
        self.postProcess(layerId)

    def setSocket(self):
        factory = RegionWeight(
            'Sockets',
            self.geo,
            self.components,
            self.joints or cmds.ls("L_bind_???Socket_*JNT"),
            self.mll
        )
        layerId = factory.run()
        self.postProcess(layerId)

    def setLip(self):
        factory = RegionWeight(
            'Lip',
            self.geo,
            self.components,
            self.joints or cmds.ls("?_bind_???Lip_*JNT"),
            self.mll
        )
        layerId = factory.run()
        self.postProcess(layerId)

    def setLipScale(self):
        factory = RegionWeight(
            'LipScale',
            self.geo,
            self.components,
            self.joints or cmds.ls("?_bind_???LipScale_*JNT"),
            self.mll
        )
        layerId = factory.run()
        self.postProcess(layerId)

    def setBrow(self):
        factory = RegionWeight(
            'Brow',
            self.geo,
            self.components,
            self.joints or cmds.ls("?_bindBrow_*JNT"),
            self.mll
        )
        layerId = factory.run()
        self.postProcess(layerId)

    def setBrowTwist(self):
        factory = RegionWeight(
            'BrowTwist',
            self.geo,
            self.components,
            self.joints or cmds.ls("?_bindBrowTwist_*JNT"),
            self.mll
        )
        layerId = factory.run()
        self.postProcess(layerId)
