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
import json
import os

# Third party
import maya.cmds as cmds
from PySide2 import QtCore, QtWidgets, QtGui

# Local moudles
from rig_tools.tool.ngSkinHelperTool.util.data import Data


class Widgets(QtWidgets.QDialog):

    def __init__(self):
        super(Widgets, self).__init__()

        self.centralwidget = QtWidgets.QWidget(self)
        self.topVLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.frame = QtWidgets.QFrame(self.centralwidget)

        self.treeWidgetMainVLayout = QtWidgets.QVBoxLayout(self.frame)
        self.treeWidgetVLayout = QtWidgets.QVBoxLayout(self.frame)
        self.treeWidget = QtWidgets.QTreeWidget(self.frame)

        self.srVLayout = QtWidgets.QVBoxLayout()
        self.srHLayout = QtWidgets.QHBoxLayout()
        self.searchTextEdit = QtWidgets.QTextEdit(self.frame)
        self.replaceTextEdit = QtWidgets.QTextEdit(self.frame)
        self.srGroupTextHLayout = QtWidgets.QHBoxLayout()
        self.srGroupTextEdit = QtWidgets.QTextEdit(self.frame)

        self.srRadioBtnHLayout = QtWidgets.QHBoxLayout()
        self.srAddItemLabel = QtWidgets.QLabel()
        self.srGroupRadioBtn = QtWidgets.QRadioButton()
        self.srItemRadioBtn = QtWidgets.QRadioButton()
        self.addGroupBtn = QtWidgets.QPushButton(self.frame)
        self.addItemBtn = QtWidgets.QPushButton(self.frame)

        self.mainBtnHLayout = QtWidgets.QHBoxLayout()
        self.applyBtn = QtWidgets.QPushButton(self.centralwidget)
        self.applyCloseBtn = QtWidgets.QPushButton(self.centralwidget)
        self.closeBtn = QtWidgets.QPushButton(self.centralwidget)

        self.sp = QtWidgets.QSizePolicy

    def centralWidget(self):
        self.centralwidget.setObjectName("centralwidget")
        self.topVLayout.setObjectName("topVLayout")
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")

    def createWidgets(self):
        self.centralWidget()
        self.searchReplaceWidgets()
        self.mainButtonWidgets()

    def searchReplaceWidgets(self):
        self.treeWidgetMainVLayout.setSpacing(5)
        self.treeWidgetMainVLayout.setContentsMargins(-1, -1, -1, 10)
        self.treeWidgetMainVLayout.setObjectName("treeWidgetMainVLayout")

        self.treeWidgetVLayout.setSpacing(-1)
        self.treeWidgetVLayout.setContentsMargins(0, -1, 0, -1)
        self.treeWidgetVLayout.setObjectName("treeWidgetVLayout")

        sizePolicy = self.sp(self.sp.Expanding, self.sp.Expanding)
        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.setHeaderLabel("Preset")
        self.treeWidget.setSizePolicy(sizePolicy)
        self.treeWidget.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.treeWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        self.srVLayout.setSpacing(3)
        self.srVLayout.setObjectName("srVLayout")

        self.srHLayout.setSpacing(3)
        self.srHLayout.setObjectName("srHLayout")

        self.searchTextEdit.setMinimumSize(QtCore.QSize(0, 0))
        self.searchTextEdit.setMaximumSize(QtCore.QSize(16777215, 27))
        sizePolicy = self.sp(self.sp.Expanding, self.sp.Fixed)
        self.searchTextEdit.setSizePolicy(sizePolicy)
        self.searchTextEdit.setObjectName("searchTextEdit")
        self.searchTextEdit.setPlaceholderText("Search")

        self.replaceTextEdit.setMinimumSize(QtCore.QSize(0, 0))
        self.replaceTextEdit.setMaximumSize(QtCore.QSize(16777215, 27))
        sizePolicy = self.sp(self.sp.Expanding, self.sp.Fixed)
        self.replaceTextEdit.setSizePolicy(sizePolicy)
        self.replaceTextEdit.setObjectName("replaceTextEdit")
        self.replaceTextEdit.setPlaceholderText("Replace")

        self.srGroupTextEdit.setMaximumSize(QtCore.QSize(16777215, 27))
        sizePolicy = self.sp(self.sp.Expanding, self.sp.Fixed)
        self.srGroupTextEdit.setSizePolicy(sizePolicy)
        self.srGroupTextEdit.setObjectName("srGroupTextEdit")
        self.srGroupTextEdit.setPlaceholderText("Group Name")
        self.srGroupTextEdit.setVisible(False)

        self.srRadioBtnHLayout.setSpacing(5)
        self.srAddItemLabel.setText("Types:")
        sizePolicy = self.sp(self.sp.Fixed, self.sp.Fixed)
        self.srAddItemLabel.setSizePolicy(sizePolicy)
        self.srAddItemLabel.setFixedHeight(25)

        self.srGroupRadioBtn.setText("Group")
        sizePolicy = self.sp(self.sp.Expanding, self.sp.Fixed)
        self.srGroupRadioBtn.setSizePolicy(sizePolicy)
        self.srGroupRadioBtn.setFixedHeight(25)

        self.srItemRadioBtn.setText("Menu")
        self.srItemRadioBtn.setChecked(True)
        sizePolicy = self.sp(self.sp.Expanding, self.sp.Fixed)
        self.srItemRadioBtn.setSizePolicy(sizePolicy)
        self.srItemRadioBtn.setFixedHeight(25)

        self.addGroupBtn.setObjectName("addGroupBtn")
        sizePolicy = self.sp(self.sp.Expanding, self.sp.Fixed)
        self.addGroupBtn.setSizePolicy(sizePolicy)
        self.addGroupBtn.setText("Add a group item")

        self.addItemBtn.setObjectName("addItemBtn")
        sizePolicy = self.sp(self.sp.Expanding, self.sp.Fixed)
        self.addItemBtn.setSizePolicy(sizePolicy)
        self.addItemBtn.setText("Add an item")

    def mainButtonWidgets(self):
        self.mainBtnHLayout.setSpacing(3)
        self.mainBtnHLayout.setObjectName("mainBtnHLayout")

        self.applyBtn.setObjectName("applyBtn")
        self.applyBtn.setText("Save")
        self.applyBtn.setMinimumHeight(26)

        self.applyCloseBtn.setObjectName("applyCloseBtn")
        self.applyCloseBtn.setText("Save and Close")
        self.applyCloseBtn.setMinimumHeight(26)

        self.closeBtn.setObjectName("closeBtn")
        self.closeBtn.setText("Close")
        self.closeBtn.setMinimumHeight(26)

    def layout(self):
        self.treeWidgetVLayout.addWidget(self.treeWidget)

        self.srRadioBtnHLayout.addStretch()
        self.srRadioBtnHLayout.addWidget(self.srAddItemLabel)
        self.srRadioBtnHLayout.addWidget(self.srGroupRadioBtn)
        self.srRadioBtnHLayout.addWidget(self.srItemRadioBtn)
        self.srRadioBtnHLayout.addStretch()

        self.srGroupTextHLayout.addWidget(self.srGroupTextEdit)
        self.srHLayout.addWidget(self.searchTextEdit)
        self.srHLayout.addWidget(self.replaceTextEdit)
        self.srVLayout.addLayout(self.srGroupTextHLayout)
        self.srVLayout.addLayout(self.srHLayout)
        self.srVLayout.addWidget(self.addGroupBtn)
        self.srVLayout.addWidget(self.addItemBtn)

        self.treeWidgetMainVLayout.addLayout(self.treeWidgetVLayout)
        self.treeWidgetMainVLayout.addLayout(self.srRadioBtnHLayout)
        self.treeWidgetMainVLayout.addLayout(self.srVLayout)

        self.topVLayout.addWidget(self.frame)

        self.mainBtnHLayout.addWidget(self.applyBtn)
        self.mainBtnHLayout.addWidget(self.applyCloseBtn)
        self.mainBtnHLayout.addWidget(self.closeBtn)
        self.topVLayout.addLayout(self.mainBtnHLayout)
        self.setLayout(self.topVLayout)


class MainWindow(Widgets):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.setObjectName("MainWindow")
        self.resize(400, 460)
        self.setWindowTitle("Custom Preset UI")

        self.data = PresetData()
        self.item = QtWidgets.QTreeWidgetItem(self.treeWidget)

        self.createWidgets()
        self.layout()
        self.assignItem()
        self.setSignal()
        self.updateRadioVis()

    def assignItem(self):
        self.data.importData()
        self.treeWidget.insertTopLevelItems(0, self.data.parentItems)
        for data in self.data.parentItems:
            data.setExpanded(True)

    def getParentItem(self):
        item = self.getCurrentData()
        return item.parent()

    def getCurrentData(self):
        item = self.treeWidget.selectedItems()
        if not item:
            return None
        return item[0]

    def getAllTextEdit(self):
        search = self.searchTextEdit.toPlainText()
        replace = self.replaceTextEdit.toPlainText()
        return search, replace

    def convertTextToItem(self):
        search, replace = self.getAllTextEdit()
        if not search and not replace:
            return None

        item = QtWidgets.QTreeWidgetItem(["{} > {}".format(search, replace)])
        itemIcon = QtGui.QIcon(self.data.getIconPath("textItem.png"))
        item.setIcon(0, itemIcon)
        return item

    def addChildItemToParent(self):
        # child = self.item.setText(0, self.convertTextToItem())
        item = self.getCurrentData()
        childNum = item.childCount()

        if ">" in item.text(0):
            return

        childItem = self.convertTextToItem()
        item.insertChild(childNum, childItem)

    def updateRadioVis(self):
        if self.srGroupRadioBtn.isChecked():
            self.srGroupTextEdit.setVisible(True)
            self.searchTextEdit.setVisible(False)
            self.replaceTextEdit.setVisible(False)
            self.addGroupBtn.setVisible(True)
            self.addItemBtn.setVisible(False)

        else:
            self.srGroupTextEdit.setVisible(False)
            self.searchTextEdit.setVisible(True)
            self.replaceTextEdit.setVisible(True)
            self.addGroupBtn.setVisible(False)
            self.addItemBtn.setVisible(True)

    def showContextMenu(self):
        action1 = QtWidgets.QAction("Delete an item")
        action2 = QtWidgets.QAction("Clear selection")
        menu = QtWidgets.QMenu(self.treeWidget)
        menu.addAction(action1)
        menu.addAction(action2)

        cursor = QtGui.QCursor()
        menu.exec_(cursor.pos())

    def deleteItem(self, item):
        self.item.parent().removeRow(item.row())

    def addGroupItem(self):
        gpItem = self.srGroupTextEdit.toPlainText()
        item = QtWidgets.QTreeWidgetItem([gpItem])
        itemIcon = QtGui.QIcon(self.data.getIconPath("layer.png"))
        item.setIcon(0, itemIcon)

        selectedItem = self.getCurrentData()
        childNum = selectedItem.childCount()
        selectedItem.insertChild(childNum, item)

    def signalApply(self):
        self.data.exportData()

    def signalApplyClose(self):
        self.signalApply()
        self.close()

    def setSignal(self):
        self.srGroupRadioBtn.clicked.connect(self.updateRadioVis)
        self.srItemRadioBtn.clicked.connect(self.updateRadioVis)
        self.addGroupBtn.clicked.connect(self.addGroupItem)
        self.addItemBtn.clicked.connect(self.addChildItemToParent)

        self.treeWidget.customContextMenuRequested.connect(self.showContextMenu)

        self.applyBtn.clicked.connect(self.signalApply)
        self.applyCloseBtn.clicked.connect(self.signalApplyClose())
        self.closeBtn.clicked.connect(self.close)
        self.treeWidget.itemPressed.connect(self.getCurrentData)


class PresetData(Data):
    data = {"Body": ["-", "-", "-"],
            "Face": ["upr > lwr", "lwr > upr"],
            "Prop": [],
            "Finger": ["01 > Base01", "01 > Index01", "01 > Middle01", "01 > Ring01", "01 > Pinky01"]}

    FILE_NAME = "copyPastePreset.json"

    def __init__(self):
        super(PresetData, self).__init__()

        self.parentItems = []

        self.widget = Widgets()
        self.item = QtWidgets.QTreeWidgetItem(self.widget.treeWidget)

    def importData(self):
        data = self.load(filePath=self.getDataPath())

        for key, values in data.items():
            keyItem = QtWidgets.QTreeWidgetItem([key])
            keyIcon = QtGui.QIcon(self.getIconPath("layer.png"))
            keyItem.setIcon(0, keyIcon)
            for value in values:
                child = QtWidgets.QTreeWidgetItem([value])
                childIcon = QtGui.QIcon(self.getIconPath("textItem.png"))
                child.setIcon(0, childIcon)
                keyItem.addChild(child)
            self.parentItems.append(keyItem)

    def exportData(self):
        # Serializing json
        jsonObject = json.dumps(self.data, indent=4)
        filePath = self.getDataPath()

        # if not os.path.exists(filePath):
        #     filePath = self.fileDialog(mode=0)    

        # Writing to sample.json
        with open(filePath, "w") as outfile:
            outfile.write(jsonObject)

    def updateData(self):
        pass

    @staticmethod
    def getDataPath():
        dirPath = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(dirPath, self.FILE_NAME)

    @staticmethod
    def getIconPath(fileName):
        dirPath = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(dirPath, "icon", fileName)

    def getSubTreeNodes(self, treeWidgetItem):
        """Returns all QTreeWidgetItems in the subtree rooted at the given node."""
        nodes = []
        for i in range(treeWidgetItem.childCount()):
            nodes.extend(self.getSubTreeNodes(treeWidgetItem.child(i)))
        return nodes

    def getAllItems(self):
        """Returns all QTreeWidgetItems in the given QTreeWidget."""
        all_items = []
        for i in range(self.widget.treeWidget.topLevelItemCount()):
            top_item = self.widget.treeWidget.topLevelItem(i)
            all_items.extend(self.getSubTreeNodes(top_item))
        return all_items
