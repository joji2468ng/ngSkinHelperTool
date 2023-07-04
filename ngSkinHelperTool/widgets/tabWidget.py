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
import sys
import webbrowser
from functools import partial

# Third party
import maya.cmds as cmds
from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtCore import QTimer
from PySide2.QtGui import QIcon

# Local modules
from rig_tools.tool.ngSkinHelperTool.tabInternal import layerManagerBase
from rig_tools.tool.ngSkinHelperTool.util import common, utils, data
from rig_tools.tool.ngSkinHelperTool.widgets.build.treeWidgets import CustomTreeWidgets


class CopyPasteTabBase(QtWidgets.QDialog):

    INFO = "Select a ng-skinned-mesh, then set each layers"

    def __init__(self, version, mll, control=None, mLayout=None):
        super(CopyPasteTabBase, self).__init__()

        self.mLayout = mLayout

        self.control = control
        self.progressStatus = False
        self.data = data.Data()

        # the object related to functions of ngSkinTools
        self.version = version
        self.mll = mll

        self.tabWidget = QtWidgets.QWidget()
        self.tabWidget.setMinimumSize(QtCore.QSize(400, 475))
        self.tabWidget.setMaximumSize(QtCore.QSize(10000, 10000))
        self.tabWidget.setObjectName("copyPasteTab")

        self.copyPasteTab_vLayout = QtWidgets.QVBoxLayout(self.tabWidget)
        self.copyPasteTab_vLayout.setContentsMargins(0, 0, 0, 0)
        self.copyPasteTab_vLayout.setObjectName("copyPasteTab_vLayout")

        self.expanding = QtWidgets.QSizePolicy.Expanding
        self.preferred = QtWidgets.QSizePolicy.Preferred
        self.minimum = QtWidgets.QSizePolicy.Minimum
        self.fixed = QtWidgets.QSizePolicy.Fixed

        self.layerSet_source_label = QtWidgets.QLabel()
        self.layerSet_source_lineEdit = QtWidgets.QLineEdit()
        self.layerSet_source_pushButton = QtWidgets.QPushButton()
        self.layerSet_destination_label = QtWidgets.QLabel()
        self.layerSet_destination_lineEdit = QtWidgets.QLineEdit()
        self.layerSet_destination_pushButton = QtWidgets.QPushButton()
        self.frameContent_line_1 = QtWidgets.QFrame()

        self.setting_applyMaskWeight_CB = QtWidgets.QCheckBox()
        self.setting_replace_radioButton = QtWidgets.QRadioButton()
        self.setting_add_radioButton = QtWidgets.QRadioButton()
        self.setting_subtract_radioButton = QtWidgets.QRadioButton()
        self.setting_cut_radioButton = QtWidgets.QRadioButton()
        self.frameContent_line_2 = QtWidgets.QFrame()

        self.sr_matchCase_CB = QtWidgets.QCheckBox()
        self.sr_result_label = QtWidgets.QLabel()
        self.sr_tableView = QtWidgets.QTableWidget()
        self.sr_preset_PB = QtWidgets.QPushButton()
        self.presetMenu = QtWidgets.QMenu(self.sr_preset_PB)
        self.import_pushButton = QtWidgets.QPushButton()
        self.export_pushButton = QtWidgets.QPushButton()
        self.plus_pushButton = QtWidgets.QPushButton()
        self.clear_pushButton = QtWidgets.QPushButton()

        self.applyAndClose_pushButton = QtWidgets.QPushButton()
        self.apply_pushButton = QtWidgets.QPushButton()
        self.close_pushButton = QtWidgets.QPushButton()

    def createWidget(self):
        self._srcDstLayerWidget()
        self._settingWidget()
        self._searchReplaceWidget()
        self._mainButtonWidget()

    def _srcDstLayerWidget(self):
        self.layerSet_source_label.setText("Source:")
        self.layerSet_source_label.setMinimumSize(QtCore.QSize(0, 22))
        self.layerSet_source_label.setAlignment(QtCore.Qt.AlignCenter)

        self.layerSet_source_lineEdit.setMinimumSize(QtCore.QSize(30, 20))
        self.layerSet_source_lineEdit.setReadOnly(True)
        self.layerSet_source_lineEdit.setDisabled(True)
        self.layerSet_source_lineEdit.setStyleSheet(
            "QLineEdit { background-color: #404040;"
            "border-radius: 3px;"
            "border-color: #505050;"
            "border-style: solid;"
            "border-width: 1.4px;}")

        self.layerSet_source_pushButton.setText("Set")
        self.layerSet_source_pushButton.setMinimumSize(QtCore.QSize(55, 21))
        self.layerSet_source_pushButton.setToolTip("Select a source layer and push this button")
        self.layerSet_source_pushButton.setStyleSheet(
            "QPushButton { background-color: #5D5D5D; border-radius: 4px;}"
            "QPushButton:pressed { background-color: #00A6F3;}"
            "QPushButton:hover:!pressed { background-color: #707070;}")

        self.layerSet_destination_label.setText("Destination:")
        self.layerSet_destination_label.setMinimumSize(QtCore.QSize(0, 22))
        self.layerSet_destination_label.setAlignment(QtCore.Qt.AlignCenter)

        self.layerSet_destination_lineEdit.setMinimumSize(QtCore.QSize(30, 20))
        self.layerSet_destination_lineEdit.setFrame(True)
        self.layerSet_destination_lineEdit.setReadOnly(True)
        self.layerSet_destination_lineEdit.setDisabled(True)
        self.layerSet_destination_lineEdit.setStyleSheet(
            "QLineEdit { background-color: #404040;"
            "border-radius: 3px;"
            "border-color: #505050;"
            "border-style: solid;"
            "border-width: 1.4px;}")

        self.layerSet_destination_pushButton.setText("Set")
        self.layerSet_destination_pushButton.setMinimumSize(QtCore.QSize(55, 21))
        self.layerSet_destination_pushButton.setToolTip("Select a destination layer and push this button")
        self.layerSet_destination_pushButton.setStyleSheet(
            "QPushButton { background-color: #5D5D5D; border-radius: 4px;}"
            "QPushButton:pressed { background-color: #00A6F3;}"
            "QPushButton:hover:!pressed { background-color: #707070;}")

        self.frameContent_line_1.setFrameShape(QtWidgets.QFrame.HLine)
        self.frameContent_line_1.setFrameShadow(QtWidgets.QFrame.Sunken)

    def _settingWidget(self):
        self.setting_applyMaskWeight_CB.setObjectName("setting_applyMaskWeight_CB")
        self.setting_applyMaskWeight_CB.setText("Apply mask weights")
        self.setting_applyMaskWeight_CB.setChecked(True)

        self.setting_replace_radioButton.setObjectName("setting_replace_radioButton")
        self.setting_replace_radioButton.setText("Replace")
        self.setting_replace_radioButton.setChecked(True)

        self.setting_add_radioButton.setObjectName("setting_add_radioButton")
        self.setting_add_radioButton.setText("Add")

        self.setting_subtract_radioButton.setObjectName("setting_subtract_radioButton")
        self.setting_subtract_radioButton.setText("Subtract")

        self.setting_cut_radioButton.setObjectName("setting_cut_radioButton")
        self.setting_cut_radioButton.setText("Cut")

        self.frameContent_line_2.setObjectName("frameContent_line_2")
        self.frameContent_line_2.setLineWidth(1)
        self.frameContent_line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.frameContent_line_2.setFrameShadow(QtWidgets.QFrame.Sunken)

    def _searchReplaceWidget(self):
        self.sr_matchCase_CB.setText("Show result")
        self.sr_matchCase_CB.setChecked(True)

        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(True)
        self.sr_result_label.setText("No matches")
        self.sr_result_label.setFont(font)

        self.sr_tableView.setFixedHeight(115)
        self.sr_tableView.setMinimumWidth(220)
        self.sr_tableView.setFocusPolicy(QtCore.Qt.NoFocus)
        self.sr_tableView.setShowGrid(True)
        self.sr_tableView.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.sr_tableView.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.sr_tableView.setRowCount(4)
        self.sr_tableView.setColumnCount(2)
        self.sr_tableView.setAlternatingRowColors(True)
        self.sr_tableView.setGridStyle(QtCore.Qt.DotLine)
        self.sr_tableView.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.sr_tableView.setHorizontalHeaderLabels(('Search', 'Replace'))

        for i in range(4):
            self.sr_tableView.setRowHeight(i, 23)

        self.sr_preset_PB.setObjectName("sr_preset_PB")
        self.sr_preset_PB.setText("Preset")
        self.sr_preset_PB.setEnabled(True)
        self.sr_preset_PB.setMinimumSize(QtCore.QSize(0, 25))
        self.sr_preset_PB.setAutoDefault(False)
        self.sr_preset_PB.setDefault(False)
        self.sr_preset_PB.setFlat(False)
        self.sr_preset_PB.setMenu(self.presetMenu)
        self.sr_preset_PB.setStyleSheet(
            "QPushButton { background-color: #5D5D5D; border-radius: 4px;}"
            "QPushButton:pressed { background-color: #00A6F3;}"
            "QPushButton:hover:!pressed { background-color: #707070;}")

        importIcon = QIcon()
        importIcon.addPixmap(QtGui.QPixmap(common.getIconPath("import.png")), QIcon.Normal, QIcon.Off)
        self.import_pushButton.setObjectName("import_export_pushButton")
        self.import_pushButton.setToolTip("Import a preset data from the file brower")
        self.import_pushButton.setMinimumSize(QtCore.QSize(16, 16))
        self.import_pushButton.setIcon(importIcon)
        self.import_pushButton.setFlat(True)

        exportIcon = QIcon()
        exportIcon.addPixmap(QtGui.QPixmap(common.getIconPath("export.png")), QIcon.Normal, QIcon.Off)
        self.export_pushButton.setObjectName("export_pushButton")
        self.export_pushButton.setToolTip("Export a current preset data")
        self.export_pushButton.setMinimumSize(QtCore.QSize(16, 16))
        self.export_pushButton.setIcon(exportIcon)
        self.export_pushButton.setIconSize(QtCore.QSize(16, 16))
        self.export_pushButton.setFlat(True)

        addIcon = QIcon()
        addIcon.addPixmap(QtGui.QPixmap(common.getIconPath("add.png")), QIcon.Normal, QIcon.Off)
        self.plus_pushButton.setObjectName("plus_pushButton")
        self.plus_pushButton.setToolTip("Add a new row in the table widget")
        self.plus_pushButton.setMinimumSize(QtCore.QSize(16, 16))
        self.plus_pushButton.setIcon(addIcon)
        self.plus_pushButton.setFlat(True)

        clearIcon = QIcon()
        clearIcon.addPixmap(QtGui.QPixmap(common.getIconPath("clear.png")), QIcon.Normal, QIcon.Off)
        self.clear_pushButton.setObjectName("clear_pushButton")
        self.clear_pushButton.setToolTip("Clear all items in the table widget")
        self.clear_pushButton.setMinimumSize(QtCore.QSize(16, 16))
        self.clear_pushButton.setIcon(clearIcon)
        self.clear_pushButton.setFlat(True)

    def _mainButtonWidget(self):
        self.applyAndClose_pushButton.setObjectName("applyAndClose_pushButton")
        self.applyAndClose_pushButton.setText("Apply and Close")
        self.applyAndClose_pushButton.setMinimumSize(QtCore.QSize(0, 27))
        self.applyAndClose_pushButton.setStyleSheet(
            "QPushButton { background-color: #5D5D5D; border-radius: 4px;}"
            "QPushButton:pressed { background-color: #00A6F3;}"
            "QPushButton:hover:!pressed { background-color: #707070;}")

        self.apply_pushButton.setObjectName("apply_pushButton")
        self.apply_pushButton.setText("Apply")
        self.apply_pushButton.setMinimumSize(QtCore.QSize(0, 27))
        self.apply_pushButton.setStyleSheet(
            "QPushButton { background-color: #5D5D5D; border-radius: 4px;}"
            "QPushButton:pressed { background-color: #00A6F3;}"
            "QPushButton:hover:!pressed { background-color: #707070;}")

        self.close_pushButton.setObjectName("close_pushButton")
        self.close_pushButton.setText("Close")
        self.close_pushButton.setMinimumSize(QtCore.QSize(0, 27))
        self.close_pushButton.setStyleSheet(
            "QPushButton { background-color: #5D5D5D; border-radius: 4px;}"
            "QPushButton:pressed { background-color: #00A6F3;}"
            "QPushButton:hover:!pressed { background-color: #707070;}")

    def setSignals(self):
        self.mLayout.displayBar.button.clicked.connect(self.deleteUnusedNgLayers)

        self.layerSet_source_pushButton.clicked.connect(self.setSourceField)
        self.layerSet_destination_pushButton.clicked.connect(self.setDistinationField)

        self.setting_replace_radioButton.clicked.connect(self.getMethod)
        self.setting_add_radioButton.clicked.connect(self.getMethod)
        self.setting_subtract_radioButton.clicked.connect(self.getMethod)
        self.setting_cut_radioButton.clicked.connect(self.getMethod)

        self.addPresetMenuAll()

        self.sr_tableView.itemChanged.connect(self.showMatchedNumber)

        self.import_pushButton.clicked.connect(self.importPreset)
        self.export_pushButton.clicked.connect(self.exportPreset)
        self.plus_pushButton.clicked.connect(self.insertRowTable)
        self.clear_pushButton.clicked.connect(self.clearTable)

        self.applyAndClose_pushButton.clicked.connect(self.applyAndClose)
        self.apply_pushButton.clicked.connect(self.apply)
        self.close_pushButton.clicked.connect(self.closeWindow)

    def deleteUnusedNgLayers(self):
        nodes = utils.getUnusedNgSkinLayerData()
        if nodes:
            cmds.delete(nodes)
            sys.stdout.write("Removed unused ngSkinLayers. >>> {}".format(nodes))

        self.changeInfoInitScreen()

    def changeInfoInitScreen(self):
        self.mLayout.displayBar.infoInitialState()

    def setSourceField(self):
        layerName, layerID = self.control.getCurrentLayer()
        if layerName is None:
            layerName = ""

        self.layerSet_source_lineEdit.setText(layerName)
        self.sourceLayerID = layerID

    def setDistinationField(self):
        layerName, layerID = self.control.getCurrentLayer()
        if not layerName:
            layerName = ""

        self.layerSet_destination_lineEdit.setText(layerName)
        self.destinationLayerID = layerID

    def importPreset(self):
        """Todo"""
        pass

    def clearTable(self):
        self.sr_tableView.clearContents()
        self.resetResultMatch()

    def exportPreset(self):
        """Todo"""
        pass

    def isApplyMask(self):
        if self.setting_applyMaskWeight_CB.isChecked():
            return True
        else:
            return False

    def getLayers(self):
        return self.sourceLayerID, self.destinationLayerID

    def getMethod(self):
        if self.setting_replace_radioButton.isChecked():
            return "replace"
        elif self.setting_add_radioButton.isChecked():
            return "add"
        elif self.setting_subtract_radioButton.isChecked():
            return "subtract"
        elif self.setting_cut_radioButton.isChecked():
            return "cut"

    def getSearchReplaceText(self):
        tokenAll = []
        for row in range(self.sr_tableView.rowCount()):
            tokenPair = []
            for col in range(2):
                items = self.sr_tableView.item(row, col)
                if not items:
                    continue
                tokenPair.append(items.text())
            if len(tokenPair) == 2:
                if tokenPair[0] == '' or tokenPair[1] == '':
                    continue
                tokenAll.append(tokenPair)
        return tokenAll

    def getNumberMatchedJoint(self):
        if not self.control:
            return None

        data = {'mesh': self.control.mesh,
                'layer': self.getLayers(),
                'method': self.getMethod(),
                'token': self.getSearchReplaceText(),
                'mask': self.isApplyMask()}

        self.control.setData(data)
        matchedNum = self.control.getNumberMatchedJoint(self.control)
        return matchedNum

    def resetResultMatch(self):
        self.sr_result_label.setText("No matches")

    def showMatchedNumber(self):
        num = self.getNumberMatchedJoint()
        if num is 0 or num is None:
            self.resetResultMatch()
        else:
            self.sr_result_label.setText("{} matches".format(num))

    def insertRowTable(self):
        newRow = self.sr_tableView.rowCount()
        self.sr_tableView.insertRow(newRow)
        self.sr_tableView.setRowHeight(newRow, 23)

    def addPresetMenuAll(self):
        faceAction = QtWidgets.QAction("Face", self.presetMenu)
        self.presetMenu.addAction(faceAction)
        bodyAction = QtWidgets.QAction("Body", self.presetMenu)
        self.presetMenu.addAction(bodyAction)
        fingerAction = QtWidgets.QAction("Finger", self.presetMenu)
        self.presetMenu.addAction(fingerAction)
        otherAction = QtWidgets.QAction("Other", self.presetMenu)
        self.presetMenu.addAction(otherAction)

        faceMenu = QtWidgets.QMenu()
        self.addMenuToPresetButton("upr", "lwr", faceMenu)
        self.addMenuToPresetButton("lwr", "up", faceMenu)
        self.addMenuToPresetButton("Socket", "Lid", faceMenu)
        faceAction.setMenu(faceMenu)

        fingerMenu = QtWidgets.QMenu()
        self.addMenuToPresetButton("01", "Base01", fingerMenu)
        self.addMenuToPresetButton("01", "Mid01", fingerMenu)
        self.addMenuToPresetButton("01", "Tip01", fingerMenu)
        fingerAction.setMenu(fingerMenu)

    def addMenuToPresetButton(self, search, replace, menu):
        callback = partial(self.assignSearchReplaceName, search, replace)
        menuItem = "{} -> {}".format(search, replace)
        menu.addAction(menuItem, callback)

    def assignSearchReplaceName(self, search, replace):
        searchItem = QtWidgets.QTableWidgetItem(search)
        replaceItem = QtWidgets.QTableWidgetItem(replace)
        itemSize = len(self.getSearchReplaceText())

        self.sr_tableView.setItem(itemSize, 0, searchItem)
        self.sr_tableView.setItem(itemSize, 1, replaceItem)

    def updateVisbilityInfomationBar(self):
        if self.progressStatus:
            self.mLayout.progressBar.setVisible(True)
        else:
            self.mLayout.progressBar.setVisible(False)

    def runProgress(self):
        if self.progressStatus:
            return

        utils.hasSkinLayer(self.control.mesh)
        indentKey, nameKey = self.control.getInfluenceData()
        infNames, infIDs = self.control.getUsedInfluenceData(indentKey, nameKey)
        remapData = self.control.storeRemapData(infIDs, infNames, nameKey)

        self.progressStatus = True
        self.mLayout.progressBar.setValue(0)
        self.updateVisbilityInfomationBar()

        for i, data in enumerate(remapData.items(), 1):
            currentNumOperation = float(i)
            numberOfOperation = float(len(remapData.values()))
            progress = 100.0 * (currentNumOperation / numberOfOperation)
            self.mLayout.progressBar.setValue(progress)

            weightsObj, weightMask = self.control.copyWeights(data[0])
            self.control.pasteWeights(weightsObj, weightMask, data[1])
        self.mLayout.displayBar.successCopyPaste(self.getMethod())

        timer = QTimer()
        timer.singleShot(3000, self.changeInfoInitScreen)

        self.progressStatus = False
        self.updateVisbilityInfomationBar()

    def apply(self):
        data = {'mesh': self.control.mesh,
                'layer': self.getLayers(),
                'method': self.getMethod(),
                'token': self.getSearchReplaceText(),
                'mask': self.isApplyMask()}

        self.control.setData(data)
        self.runProgress()

    def closeWindow(self):
        self.mLayout.close()

    def applyAndClose(self):
        self.apply()
        self.close()


class BuildTabBase(QtWidgets.QWidget):
    INFO = "Easily create layers / assign initial weights on a selected-mesh"
    HELP_URL = "https://confluence.reelfx.com/display/RIG/Upper+Head+Convenience+Functions"

    def __init__(self, version, mll, control=None, mLayout=None):
        super(BuildTabBase, self).__init__()

        self.mLayout = mLayout

        self.version = version
        self.mll = mll
        self.control = control
        self.data = data.Data()

        # Main widget for build tab
        self.tabWidget = QtWidgets.QWidget()
        self.tabWidget.setObjectName("buildTab")

        # timer instance
        self.timer = QTimer()

        # QSizePolicy
        self.expanding = QtWidgets.QSizePolicy.Expanding
        self.preferred = QtWidgets.QSizePolicy.Preferred
        self.minimum = QtWidgets.QSizePolicy.Minimum
        self.fixed = QtWidgets.QSizePolicy.Fixed

        # Main layout for the buildTab
        self.buildMainVLayout = QtWidgets.QVBoxLayout(self.tabWidget)
        self.buildMainVLayout.setObjectName("buildMainVLayout")
        self.buildMainVLayout.setContentsMargins(20, 20, 20, 20)

        # Sub layouts for each widgets
        self.buildCreateLayersGroup = QtWidgets.QGroupBox(self.tabWidget)
        self.buildCreateLayersVLayout = QtWidgets.QVBoxLayout(self.buildCreateLayersGroup)
        self.buildCreateLayersHLayout = QtWidgets.QHBoxLayout(self.buildCreateLayersGroup)
        self.buildCreateButtonHLayout = QtWidgets.QHBoxLayout(self.buildCreateLayersGroup)

        self.buildSettingPb = QtWidgets.QPushButton(self.buildCreateLayersGroup)
        self.buildSettingMenu = QtWidgets.QMenu(self.buildSettingPb)

        self.presetTree = CustomTreeWidgets(types="preset",
                                            parent=self.buildCreateLayersGroup)
        self.layerTree = CustomTreeWidgets(widgets=self.presetTree,
                                           types="layer",
                                           parent=self.buildCreateLayersGroup)

        self.layerData = layerManagerBase.LayerPresetData(self.presetTree)

        # The preset and the layer tree widgets
        self.widgets = {"preset": self.presetTree, "layer": self.layerTree}
        self.setter = layerManagerBase.TreeWidgetSetter(self.widgets)

        # The button object to generate layers
        self.buildCreateButtonPb = QtWidgets.QPushButton(self.buildCreateLayersGroup)

        self.buildAssignWeightsGroup = QtWidgets.QGroupBox(self.tabWidget)
        self.buildAssignWeightsVLayout = QtWidgets.QVBoxLayout(self.buildAssignWeightsGroup)
        self.buildReelfxLabelHLayout = QtWidgets.QHBoxLayout(self.buildAssignWeightsGroup)
        self.buildReelfxLabel = QtWidgets.QLabel(self.buildAssignWeightsGroup)
        self.buildAssignWeightsHLayout = QtWidgets.QHBoxLayout(self.buildAssignWeightsGroup)
        self.buildReelfxPresetCb = QtWidgets.QComboBox(self.buildAssignWeightsGroup)
        self.buildReelfxPresetPb = QtWidgets.QPushButton(self.buildAssignWeightsGroup)
        self.buildReelfxHelpPb = QtWidgets.QPushButton(self.buildAssignWeightsGroup)

    def getControl(self, mesh):
        """Get an object of createLayer class

        :param
            parent: object of layout
        :return: object of creayLayer class
        """
        if mesh is None:
            message = "Please select any ng-skinned mesh"
            self.mLayout.displayBar.errorScreen(message)
            return None

        verName = utils.getToolVersion(mesh)
        control = layerManagerBase.getVersionControl(verName, self.presetTree)
        return control

    def createLayersWidget(self):
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(True)
        self.buildCreateLayersGroup.setTitle("Create Layer")
        self.buildCreateLayersGroup.setFont(font)
        self.buildCreateLayersGroup.setObjectName("buildCreateLayersGroup")

        self.buildCreateLayersVLayout.setObjectName("buildCreateLayersVLayout")
        self.buildCreateLayersVLayout.setContentsMargins(10, 10, 10, 10)

        self.buildCreateLayersHLayout.setSpacing(2)
        self.buildCreateLayersHLayout.setObjectName("buildCreateLayersHLayout")

        self.buildCreateButtonHLayout.setSpacing(3)
        self.buildCreateButtonHLayout.setObjectName("buildCreateButtonHLayout")

        self.buildCreateButtonPb.setText("Create")
        self.buildCreateButtonPb.setObjectName("buildCreateButtonPb")
        self.buildCreateButtonPb.setToolTip("Create ngLayer structures on the skinned mesh using a user-defined preset")
        self.buildCreateButtonPb.setMinimumSize(QtCore.QSize(300, 25))
        self.buildCreateButtonPb.setSizePolicy(self.expanding, self.fixed)

        self.buildCreateButtonPb.setStyleSheet(
            "QPushButton { background-color: #5D5D5D; border-radius: 4px;}"
            "QPushButton:pressed { background-color: #00A6F3;}"
            "QPushButton:hover:!pressed { background-color: #707070;}")

        settingIcon = QIcon()
        settingIcon.addPixmap(QtGui.QPixmap(common.getIconPath("setting.png")), QIcon.Normal, QIcon.Off)
        self.buildSettingPb.setObjectName("buildSettingPb")
        self.buildSettingPb.setMinimumSize(25, 25)
        self.buildSettingPb.setIcon(settingIcon)
        self.buildSettingPb.setFlat(False)
        self.buildSettingPb.setMenu(self.buildSettingMenu)
        self.buildSettingPb.setStyleSheet(
            "QPushButton { background-color: #5D5D5D; border-radius: 4px;}"
            "QPushButton:pressed { background-color: #00A6F3;}"
            "QPushButton:hover:!pressed { background-color: #707070;}")

    def assignInitialWeightWidget(self):
        font = QtGui.QFont()
        font.setPointSize(8)
        self.buildAssignWeightsGroup.setTitle("Assign Initial Weights")
        self.buildAssignWeightsGroup.setFont(font)
        self.buildAssignWeightsGroup.setObjectName("buildAssignWeightsGroup")

        font = QtGui.QFont()
        font.setPointSize(7)
        self.buildReelfxLabelHLayout.setContentsMargins(32, 0, 0, 0)
        self.buildReelfxLabel.setText("Reel FX Presets:")
        self.buildReelfxLabel.setFont(font)

        helpIcon = QIcon()
        helpIcon.addPixmap(QtGui.QPixmap(common.getIconPath("question.png")), QIcon.Normal, QIcon.Off)
        self.buildReelfxHelpPb.setObjectName("buildReelfxHelpPb")
        self.buildReelfxHelpPb.setMinimumSize(16, 16)
        self.buildReelfxHelpPb.setIcon(helpIcon)
        self.buildReelfxHelpPb.setFlat(True)

        self.buildAssignWeightsHLayout.setContentsMargins(30, 0, 30, 20)
        self.buildAssignWeightsHLayout.setObjectName("buildAssignWeightsHLayout")

        self.buildReelfxPresetCb.setMinimumSize(QtCore.QSize(50, 25))
        self.buildReelfxPresetCb.setObjectName("buildReelfxPresetCb")
        self.buildReelfxPresetCb.addItem("Face - Brow")
        self.buildReelfxPresetCb.addItem("Face - BrowTwist")
        self.buildReelfxPresetCb.addItem("Face - Eyelids")
        self.buildReelfxPresetCb.addItem("Face - Socket")
        self.buildReelfxPresetCb.addItem("Face - Squints")
        self.buildReelfxPresetCb.addItem("Face - Lips")
        self.buildReelfxPresetCb.addItem("Face - LipsScale")

        self.buildReelfxPresetPb.setObjectName("buildReelfxPresetPb")
        self.buildReelfxPresetPb.setText("Assign")
        self.buildReelfxPresetPb.setToolTip("Assign initial weights with the current preset comboBox")
        self.buildReelfxPresetPb.setMinimumSize(QtCore.QSize(0, 25))
        self.buildReelfxPresetPb.setStyleSheet(
            "QPushButton { background-color: #5D5D5D; border-radius: 4px;}"
            "QPushButton:pressed { background-color: #00A6F3;}"
            "QPushButton:hover:!pressed { background-color: #707070;}")

    def createLayers(self):
        meshes = utils.getSkinnedMesh(mode=1)
        if not meshes:
            message = "Please select any skinned mesh"
            self.mLayout.displayBar.errorScreen(message)
            self.timer.singleShot(2000, self.changeInfoInitScreen)
            return

        # create layers on the selected mesh
        for mesh in meshes:
            control = self.control(self.layerTree, self.mLayout)
            control.createLayer(mesh)

        message = "Created all defined-layers in the selected mesh"
        self.mLayout.displayBar.successScreen(message)

        self.timer.singleShot(3000, self.changeInfoInitScreen)

    def changeInfoInitScreen(self):
        self.mLayout.displayBar.initScreen(self.INFO)

    def menuSetting(self):
        saveIcon = QIcon()
        saveIcon.addPixmap(QtGui.QPixmap(common.getIconPath("save.png")), QIcon.Normal, QIcon.Off)
        saveAction = QtWidgets.QAction("Save Presets", self.buildSettingMenu)
        saveAction.setIcon(saveIcon)
        saveAction.triggered.connect(self.layerData.exportFile)
        self.buildSettingMenu.addAction(saveAction)

        separatorAction = QtWidgets.QAction(self.buildSettingMenu)
        separatorAction.setSeparator(True)
        self.buildSettingMenu.addAction(separatorAction)

        importIcon = QIcon()
        importIcon.addPixmap(QtGui.QPixmap(common.getIconPath("import.png")), QIcon.Normal, QIcon.Off)
        importAction = QtWidgets.QAction("Import Preset File", self.buildSettingMenu)
        importAction.setIcon(importIcon)
        importAction.triggered.connect(self.layerData.loadFile)
        self.buildSettingMenu.addAction(importAction)

        exportIcon = QIcon()
        exportIcon.addPixmap(QtGui.QPixmap(common.getIconPath("export.png")), QIcon.Normal, QIcon.Off)
        exportAction = QtWidgets.QAction("Export Preset File", self.buildSettingMenu)
        exportAction.setIcon(exportIcon)
        exportAction.triggered.connect(self.layerData.exportFileAs)
        self.buildSettingMenu.addAction(exportAction)

    def openHelpPage(self):
        """Open a confluence page for the tool
        """
        webbrowser.open(self.HELP_URL)

    def layout(self):
        self.buildCreateLayersHLayout.addWidget(self.presetTree)
        self.buildCreateLayersHLayout.addWidget(self.layerTree)

        self.buildCreateButtonHLayout.addWidget(self.buildCreateButtonPb)
        self.buildCreateButtonHLayout.addWidget(self.buildSettingPb)

        self.buildCreateLayersVLayout.addLayout(self.buildCreateLayersHLayout)
        self.buildCreateLayersVLayout.addLayout(self.buildCreateButtonHLayout)

        self.buildReelfxLabelHLayout.addWidget(self.buildReelfxLabel)
        self.buildReelfxLabelHLayout.addWidget(self.buildReelfxHelpPb)
        self.buildReelfxLabelHLayout.addStretch()
        self.buildAssignWeightsHLayout.addWidget(self.buildReelfxPresetCb)
        self.buildAssignWeightsHLayout.addWidget(self.buildReelfxPresetPb)

        self.buildAssignWeightsVLayout.addLayout(self.buildReelfxLabelHLayout)
        self.buildAssignWeightsVLayout.addLayout(self.buildAssignWeightsHLayout)

        self.buildMainVLayout.addWidget(self.buildCreateLayersGroup)
        self.buildMainVLayout.addWidget(self.buildAssignWeightsGroup)

        self.tabWidget.setLayout(self.buildMainVLayout)


class MirrorTabBase(QtWidgets.QWidget):
    INFO = "Mirror functions for a selected-ng-skinned-mesh"

    def __init__(self, version, mll, control=None, mLayout=None):
        """Initirize for utils tab

        :param mLayout:
        """
        super(MirrorTabBase, self).__init__()

        # main layout
        self.mLayout = mLayout

        self.version = version
        self.mll = mll
        self.control = control

        # timer instance
        self.timer = QTimer()

        # main utility widget
        self.tabWidget = QtWidgets.QWidget()
        self.tabWidget.setObjectName("mirrorTab")

        # define each of sizePolicies
        self.expanding = QtWidgets.QSizePolicy.Expanding
        self.preferred = QtWidgets.QSizePolicy.Preferred
        self.minimum = QtWidgets.QSizePolicy.Minimum
        self.fixed = QtWidgets.QSizePolicy.Fixed

        # construct a main vertical box layout
        self.mirrorMainVLayout = QtWidgets.QVBoxLayout(self.tabWidget)
        self.mirrorMainVLayout.setObjectName("mirrorMainVLayout")
        self.mirrorMainVLayout.setSpacing(20)
        self.mirrorMainVLayout.setContentsMargins(20, 20, 20, 20)

    def changeInfoInitScreen(self):
        self.mLayout.displayBar.initScreen(self.INFO)


class UtilTabBase(QtWidgets.QWidget):
    INFO = "Utility functions for a selected-ng-skinned-mesh"

    def __init__(self, version, mll, control=None, mLayout=None):
        """Initirize for utils tab

        :param mLayout:
        """
        super(UtilTabBase, self).__init__()

        # main layout
        self.mLayout = mLayout

        self.version = version
        self.mll = mll
        self.control = control

        # timer instance
        self.timer = QTimer()

        # main utility widget
        self.tabWidget = QtWidgets.QWidget()
        self.tabWidget.setObjectName("utilTab")

        # define each of sizePolicies
        self.expanding = QtWidgets.QSizePolicy.Expanding
        self.preferred = QtWidgets.QSizePolicy.Preferred
        self.minimum = QtWidgets.QSizePolicy.Minimum
        self.fixed = QtWidgets.QSizePolicy.Fixed

        # construct a main vertical box layout
        self.utilMainVLayout = QtWidgets.QVBoxLayout(self.tabWidget)
        self.utilMainVLayout.setObjectName("utilMainVLayout")
        self.utilMainVLayout.setSpacing(20)
        self.utilMainVLayout.setContentsMargins(20, 20, 20, 20)

        # construct all of widgets needed in util tab
        self.convertLayerDataGroup = QtWidgets.QGroupBox(self.tabWidget)
        self.convertGroupVLayout = QtWidgets.QVBoxLayout(self.convertLayerDataGroup)
        self.convertBtnHLayout = QtWidgets.QHBoxLayout(self.convertLayerDataGroup)

        self.convertLaunchCBHLayout = QtWidgets.QHBoxLayout(self.convertLayerDataGroup)
        self.convertLaunchCB = QtWidgets.QCheckBox(self.convertLayerDataGroup)

        self.convertSeparatorLine1HLayout = QtWidgets.QHBoxLayout(self.convertLayerDataGroup)
        self.convertSeparatorLine1 = QtWidgets.QFrame(self.convertLayerDataGroup)

        self.convertBtn = QtWidgets.QPushButton(self.convertLayerDataGroup)
        self.convertOptionHLayout = QtWidgets.QHBoxLayout()
        self.convertOption1RadioBtn = QtWidgets.QRadioButton()
        self.convertOption2RadioBtn = QtWidgets.QRadioButton()

        # the object related to functions of ngSkinTools
        if not utils.IS_NG1:
            self.convertBtn.setEnabled(False)

        if not utils.IS_NG2:
            self.convertBtn.setEnabled(False)

    def convertWidget(self):
        """Construct the convert widget
        """
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(True)
        self.convertLayerDataGroup.setTitle("Convert Layer Data")
        self.convertLayerDataGroup.setFont(font)
        self.convertLayerDataGroup.setObjectName("convertLayerDataGroup")

        self.convertGroupVLayout.setSpacing(0)
        self.convertGroupVLayout.setContentsMargins(0, 5, 0, 15)
        self.convertGroupVLayout.setObjectName("convertGroupVLayout")

        font = QtGui.QFont()
        font.setPointSize(7)
        self.convertLaunchCBHLayout.setContentsMargins(5, 10, 0, 5)
        name = "Launch ngSkin{} Helper Tool"
        if self.version == utils.NG1_VERSION:
            self.convertLaunchCB.setText(name.format("2"))
        else:
            self.convertLaunchCB.setText(name.format("1"))

        self.convertLaunchCB.setFont(font)
        self.convertLaunchCB.setChecked(True)

        self.convertSeparatorLine1HLayout.setContentsMargins(10, 3, 10, 3)
        self.convertSeparatorLine1.setFixedWidth(240)
        self.convertSeparatorLine1.setFrameShape(QtWidgets.QFrame.HLine)
        self.convertSeparatorLine1.setFrameShadow(QtWidgets.QFrame.Sunken)

        self.convertOptionHLayout.setSpacing(10)
        self.convertOptionHLayout.setObjectName("convertOptionHLayout")

        self.convertOption1RadioBtn.setObjectName("convertOption1RadioBtn")
        self.convertOption1RadioBtn.setText("Selected")
        self.convertOption1RadioBtn.setChecked(True)

        self.convertOption2RadioBtn.setObjectName("convertOption2RadioBtn")
        self.convertOption2RadioBtn.setText("Scene")

        self.convertBtnHLayout.setSpacing(0)
        self.convertBtnHLayout.setContentsMargins(10, 10, 10, 0)
        self.convertBtnHLayout.setObjectName("convertBtnHLayout")

        self.convertBtn.setMinimumSize(QtCore.QSize(160, 25))
        self.convertBtn.setObjectName("convertBtn")
        self.convertBtn.setText("Convert")
        self.convertBtn.setToolTip("Convert the ngSkinToolData to upgrade or downgrade the version of ngSkinTools")
        self.convertBtn.setStyleSheet(
            "QPushButton { background-color: #5D5D5D; border-radius: 4px;}"
            "QPushButton:pressed { background-color: #00A6F3;}"
            "QPushButton:hover:!pressed { background-color: #707070;}")

    def changeInfoInitScreen(self):
        self.mLayout.displayBar.initScreen(self.INFO)

    def convert(self):
        meshes = None
        # selection mode
        if self.convertOption1RadioBtn.isChecked():
            meshes = utils.getNgSkinnedMesh(mode=1)
        # all skinned-meshes mode
        elif self.convertOption2RadioBtn.isChecked():
            meshes = utils.getNgSkinnedMesh(mode=2)

        if not meshes:
            message = "Please select any ng-skinned mesh"
            self.mLayout.displayBar.errorScreen(message)
            self.timer.singleShot(2000, self.changeInfoInitScreen)
            return

        for mesh in meshes:
            # the mesh needs to be selected for the convert process
            if self.convertOption2RadioBtn.isChecked():
                cmds.select(cl=True)
                cmds.select(mesh)
            self.control.convert(mesh)

        if self.convertLaunchCB.isChecked():
            self.mLayout.close()
            if self.version == utils.NG1_VERSION:
                from rig_tools.tool.ngSkinHelperTool import ng2MainUI
                ng2MainUI.main(3)
            else:
                from rig_tools.tool.ngSkinHelperTool import ng1MainUI
                ng1MainUI.main(3)


