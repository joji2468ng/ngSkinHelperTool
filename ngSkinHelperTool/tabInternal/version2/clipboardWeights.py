
import numpy as np

import ngSkinTools2
from ngSkinTools2.api import plugin
from ngSkinTools2.api.session import session

from rig_tools.tool.ngSkinHelperTool.util import utils


class ClipboardOperation(object):

    REPLACE = 'pasteReplace'
    ADD = 'pasteAdd'
    SUBTRACT = 'pasteSubtract'

    def __init__(self):
        self.weightClip = None

        skinNode = session.state.selectedSkinCluster
        if skinNode is None:
            return

    def copyWeights(self, operation):
        # copy or cut weights from a specific joint on the source layer
        layer = session.state.currentLayer.layer
        influences = session.context.selectedInfluences()

        weightClip = layer.get_weights(influences[0])
        if operation == "cut":
            array = np.array([weightClip, weightClip])
            weightList = np.subtract(array[1], array[0]).tolist()
            layer.set_weights(influences[0], weightList)

        self.weightClip = weightClip

    def pasteWeights(self, operation, copyWeightList):
        layer = session.state.currentLayer.layer
        influences = session.context.selectedInfluences()
        pasteWeightList = layer.get_weights(influences[0])

        weightList = None
        if operation == self.REPLACE:
            weightList = copyWeightList
        elif operation == self.ADD:
            array = np.array([copyWeightList, pasteWeightList])
            weightList = np.clip(np.sum(array, axis=0), 0.0, 1.0).tolist()
        elif operation == self.SUBTRACT:
            array = np.array([copyWeightList, pasteWeightList])
            weightList = np.subtract(array[1], array[0]).tolist()

        # paste weights to the destination layer with a copied weights
        layer.set_weights(influences[0], weightList)

        # update all influences in the list
        session.events.influencesListUpdated.emit()
