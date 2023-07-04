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
import os
import json
import logging

# Maya modules
from PySide2 import QtCore, QtWidgets, QtGui

# Local modules
from rig_tools.tool.ngSkinHelperTool.util import common, utils
from rig_tools.tool.ngSkinHelperTool.util.data import Data


# ----------------------------------------------------------------- GLOBALS --#
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class TreeWidgetReader(object):

    def __init__(self, treeWidget):
        """Class that reads data from a QTreeWidget and returns it as any data.
        It is designed to be used with a specific format of QTreeWidget items,

        :param treeWidget: QTreeWidget
        """
        self.tree = treeWidget
        self.currentData = []

    def getAllParentItem(self, currentItem):
        """All parents are listed in the given item.

        :param currentItem: QTreeWidgetItem
        :return: list
        """
        parents = []
        while currentItem.parent() is not None:
            currentItem = currentItem.parent()
            parents.append(currentItem)

        return parents

    def getParentItem(self, currentItem):
        """Get a single parent item in the given item

        :param currentItem: QTreeWidgetItem
        :return: QTreeWidgetItem or None
        """
        _parent = currentItem.parent()
        if _parent:
            return _parent

        return None

    def getCurrentData(self):
        item = self.tree.selectedItems()
        if not item:
            return None, None
        return item[0], item[0].text(0)

    def getItemType(self, item):
        if not item:
            return
        # Get the icon of the current item
        icon = item.icon(0)

        # Get the file name of the icon
        return icon.themeName()

    def getChildCount(self, parent):
        num = parent.childCount()
        return num

    def getItemData(self, item, id=None, types=None):
        itemData = item.data(0, QtCore.Qt.UserRole)
        if itemData:
            id = itemData["id"]

        newItemData = {}
        newItemData["name"] = item.text(0)
        newItemData["id"] = id
        newItemData["type"] = types

        if types == "group":
            newItemData["children"] = [{"layers": None}]
        else:
            newItemData["layers"] = []

        parent = self.getParentItem(item)
        if parent:
            newItemData["index"] = parent.indexOfChild(item)
            parentData = parent.data(0, QtCore.Qt.UserRole)
            newItemData["parentId"] = parentData["id"]
        else:
            newItemData["index"] = self.tree.indexOfTopLevelItem(item)
            newItemData["parentId"] = 0

        return newItemData

    def getAllPresetIdInTree(self, dic):
        idList = []
        if isinstance(dic, dict):
            for key, value in dic.items():
                for valueKey, valueVal in value.items():
                    if valueKey == "id":
                        idList.append(valueVal)

                    if valueKey == "children":
                        idList.extend(self.getAllIdInTree(valueVal))
        elif isinstance(dic, list):
            for item in dic:
                idList.extend(self.getAllIdInTree(item))
        return idList

    def getAllIdInTree(self, dic):
        idList = []
        if isinstance(dic, dict):
            for key, value in dic.items():
                if key == "id":
                    idList.append(value)

                if key == "children":
                    idList.extend(self.getAllIdInTree(value))
        elif isinstance(dic, list):
            for item in dic:
                idList.extend(self.getAllIdInTree(item))
        return idList

    def countId(self, dic):
        """Get a total number of ID in dictinary

        :param
            dic: dictinary of data
        :return: int
            a total number of id in the dictinary
        """
        count = 0
        if isinstance(dic, dict):
            for key, value in dic.items():
                if key == "id":
                    count += 1

                if key == "children":
                    count += self.countId(value)
        elif isinstance(dic, list):
            for item in dic:
                count += self.countId(item)
        return count

    def getAllChildren(self, item):
        children = []
        for i in range(item.childCount()):
            child = item.child(i)
            children.append(child)
            children += self.getAllChildren(child)
        return children

    def getLayerStructure(self):
        """Recursive function to get all items in the TreeWidget"""
        allItems = []

        # Recursive function to get all child items
        def getChildItems(treeItem):
            items = []
            for i in range(treeItem.childCount()):
                itemData = {}
                childItemData = treeItem.child(i).data(0, QtCore.Qt.UserRole)

                itemData["name"] = treeItem.child(i).text(0)
                itemData["id"] = childItemData["id"]
                itemData["type"] = childItemData["type"]
                itemData["index"] = treeItem.indexOfChild(treeItem.child(i))
                itemData["parentId"] = childItemData["parentId"]
                items.append(itemData)

                if childItemData["type"] == "layer":
                    subItems = getChildItems(treeItem.child(i))
                    if not subItems:
                        continue
                    for subIndex in range(len(subItems)):
                        allItems.append(subItems[subIndex])
            return items

        num = self.tree.topLevelItemCount()
        if num == 0:
            return None

        for i in range(num):
            itemData = {}

            topItem = self.tree.topLevelItem(i)
            topItemData = topItem.data(0, QtCore.Qt.UserRole)

            itemData["name"] = topItem.text(0)
            itemData["id"] = topItemData["id"]
            itemData["index"] = self.tree.indexOfTopLevelItem(topItem)
            itemData["parentId"] = topItemData["parentId"]
            itemData["type"] = topItemData["type"]
            allItems.append(itemData)

            if topItemData["type"] == "layer":
                subItems = getChildItems(topItem)
                if not subItems:
                    continue
                for subIndex in range(len(subItems)):
                    allItems.append(subItems[subIndex])

        return allItems

    def getSubTreeNodes(self, treeWidgetItem):
        """Returns all QTreeWidgetItems in the subtree rooted at the given node.
        :param
            treeWidgetItem: QTreeWidgetItem
            sumNum: a total number of existing items in widget
        :return:
            list of each data, a total number of items
        """
        nodes = []
        for i in range(treeWidgetItem.childCount()):
            itemData = {}
            childItemData = treeWidgetItem.child(i).data(0, QtCore.Qt.UserRole)

            itemData["name"] = treeWidgetItem.child(i).text(0)
            itemData["id"] = childItemData["id"]
            itemData["type"] = childItemData["type"]
            itemData["index"] = treeWidgetItem.indexOfChild(treeWidgetItem.child(i))
            itemData["parentId"] = childItemData["parentId"]
            if childItemData["type"] == "group":
                itemData["children"] = self.getSubTreeNodes(treeWidgetItem.child(i))
            elif childItemData["type"] == "preset":
                if "layers" in childItemData:
                    itemData["layers"] = childItemData["layers"]
            nodes.append(itemData)
        return nodes

    def getAllItems(self):
        """Returns all QTreeWidgetItems in the given QTreeWidget.
        :param
            types: type name of QTreeWidget
        :return:
            list of all items in QTreeWidget
        """
        allItems = {}

        num = self.tree.topLevelItemCount()
        if num == 0:
            return None

        for i in range(num):
            itemData = {}
            topItem = self.tree.topLevelItem(i)
            topItemData = topItem.data(0, QtCore.Qt.UserRole)

            itemData["name"] = topItem.text(0)
            itemData["id"] = topItemData["id"]
            itemData["index"] = self.tree.indexOfTopLevelItem(topItem)
            itemData["parentId"] = topItemData["parentId"]
            itemData["type"] = topItemData["type"]
            if topItemData["type"] == "group":
                itemData["children"] = self.getSubTreeNodes(topItem)

            allItems[itemData["name"]] = itemData
        return allItems


class TreeWidgetSetter(object):

    def __init__(self, treeWidgets):
        self.tree = treeWidgets
        self.getterPreset = TreeWidgetReader(self.tree["preset"])
        self.getterLayer = TreeWidgetReader(self.tree["layer"])

        customMenu = TreeWidgetContextMenu(self.tree)
        self.tree["preset"].customContextMenuRequested.connect(customMenu.showPresetContextMenu)
        self.tree["layer"].customContextMenuRequested.connect(customMenu.showLayerContextMenu)

    def onItemChanged(self):
        # Get a current selected item
        presetItem, _ = self.getterPreset.getCurrentData()
        if presetItem is None:
            return

        itemDict = {}
        rootItems = []

        # Clear all items in the layer widget
        self.tree["layer"].clear()

        # Create each layers from a preset data
        presetData = presetItem.data(0, QtCore.Qt.UserRole)
        if "preset" in presetData.get("type"):
            self.tree["preset"].setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            self.tree["layer"].setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        else:
            self.tree["layer"].setContextMenuPolicy(QtCore.Qt.NoContextMenu)

        if presetData.get("layers") is None:
            return

        for layer in presetData.get("layers"):
            layerItem = QtWidgets.QTreeWidgetItem([layer["name"]])
            layerIcon = QtGui.QIcon(common.getIconPath("layer.png"))
            layerItem.setIcon(0, layerIcon)

            # Set the layer data to the item
            layerItem.setData(0, QtCore.Qt.UserRole, layer)

            # Set the item as editable
            layerItem.setFlags(layerItem.flags() | QtCore.Qt.ItemIsEditable)

            itemDict[layer['id']] = layerItem

            # If the item has a parent, add it as a child to the parent item
            parentId = layer["parentId"]
            if parentId:
                parentItem = itemDict.get(parentId)
                if parentItem is not None:
                    parentItem.addChild(layerItem)
                else:
                    # If the parent item doesn't exist yet, store the child item for later
                    childItems = itemDict.get(parentId, None)
                    itemDict[parentId] = childItems
            else:
                # If the item has no parent, it's a root item
                rootItems.append(layerItem)

        # Set the correct order for the child items of each parent item
        for layer in presetData.get("layers"):
            parentId = layer['parentId']
            if not parentId:
                continue

            parentItem = itemDict.get(parentId)
            if not parentItem:
                continue

            childItems = itemDict.get(layer['id'], [])
            childIndex = layer.get('index')
            if childIndex is not None:
                parentItem.insertChild(childIndex, childItems)
            else:
                parentItem.addChildren(childItems)

        # Add all root items to the layer widget
        self.tree["layer"].insertTopLevelItems(0, rootItems)

        # Expands the layer items
        for layer in presetData.get("layers"):
            parentId = layer["parentId"]
            if parentId:
                parentItem = itemDict.get(parentId)
                parentItem.setExpanded(True)

    def editPresetItem(self):
        """Rename current QTreeWidgetItem.text to a new name

        :param types: QTreeWidget
        :return: None
        """
        # Get the preset data
        currentPreset, currentName = self.getterPreset.getCurrentData()
        if not currentPreset:
            return

        presetData = currentPreset.data(0, QtCore.Qt.UserRole)
        if currentName != presetData["name"]:
            presetData["name"] = currentName

            # Store the latest data
            currentPreset.setData(0, QtCore.Qt.UserRole, presetData)

        parentPreset = currentPreset.parent()
        if parentPreset:
            parentData = parentPreset.data(0, QtCore.Qt.UserRole)
            for data in parentData["children"]:
                if not data["index"] == presetData["index"]:
                    continue

                data["name"] = presetData["name"]
                parentPreset.setData(0, QtCore.Qt.UserRole, parentData)

    def editLayerItem(self):
        """Rename current QTreeWidgetItem.text to a new name

        :param types: QTreeWidget
        :return: None
        """
        # Get the preset data
        currentPreset, _ = self.getterPreset.getCurrentData()
        presetData = currentPreset.data(0, QtCore.Qt.UserRole)

        # Get the previous layer data
        currentItem, currentName = self.getterLayer.getCurrentData()

        if not currentItem:
            return

        previousData = currentItem.data(0, QtCore.Qt.UserRole)

        # Generate new data If the layer name was changed
        if currentName != previousData["name"]:
            previousData["name"] = currentName
            updateData = previousData

            currentLayerId = updateData["id"]

            layerList = []
            for data in presetData["layers"]:
                if data["id"] == currentLayerId:
                    layerList.append(updateData)
                else:
                    layerList.append(data)
            presetData["layers"] = layerList

            # Store the latest data
            currentPreset.setData(0, QtCore.Qt.UserRole, presetData)
            currentItem.setData(0, QtCore.Qt.UserRole, updateData)


class TreeWidgetContextMenu(object):

    def __init__(self, treeWidgets, types=None):
        self.tree = treeWidgets
        self.menuExec = TreeWidgetOperation(treeWidgets)
        self.types = types
        self.cursor = QtGui.QCursor()
        self.presetMenu = QtWidgets.QMenu(self.tree["preset"])
        self.layerMenu = QtWidgets.QMenu(self.tree["layer"])

        self.initPresetUI()
        self.initLayerUI()

    def initPresetUI(self):
        submenu = QtWidgets.QMenu("Add Item")
        groupAction = submenu.addAction("Group")
        presetAction = submenu.addAction("Preset")
        self.presetMenu.addMenu(submenu)
        duplicateAction = self.presetMenu.addAction("Duplicate Item")
        deleteAction = self.presetMenu.addAction("Delete Item")
        self.presetMenu.addSeparator()
        expandLayerCmd = self.presetMenu.addAction("Expand All Items")
        collapseLayerCmd = self.presetMenu.addAction("Collapse All Items")

        duplicateAction.setEnabled(False)

        groupAction.triggered.connect(self.menuExec.addGroupItem)
        presetAction.triggered.connect(lambda: self.menuExec.addPresetItemToParent("preset"))
        duplicateAction.triggered.connect(lambda: self.menuExec.duplicateItem("preset"))
        deleteAction.triggered.connect(lambda: self.menuExec.deleteItem("preset"))
        expandLayerCmd.triggered.connect(lambda: self.menuExec.expandAllItems("preset", expand=True))
        collapseLayerCmd.triggered.connect(lambda: self.menuExec.expandAllItems("preset", expand=False))

    def initLayerUI(self):
        newLayerCmd = self.layerMenu.addAction("Add Layer")
        duplicateAction = self.layerMenu.addAction("Duplicate Layer")
        deleteCmd = self.layerMenu.addAction("Delete Layer")
        self.layerMenu.addSeparator()
        expandLayerCmd = self.layerMenu.addAction("Expand All Items")
        collapseLayerCmd = self.layerMenu.addAction("Collapse All Items")

        duplicateAction.setEnabled(False)

        newLayerCmd.triggered.connect(self.menuExec.addLayer)
        duplicateAction.triggered.connect(lambda: self.menuExec.duplicateItem("layer"))
        deleteCmd.triggered.connect(lambda: self.menuExec.deleteItem("layer"))
        expandLayerCmd.triggered.connect(lambda: self.menuExec.expandAllItems("layer", expand=True))
        collapseLayerCmd.triggered.connect(lambda: self.menuExec.expandAllItems("layer", expand=False))

    def showPresetContextMenu(self, position):
        self.presetMenu.exec_(self.tree["preset"].mapToGlobal(position))

    def showLayerContextMenu(self, position):
        self.layerMenu.exec_(self.tree["layer"].mapToGlobal(position))


class TreeWidgetOperation(object):

    def __init__(self, treeWidgets):
        self.tree = treeWidgets
        self.getterPreset = TreeWidgetReader(self.tree["preset"])
        self.getterLayer = TreeWidgetReader(self.tree["layer"])
        self.data = LayerPresetData(self.tree["preset"])

    def addLayer(self):
        """Create a layer in the layer widget
        :return:
        """
        # Get the preset data
        preset, _ = self.getterPreset.getCurrentData()
        presetData = preset.data(0, QtCore.Qt.UserRole)

        # Create a new layer object with an icon
        layer = QtWidgets.QTreeWidgetItem(["New Layer"])
        layerIcon = QtGui.QIcon(self.data.getIconPath("group"))
        layer.setIcon(0, layerIcon)

        # Insert the layer item to the layer widget
        selectedItem, _ = self.getterLayer.getCurrentData()
        if not selectedItem:
            self.tree["layer"].insertTopLevelItem(0, layer)
        else:
            selectedItem.insertChild(0, layer)
            selectedItem.setExpanded(True)

        # Get a data for the new layer and set a data to its object
        num = self.getterLayer.getAllIdInTree(presetData["layers"])
        if num:
            maxId = max(num)
        else:
            maxId = 0

        layerData = self.getterLayer.getItemData(layer, id=maxId + 1, types="layer")
        layer.setData(0, QtCore.Qt.UserRole, layerData)

        # Set a flag to make item editable
        layer.setFlags(layer.flags() | QtCore.Qt.ItemIsEditable)

        # Get the latest data and sort the 'layers' list by the 'index' value
        layerAllListData = self.getterLayer.getLayerStructure()
        allItems = sorted(layerAllListData, key=lambda x: x['index'])

        # Store the lastest data
        presetData["layers"] = allItems
        preset.setData(0, QtCore.Qt.UserRole, presetData)

        # Select and edit new item
        self.tree["layer"].setCurrentItem(layer)


    def addPresetItemToParent(self, types):
        """Add a new preset item in a QTreeWidget

        :param types: QTreeWidget
            The name of QTreeWidget
        """
        selectedItem, _ = self.getterPreset.getCurrentData()
        presetData = selectedItem.data(0, QtCore.Qt.UserRole)
        if "preset" in presetData["type"]:
            return

        # Generate a new id for the new item based on the current maximum id in the collection
        allitems = self.getterPreset.getAllItems()
        allId = self.getterPreset.getAllPresetIdInTree(allitems)
        if allId:
            newId = max(allId) + 1
        else:
            newId = 1

        # Generate a new item on the preset widget
        preset = QtWidgets.QTreeWidgetItem(["preset"])
        presetIcon = self.data.getIconPath("preset")
        preset.setIcon(0, presetIcon)

        # Insert the new item at the end of child items for the selected item
        childNum = selectedItem.childCount()
        selectedItem.insertChild(childNum, preset)

        # Store new item into the database
        presetData = self.getterPreset.getItemData(preset, newId, types="preset")
        preset.setData(0, QtCore.Qt.UserRole, presetData)

        _parent = preset.parent()
        if _parent:
            parentData = _parent.data(0, QtCore.Qt.UserRole)
            parentData["children"].append(presetData)
            _parent.setData(0, QtCore.Qt.UserRole, parentData)

        # Set a flag to make item editable
        preset.setFlags(preset.flags() | QtCore.Qt.ItemIsEditable)

        # Select a new item and set it as editable
        self.tree["preset"].setCurrentItem(preset)
        self.tree["preset"].editItem(preset, 0)

    def addGroupItem(self):
        """Add a new group item in a preset QTreeWidget
        """
        selectedItem, _ = self.getterPreset.getCurrentData()
        presetData = selectedItem.data(0, QtCore.Qt.UserRole)
        if "preset" in presetData["type"]:
            return

        # Create a new group object with an icon
        group = QtWidgets.QTreeWidgetItem(["NewGroup"])
        groupIcon = QtGui.QIcon(self.data.getIconPath("group"))
        groupIcon.setThemeName("group")
        group.setIcon(0, groupIcon)

        allItems = self.getterPreset.getAllItems()
        # Generate a new id for the new item based on the current maximum id in the collection
        allId = self.getterPreset.getAllIdInTree(allItems)

        if allId:
            newId = max(allId) + 1
        else:
            newId = 1

        # Insert the new item at the end of child items for the selected item
        if not selectedItem:
            self.tree["preset"].addTopLevelItem(group)
        else:
            childNum = selectedItem.childCount()
            selectedItem.insertChild(childNum, group)

        # Get the current layer data
        groupData = self.getterPreset.getItemData(group, newId, types="group")
        group.setData(0, QtCore.Qt.UserRole, groupData)

        # Set a flag to make item editable
        group.setFlags(group.flags() | QtCore.Qt.ItemIsEditable)

        # Select and edit new item
        self.tree["preset"].setCurrentItem(group)
        self.tree["preset"].editItem(group, 0)

    def deleteItem(self, types):
        """Delete a selected item from a QTreeWidget

        :param types: QTreeWidget
            The name of QTreeWidget
        """
        # Get the preset data
        preset, _ = self.getterPreset.getCurrentData()
        presetData = preset.data(0, QtCore.Qt.UserRole)

        # Get the current item
        item, parent = None, None
        if types == "preset":
            item, _ = self.getterPreset.getCurrentData()
            parent = self.getterPreset.getParentItem(item)

        elif types == "layer":
            item, _ = self.getterLayer.getCurrentData()
            parent = self.getterLayer.getParentItem(item)

        if not item:
            return

        # Remove the selected item from the widget
        if not parent:
            index = self.tree[types].indexOfTopLevelItem(item)
            self.tree[types].takeTopLevelItem(index)
        else:
            parent.removeChild(item)

        # Get the data to be deleted
        deleteData = item.data(0, QtCore.Qt.UserRole)
        if types == "layer":
            # Remove the layer from the data structure
            for data in presetData["layers"]:
                if data["id"] == deleteData["id"]:
                    presetData["layers"].remove(data)
                    break

            # Get the updated layer structure
            presetData["layers"] = self.getterLayer.getLayerStructure()

            # Set the fresh data to the object
            preset.setData(0, QtCore.Qt.UserRole, presetData)

    def duplicateItem(self, types, item=None):
        """Todo

        :param types:
        :param item:
        :return:
        """
        if not item:
            item = self.tree[types].currentItem()

        # Create a new item with the same text and user data
        newItemName = [item.text(i) for i in range(item.columnCount())]
        if item.parent():
            newItem = QtWidgets.QTreeWidgetItem(item.parent(), newItemName)
        else:
            newItem = QtWidgets.QTreeWidgetItem(newItemName)

        newItem.setFlags(newItem.flags() | QtCore.Qt.ItemIsEditable)
        icon = self.data.getIconPath(types)
        icon.setThemeName(types)
        newItem.setIcon(0, icon)
        newItem.setData(0, QtCore.Qt.UserRole, item.data(0, QtCore.Qt.UserRole))

        # Recursively duplicate each child item
        for i in range(item.childCount()):
            childItem = item.child(i)
            duplicateChildItem = self.duplicateItem(types, childItem)
            newItem.addChild(duplicateChildItem)

        return newItem

    def expandAllItems(self, types, expand=True):
        """ Expands all items
        :param treeWidget:
        :return:
        """
        num = self.tree[types].topLevelItemCount()
        if num == 0:
            return None

        getter = TreeWidgetReader(self.tree[types])
        allChildren = []
        for i in range(num):
            topItem = self.tree[types].topLevelItem(i)
            topItem.setExpanded(expand)
            allChildren.extend(getter.getAllChildren(topItem))

        for item in allChildren:
            item.setExpanded(expand)


class LayerPresetData(Data):
    FILE_NAME = "layerPresets.json"  # Name of the file

    def __init__(self, treeWidget=None):
        """Initialize the LayerPresetData object.

        :param treeWidget: The tree widget object.
        """
        super(LayerPresetData, self).__init__()

        self.tree = treeWidget
        self.filePath = common.getDataPath(self.FILE_NAME)
        self.getter = TreeWidgetReader(treeWidget)

    def getIconPath(self, types):
        """Return the icon path based on the type of item

        :param types: The type of the item.
        :return: The icon path
        """
        if types == "group" or types == "layer":
            return QtGui.QIcon(common.getIconPath("layer.png"))
        elif types == "preset":
            return QtGui.QIcon(common.getIconPath("textItem.png"))

    def getDataFromWidget(self):
        """Get the latest preset items from the widget.

        :return: The JSON serialized data.
        """
        # Get the latest preset items
        data = self.getter.getAllItems()

        # Serializing json
        jsonObject = json.dumps(data, indent=4)
        return jsonObject, data

    def importData(self, data=None):
        """Import the data into the QTreeWidget object.

        :param data: The data to import.
        """
        listLayer = {}
        listKeyItem = {}

        if data is None:
            data = self.load(filePath=self.filePath)

        if self.tree:
            self.tree.clear()

        for i, (key, values) in enumerate(data.items()):
            keyItem = QtWidgets.QTreeWidgetItem([key])
            keyItem.setFlags(keyItem.flags() | QtCore.Qt.ItemIsEditable)
            keyItem.setData(0, QtCore.Qt.UserRole, values)
            keyIcon = self.getIconPath(values.get("type"))
            keyIcon.setThemeName(values.get("type"))
            keyItem.setIcon(0, keyIcon)

            listKeyItem[key] = keyItem

            for child in values.get("children"):
                childItem = QtWidgets.QTreeWidgetItem([child.get("name")])
                childItem.setData(0, QtCore.Qt.UserRole, child)
                childItem.setFlags(childItem.flags() | QtCore.Qt.ItemIsEditable)
                childIcon = self.getIconPath(child.get("type"))
                childIcon.setThemeName(values.get("type"))
                childItem.setIcon(0, childIcon)
                keyItem.addChild(childItem)

            listLayer[values.get("index")] = listKeyItem[key]

        layers = []
        for i in range(0, len(listLayer)):
            layers.append(listLayer[i])
        return layers

    def loadFile(self, loadedData=None):
        """Load the file data into the LayerPresetData object.
        """
        if loadedData is None:
            loadedData = self.load()
            if loadedData is None:
                return

        layers = self.importData(data=loadedData)

        # assign them to the widget list
        self.tree.takeTopLevelItem(0)
        self.tree.addTopLevelItems(layers)

        for data in layers:
            data.setExpanded(True)

    def exportFile(self):
        """Export the file data from the LayerPresetData object.
        """
        if not os.path.exists(self.filePath):
            self.filePath = self.fileDialog(mode=0)

        # Writing to sample.json
        _, data = self.getDataFromWidget()
        self.save(self.filePath, data)

    def exportFileAs(self):
        """Export the file data from the LayerPresetData object as a new file.
        """
        _, data = self.getDataFromWidget()
        self.saveAs(data)
