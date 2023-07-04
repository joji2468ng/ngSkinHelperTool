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
import re

# Maya modules
import maya.cmds as cmds
import maya.mel as mel

# Reelfx modules
from rig_tools.util import validate

# Local modules
from rig_tools.tool.ngSkinHelperTool.util import common

NG1_VERSION = "ngSkinTools1"
NG2_VERSION = "ngSkinTools2"

# ngSkinTools1 modules
IS_NG1 = False
if cmds.pluginInfo('ngSkinTools', query=True, registered=True):
    IS_NG1 = True

# ngSkinTools2 modules
IS_NG2 = False
if cmds.pluginInfo('ngSkinTools2', query=True, registered=True):
    IS_NG2 = True

log = logging.getLogger(__name__)


def getSkinnedMesh(mode=1):
    """Function that retrieves the currently selected mesh object

    :param mode: int
        1: selection mode
        2: all meshs that search all skinned-mesh in the scene
    :return: list
        a list containing ng-skined mesh
    """
    geo = []
    # seletion mode
    if mode == 1:
        sel = common.asList(cmds.ls(sl=True))
        geo.extend([g for g in sel if validate.isGeometry(g)])

    # all meshes mode that search all skinned-mesh in the scene
    elif mode == 2:
        namespaces = [cmds.listRelatives(i, p=True)[0] for i in cmds.ls("*:*", type="mesh", ni=True)]
        geoAll = [cmds.listRelatives(i, p=True)[0] for i in cmds.ls(type="mesh", ni=True)]

        # remove geometries with namespace
        for space in namespaces:
            geoAll.remove(space)

        geo = geoAll

    if not geo:
        return None

    skinGeo = [g for g in geo if isSkinnedMesh(g)]
    return skinGeo


def getNgSkinnedMesh(mode=1):
    skinGeo = getSkinnedMesh(mode)
    if not skinGeo:
        return None

    ngSkinGeo = [g for g in skinGeo if hasSkinLayer(g)]

    return ngSkinGeo


def isSkinnedMesh(geo):
    """This function checks if the input mesh has any skinCluster nodes attached to it or not

    :param geo: str
        a skinned mesh
    :return: bool
    """
    scls = mel.eval('findRelatedSkinCluster "{}"'.format(geo))
    if not scls:
        return False
    return True


def getUnusedNgSkinLayerData():
    """ Finds ngSkinLayerData not tied to any skinCluster
    :return: list
        a list for unusedNgLayerData
    """
    ngData1, ngData2 = None, None
    if IS_NG1:
        ngData1 = getAllNgSkinLayerData(version=1, inactive=True)

    if IS_NG2:
        ngData2 = getAllNgSkinLayerData(version=2, inactive=True)

    data = []
    if ngData1:
        data.extend(ngData1)
    elif ngData2:
        data.extend(ngData2)
    return data


def hasSkinLayer(mesh):
    scls = mel.eval('findRelatedSkinCluster "{}"'.format(mesh))
    if not scls:
        return False

    hasDataV1, hasDataV2 = False, False
    if IS_NG1:
        hasDataV1 = hasLayerData(mesh, version=1)
    if IS_NG2:
        hasDataV2 = hasLayerData(mesh, version=2)

    ngVersion = []
    if hasDataV1:
        ngVersion.append(NG1_VERSION)
    elif hasDataV2:
        ngVersion.append(NG2_VERSION)

    if not hasDataV1 and not hasDataV2:
        return False
    return True, ngVersion[0]


def hasLayerData(node, version=1):
    """Return True if `mesh` has ngSkin layer data."""

    if version == 1:
        from ngSkinTools.mllInterface import MllInterface

        if cmds.objExists(node) and cmds.objectType(node, isType="skinCluster"):
            scls = node
            mesh, = cmds.skinCluster(scls, query=True, geometry=True)
            mesh, = cmds.listRelatives(mesh, parent=True)
        else:
            mesh = node
            scls = mel.eval('findRelatedSkinCluster "{}"'.format(node))

        if not scls:
            return False

        mll = MllInterface()
        mll.setCurrentMesh(mesh)
        return mll.getLayersAvailable()

    elif version == 2:
        from ngSkinTools2.api import plugin
        return plugin.ngst2Layers(node, q=True, layerDataAttach=True)


def getToolVersion(mesh):
    _, version = hasSkinLayer(mesh)
    return version


def checkNgSkinToolsPlugins():
    global IS_NG1, IS_NG2
    IS_NG1 = False
    if cmds.pluginInfo('ngSkinTools', query=True, loaded=True):
        IS_NG1 = True
    else:
        try:
            cmds.pluginInfo('ngSkinTools', loaded=True)
            IS_NG1 = True
        except:
            pass

    IS_NG2 = False
    if cmds.pluginInfo('ngSkinTools2', query=True, loaded=True):
        IS_NG2 = True
    else:
        try:
            cmds.pluginInfo('ngSkinTools2', loaded=True)
            IS_NG2 = True
        except:
            pass

    return IS_NG1, IS_NG2


def loadNgModules(plugInName='ngSkinTools', *module_names):
    """
    Loads ngSkinTools modules if their corresponding plugins are loaded.
    :param
        plugIn: ['ngSkinTools', 'ngSkinTools2']
        module_names: variable number of module names to import
    :return: list of loaded module objects
    """
    loaded_modules = []

    for module_name in module_names:
        module_loaded = False

        # check if plugin is loaded
        if cmds.pluginInfo(plugInName, query=True, loaded=True):
            # fromlist argument is used to import the module by name.
            module = __import__(plugin_name + '.' + module_name, fromlist=[module_name])
            loaded_modules.append(module)
            module_loaded = True
            break

        # if plugin is not loaded, print a message
        if not module_loaded:
            print('Plugin for {} module is not loaded'.format(module_name))

    return loaded_modules


def getAllNgSkinLayerData(version=1, active=False, inactive=False):
    """
    Finds any ngSkinLayerNodes floating in the scene with no connections.

    If no arguments are passed or active and inactive are both False,
    All ngSkinLayerData nodes are returned.

    Args:
        active: bool
            Returns only ngSkinLayerData nodes tied to a skinCluster.

        inactive: bool
            Returns floating ngSkinLayerData that not tied to any skinCluster.

    :returns: Unused ngSkinLayerData found/deleted.
    :rtype: list(str)
    """
    data = None
    if version == 1:
        data = "ngSkinLayerData"
    elif version == 2:
        data = "ngst2SkinLayerData"

    ngSkinLayerData = cmds.ls(type=data)
    if (active and inactive) or (not active and not inactive):
        return ngSkinLayerData

    activeNodes = []
    inactiveNodes = []
    for node in ngSkinLayerData:
        if not cmds.listConnections(node, source=True, type="skinCluster"):
            inactiveNodes.append(node)
        else:
            activeNodes.append(node)

    if active:
        return activeNodes
    else:
        return inactiveNodes



def killScriptJob(functions, event=None):
    """ Kills all scriptJobs that call the specified function.
    Sometimes the saved id somehow gets moved or lost. This will use a name.

    :parameters:
        functions : callable | list(callable)
            The script or function call given to the script job.
        event : str
            The event string that triggers the job. (Optional)

    :return: list of all deleted jobs
    :type: list

    """
    jobs = []

    # Loop through all scriptJobs
    for job in cmds.scriptJob(listJobs=True):
        for func in common.asList(functions):
            if event:
                valid_event = False
                splitjob = re.findall("[A-Za-z0-9-_]+", job)
                for idx, text in enumerate(splitjob):
                    if text not in ('e', 'event'):
                        continue
                    jobEvent = splitjob[idx + 1]
                    if event == jobEvent:
                        valid_event = True
                        break
                if not valid_event:
                    continue

            jobCbStr = re.findall("<([A-Za-z0-9_<. ]+)>", str(job))
            if not jobCbStr:
                continue

            funcStr = re.findall("<([A-Za-z0-9_<. ]+)>", str(func))
            if not funcStr:
                continue

            if not (jobCbStr[0].rpartition(' ')[0]
                    == funcStr[0].rpartition(' ')[0]):
                continue

            jobs.append(job)

            # Kill it using the job ID.
            jobNum = job.partition(":")[0]
            cmds.evalDeferred(
                "cmds.scriptJob(kill={}, force=True)".format(jobNum))

    return jobs
