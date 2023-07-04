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
# Built-in
from functools import partial
import sys
import json

# Third party
import maya.cmds as cmds

from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtWidgets import QTreeWidget, QTreeWidgetItem
from PySide2.QtCore import QTimer
from PySide2.QtGui import QIcon

from rig_tools.tool.ngSkinHelperTool.tabInternal import layerManagerBase


class CustomTreeWidgets(QTreeWidget):
    mimeFormat = "application/x-qabstractitemmodeldatalist"

    def __init__(self, types="preset", widgets=None, parent=None):
        super(CustomTreeWidgets, self).__init__(parent)

        self.tree = widgets
        self.types = types
        self.nodeDropped = QtCore.Signal()
        self.createTreeWidget(headerLabel=self.getHeaderLabel(types))

        # Getter object
        if widgets:
            self.getterPreset = layerManagerBase.TreeWidgetReader(self.tree)

    def getHeaderLabel(self, types):
        """Get a header label for a layer

        :param types:
        :return:
        """
        label = None
        if types == "preset":
            label = "Preset"
        elif types == "layer":
            label = "Layer Structure"
        return label

    def createTreeWidget(self, headerLabel):
        """Create a custom tree widget

        :param headerLabel: str
            [preset or layer] name of widget types
        """
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setHeaderLabel(headerLabel)
        self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.setDragEnabled(True)
        self.viewport().setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setAlternatingRowColors(True)
        self.setRootIsDecorated(True)
        self.setItemsExpandable(True)
        self.setAllColumnsShowFocus(False)
        self.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.setAutoExpandDelay(-1)
        self.setIndentation(20)

    def clearSelection(self):
        super(CustomTreeWidgets, self).clearSelection()
        self.clearFocus()
        self.viewport().update()

    def startDrag(self, supportedActions):
        """In a QTreeWidget, the startDrag() method is called when the user starts to drag an item.
        It creates a QDrag object, which is responsible for carrying the item data during the drag operation.
        """
        item = self.currentItem()
        if not item:
            return

        # Create a QMimeData object
        mimeData = QtCore.QMimeData()

        # Set a MIME type and data
        itemData = item.data(0, QtCore.Qt.UserRole)

        # data = self.getter.getItemData(item)
        byteArray = self.serializeDictToJson(itemData)
        mimeData.setData(self.mimeFormat, byteArray)

        # Set the data to be dragged here
        drag = QtGui.QDrag(self)
        drag.setMimeData(mimeData)

        # Set the pixmap to a transparent image
        pixmap = QtGui.QPixmap(item.sizeHint(0))
        pixmap.fill(QtCore.Qt.transparent)
        drag.setPixmap(pixmap)

        _treeWidget = item.treeWidget()
        rect = _treeWidget.visualItemRect(item)
        drag.setHotSpot(rect.center())

        # Start the drag
        drag.exec_(QtCore.Qt.CopyAction | QtCore.Qt.MoveAction)

    def serializeDictToJson(self, itemData):
        """Convert the dictionary into a JSON string, then encode the resulting string into bytes

        :param itemData: dict
        :return: QByteArray
        """
        json_string = json.dumps(itemData)
        return QtCore.QByteArray(json_string.encode())

    def dragEnterEvent(self, event):
        """The dragEnterEvent method in a QTreeWidget is an event handler that is called
        when a drag and drop operation enters the boundaries of the widget.
        It is responsible for accepting or rejecting the drag based on whether the widget can handle the incoming data.

        :param event:
        """
        # Accept the drag event if it has mime data
        if event.mimeData().hasFormat(self.mimeFormat):
            event.accept()
            event.setDropAction(QtCore.Qt.MoveAction)
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        """An event that occurs during a drag and drop operation when the mouse is moved over a widget that
        is a potential drop target. The purpose of this event is to allow the widget to provide feedback
        to the user about whether the drop is possible and what kind of drop it will be.

        :param event:
        :return:
        """
        super(CustomTreeWidgets, self).dragMoveEvent(event)

        # Accept the drag move event if it is over a valid drop target
        if event.mimeData().hasFormat(self.mimeFormat):
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        """This method is called when a drag and drop operation is completed and
        the dragged item is dropped onto a valid drop target.
        This method is responsible for handling the dropped item and updating the view accordingly.

        :param event:
        :return:
        """
        mime = event.mimeData()
        if not mime.hasFormat(self.mimeFormat):
            return

        srcItem = self.currentItem()
        dstItem = self.itemAt(event.pos())

        if not srcItem:
            return

        # Get the data for the source and destination items
        srcItemData = srcItem.data(0, QtCore.Qt.UserRole)
        dstItemData = dstItem.data(0, QtCore.Qt.UserRole) if dstItem else None

        # Get the parent items of the source and destination items
        srcParentItem = srcItem.parent()

        # The destination item is the source item,
        if srcItem is dstItem:
            return

        # Ensure that the destination item is expanded
        if dstItem and not dstItem.isExpanded():
            dstItem.setExpanded(True)

        pos = self.dropIndicatorPosition()
        if srcParentItem:
            self.moveItemWithinParent(srcItem,
                                      dstItem,
                                      srcItemData,
                                      dstItemData,
                                      pos)
            event.accept()
        elif srcParentItem is None and dstItem:
            self.moveTopLevelItem(srcItem,
                                  dstItem,
                                  srcItemData,
                                  dstItemData,
                                  pos)
            event.accept()
        else:
            event.ignore()

        # print srcItemData
        self.setCurrentItem(srcItem)

    def mousePressEvent(self, event):
        if not self.indexAt(event.pos()).isValid():
            self.selectionModel().clear()
        super(CustomTreeWidgets, self).mousePressEvent(event)

    def moveItemWithinParent(self, srcItem, dstItem, srcItemData, dstItemData, pos):
        """Function that moves an item within a given parent object or data structure.

        :param srcItem: The item of the source item to move
        :param dstItem: The item of the destination item to move the source item to
        :param srcItemData: The data of the source item
        :param dstItemData: The data of the destination item
        :param pos: QtWidgets.QAbstractItemView
        :return:
        """
        # Remove the source item from its parent
        srcParent = srcItem.parent()
        srcIndex = srcParent.indexOfChild(srcItem)
        srcItem.parent().takeChild(srcIndex)

        if dstItem:
            dstParentItem = dstItem.parent() or self.invisibleRootItem()

            # The source item is a parent of the destination item.
            if dstParentItem is srcItem:
                return

            # Clone source and destination item
            srcItemClone = srcItem.clone()
            dstItemClone = dstItem.clone()

            view = QtWidgets.QAbstractItemView
            if pos == QtWidgets.QAbstractItemView.OnItem:
                dstItem.addChild(srcItem)
                srcItemData["parentId"] = dstItemData["id"]
                srcItemData["index"] = dstItem.indexOfChild(srcItem)
            elif pos is view.AboveItem:
                # Swap the items in the tree
                dstIndex = dstParentItem.indexOfChild(dstItem)
                dstParentItem.takeChild(dstIndex)
                dstParentItem.insertChild(dstIndex, srcItemClone)
                dstParentItem.insertChild(dstIndex + 1, dstItemClone)

                # Update the data for the source and destination items
                srcItemData["index"] = dstIndex
                dstItemData["index"] = dstIndex + 1
                srcItemData["parentId"] = dstItemData["parentId"]
            elif pos is view.BelowItem:
                # Swap the items in the tree
                dstIndex = dstParentItem.indexOfChild(dstItem)
                dstParentItem.takeChild(dstIndex)
                dstParentItem.insertChild(dstIndex, dstItemClone)
                dstParentItem.insertChild(dstIndex + 1, srcItemClone)

                # Update the data for the source and destination items
                srcItemData["index"] = dstIndex + 1
                dstItemData["index"] = dstIndex
                srcItemData["parentId"] = dstItemData["parentId"]

        else:
            # Insert the source item as a top-level item
            self.addTopLevelItem(srcItem)
            srcItemData["parentId"] = 0
            srcItemData["index"] = self.indexOfTopLevelItem(srcItem)

        for i in range(srcParent.childCount()):
            srcNextItem = srcParent.child(i)
            srcNextItemData = srcNextItem.data(0, QtCore.Qt.UserRole)
            srcNextItemData["index"] = i
            self.updatePresetData(srcNextItem, srcNextItemData)

        self.updatePresetData(srcItem, srcItemData)
        self.updatePresetData(dstItem, dstItemData)

    def moveTopLevelItem(self, srcItem, dstItem, srcItemData, dstItemData, pos):
        """Move a top level item from the source index to the destination index.

        :param srcItem: The item of the source item to move
        :param dstItem: The item of the destination item to move the source item to
        :param srcItemData: The data of the source item
        :param dstItemData: The data of the destination item
        :param pos: QtWidgets.QAbstractItemView
        :return:
        """
        srcIndex = self.indexOfTopLevelItem(srcItem)

        # If the source item and destination item have the same parent, then we can just swap their positions
        srcItemClone = srcItem.clone()
        dstItemClone = dstItem.clone()

        dstParentItem = dstItem.parent()
        if dstParentItem:
            dstIndex = dstParentItem.indexOfChild(dstItem)
        else:
            dstIndex = self.indexOfTopLevelItem(dstItem)

        # Check if the indices are valid
        if not (0 <= srcIndex < self.topLevelItemCount()):
            return
        if srcIndex == dstIndex:
            return

        self.takeTopLevelItem(srcIndex)

        # Swap the items in the tree
        view = QtWidgets.QAbstractItemView
        if pos is view.AboveItem:
            if dstParentItem:
                # print("abstrct parent here")
                dstParentItem.takeChild(dstIndex)
                dstParentItem.insertChild(dstIndex, srcItemClone)
                dstParentItem.insertChild(dstIndex + 1, dstItemClone)
                srcItemData["parentId"] = dstItemData["parentId"]
                dstItemData["parentId"] = dstItemData["parentId"]
            else:
                # print("abstrct here")
                self.insertTopLevelItem(dstIndex, srcItemClone)
                self.insertTopLevelItem(dstIndex + 1, dstItem)
                # self.takeTopLevelItem(dstItemClone)

            # Update the data for the source and destination items
            srcItemData["index"] = dstIndex
            dstItemData["index"] = dstIndex + 1
        elif pos is view.BelowItem:
            if dstParentItem:
                # print("hi parent here")
                dstParentItem.takeChild(dstIndex)
                dstParentItem.insertChild(dstIndex + 1, srcItemClone)
                dstParentItem.insertChild(dstIndex, dstItemClone)
                srcItemData["parentId"] = dstItemData["parentId"]
                dstItemData["parentId"] = dstItemData["parentId"]
            else:
                # print("hi no parent here")
                self.insertTopLevelItem(dstIndex, srcItemClone)
                self.insertTopLevelItem(dstIndex - 1, dstItemClone)
                self.takeTopLevelItem(dstIndex)

            # Update the data for the source and destination items
            srcItemData["index"] = dstIndex + 1
            dstItemData["index"] = dstIndex

        elif pos == QtWidgets.QAbstractItemView.OnItem:
            dstItem.addChild(srcItemClone)
            srcItemData["parentId"] = dstItemData["id"]
            srcItemData["index"] = dstItem.indexOfChild(srcItemClone)

        self.updatePresetData(srcItem, srcItemData)
        self.updatePresetData(dstItem, dstItemData)

    def updatePresetData(self, item, itemData):
        """Function that updates some data related to a preset item.

        :param srcItem: The item of the source item to move
        :param dstItem: The item of the destination item to move the source item to
        :param srcItemData: The data of the source item
        :param dstItemData: The data of the destination item
        """
        # Set the latest data in srcItem and dstItem
        item.setData(0, QtCore.Qt.UserRole, itemData) if item else None

        if not self.tree:
            return

        # Get the preset data
        preset, _ = self.getterPreset.getCurrentData()
        presetData = preset.data(0, QtCore.Qt.UserRole)

        # Swap the old data with the latest one
        for data in presetData["layers"]:
            if not itemData:
                continue

            # print(data)
            if data["id"] == itemData["id"]:
                dataIndex = presetData["layers"].index(data)
                presetData["layers"].pop(dataIndex)
                presetData["layers"].insert(dataIndex, itemData)

        # Update the latest data
        sortedLayerData = sorted(presetData['layers'], key=lambda x: x['index'])
        presetData["layers"] = sortedLayerData
        preset.setData(0, QtCore.Qt.UserRole, presetData)
