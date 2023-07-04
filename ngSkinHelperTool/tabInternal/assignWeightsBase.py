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
# Maya module
import maya.cmds as cmds
import maya.mel as mel
from maya.api import OpenMaya

# Third module
from ngSkinTools2.api import target_info, layers

# Custom module
from rig_tools.core import geometry
from rig_tools.util import argument
from rig_tools.util import context


class RegionWeightFactory(object):

    def __init__(self, layerName, geo=None, components=None, joints=None, mll=None):
        """A class for calculating region weights for a given layer and geometry.

        Args:
            layerName (str): The name of the layer to set up region weights for.
            geo (str): The name of the geometry to set up region weights on.
            components (list): A list of components (vertices) to set up region weights for.
            joints (list): A list of joints to set up region weights with.

        Attributes:
            layerName (str): The name of the layer to set up region weights for.
            geo (str): The name of the geometry to set up region weights on.
            components (list): A list of components (vertices) to set up region weights for.
            joints (list): A list of joints to set up region weights with.
            mll (MllInterface): An instance of the MllInterface class.
        """
        self.layerName = layerName
        self.geo = geo
        self.components = components
        self.joints = joints

        self._parseJoints()
        self._parseComponents()
        self._parseMeshs()

        self.mll = mll
        self.mll.setCurrentMesh(self.geo)

        if not self.mll.getLayersAvailable():
            self.mll.initLayers()

    def _parseJoints(self):
        """Parses and retrieves joint objects from the current selection in the scene.
        :return:
        """
        if self.joints is None:
            self.joints = cmds.ls(selection=True, type="joint")

    def _parseComponents(self):
        """Parses and retrieves components (vertices) from the current selection in the scene.
         Raises an exception if no vertices are specified.

         :return: None
         :raises ValueError: If no vertices are specified.
         """
        # Retrieve a list of component objects(vertices) from the current selection
        if self.components is None:
            self.components = cmds.ls(selection=True, type="float3")

        # Query and update with the components If it is an object set,
        elif isinstance(self.components, basestring):
            if cmds.objectType(self.components, isType='objectSet'):
                self.components = cmds.sets(self.components, query=True)

        self.components = cmds.filterExpand(self.components or [], selectionMask=31)

        # raises an exception if no vertices are specified
        if not self.components:
            raise ValueError("Must specify vertices bounding the region.")

    def _parseMeshs(self):
        """Parses and retrieves the mesh associated with the specified components.
        Raises exceptions if there are multiple meshes, the specified mesh doesn't exist,
        or the specified mesh is not a valid mesh object.

        :return: None
        :raises ValueError: If there are multiple meshes, the specified mesh doesn't exist,
                            or the specified mesh is not a valid mesh object.
        """
        # Create a set of meshes by iterating over the components and getting the associated mesh.
        meshes = list(set([
            geometry.getMeshFromComponent(c)
            for c in self.components
        ]))

        # Check if there are multiple meshes.
        if len(meshes) > 1:
            raise ValueError("Can only set region weights on a single mesh.")

        # If self.geo is None, assign it the first mesh in the set.
        self.geo = self.geo or meshes[0]

        # Check if self.geo is in the set of meshes.
        if self.geo not in meshes:
            raise ValueError("Must specify vertices from the specified mesh.")

        # Check if the specified mesh exists.
        if not cmds.objExists(self.geo):
            raise ValueError("Specified mesh does not exist: '{}'.".format(geo))

        # Check if the specified mesh is a valid mesh object.
        if not argument.getMDagPath(self.geo, api2=True).hasFn(OpenMaya.MFn.kMesh):
            raise ValueError("Must specify a mesh.")

    def addMissingJoints(self):
        """Adds missing joints to the skin cluster associated with the specified mesh.

        :return: None
        :raises ValueError: If specified joints do not exist, the region selection is invalid,
                            or the specified mesh is not skinned.
        """
        joints_exist = [cmds.objExists(jnt) for jnt in self.joints]

        if not all(joints_exist):
            missing_joints = ', '.join(itertools.compress(self.joints, joints_exist))
            raise ValueError("Specified joints do not exist: '{}'.".format(missing_joints))

        # Check if the number of selected components matches the expected number based on the number of joints.
        if len(self.components) != (len(self.joints) * 2):
            raise ValueError("Must select a region with one edge loop per joint.")

        # Get the skin cluster associated with the specified mesh
        scls = mel.eval('findRelatedSkinCluster "{}"'.format(self.geo))
        if not scls:
            raise ValueError("'{}' is not skinned.".format(self.geo))

        # Retrieve the influences (joints) connected to the skin cluster.
        sclsMatrix = argument.Plug.make(scls, 'matrix').asString()
        influences = cmds.listConnections(sclsMatrix)

        # Find the missing joints that are not already influences of the skin cluster.
        missing_joints = [jnt for jnt in self.joints if not jnt in influences]

        # If there are missing joints, add them as influences to the skin cluster with weight 0.0.
        if missing_joints:
            cmds.skinCluster(
                scls,
                edit=True,
                lockWeights=False,
                weight=0.0,
                addInfluence=missing_joints
            )

    def _distanceBetween(self, pntA, pntB):
        """Calculates the distance between two points in 3D space.

        :param pntA: The first point.
        :param pntB: The second point.
        :return: The distance between the two points.
        """
        pntA = argument.parseVector(pntA)
        pntB = argument.parseVector(pntB)

        return (pntB - pntA).magnitude()

    def _findJointClosestToComp(self):
        """Finds the joint closest to each component

        :return: A dictionary mapping joints to their closest components.
        """
        # Get the spokes between the edge rings containing the components.
        spokes = geometry.getSpokesBetweenEdgeRings(self.components)

        vertices = {}
        # Find the joint closest to any component in each spoke.
        for jnt in self.joints:
            dist = None
            idx = None

            # Iterate over each spoke and find the nearest point index on the spoke for the current joint.
            for i, spoke in enumerate(spokes):
                ni = geometry.findNearestPointIndex(jnt, spoke)
                vtx = spoke[ni]
                d = self._distanceBetween(jnt, vtx)

                # Compare the distances and update the closest distance and component index if necessary.
                if dist is None or d < dist:
                    dist = d
                    idx = i
            # Store the closest component (spoke) for the current joint in the vertices dictionary.
            vertices[jnt] = spokes[idx]
        return vertices

