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
import logging
import os

# Third Party
import maya.cmds as cmds
import maya.OpenMayaUI as OpenMayaUI
import ngSkinTools2.mllInterface
from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtGui import QIcon

# Reel-fx modules
import rig_tools.ui.pyside.util as pyqt_util

# Local modules
from rig_tools.tool.ngSkinHelperTool.util import utils, common
from rig_tools.tool.ngSkinHelperTool.widgets import widget, tabWidget
from rig_tools.tool.ngSkinHelperTool.widgets.widget import MainLayout
from rig_tools.tool.ngSkinHelperTool.tabInternal import layerManagerBase
from rig_tools.tool.ngSkinHelperTool.tabInternal.version2 import copyPaste
from rig_tools.tool.ngSkinHelperTool.tabInternal.version2 import layerCreation
from rig_tools.tool.ngSkinHelperTool.tabInternal.version2 import mirrorHelper
from rig_tools.tool.ngSkinHelperTool.tabInternal.version2 import convert
from rig_tools.tool.ngSkinHelperTool.tabInternal.version2 import assignWeights
from rig_tools.tool.ngSkinHelperTool.tabInternal.version2 import clipboardWeights

# ----------------------------------------------------------------- GLOBALS --#
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

utils.checkNgSkinToolsPlugins()


class MainTabInfo:

    def __init__(self, parent):
        self.tabNames = ["CopyPaste", "Build", "Mirror", "Utils"]
        self.controlMapping = {
            "CopyPaste": copyPaste.NgSkinControlV2(),
            "Build": layerCreation.NgLayerControlV2,
            "Mirror": mirrorHelper.NgControlV2(parent),
            "Utils": convert.NgControlV2(parent)
        }


class MainWindow(MainLayout):
    TITLE_NAME = "ngSkin2 Helper Tool"

    def __init__(self, tabIndex, parent=None):
        super(MainWindow, self).__init__(self.TITLE_NAME, parent)

        self.sourceLayerID = None
        self.destinationLayerID = None
        self.control = None

        # the object related to functions of ngSkinTools
        self.mll2 = ngSkinTools2.mllInterface.MllInterface()
        self.version = utils.NG2_VERSION

        # the procedures of building UI
        self.setWindowTitle(self.TITLE_NAME)
        self.createWidgets()
        self.mainLayout.setMenuBar(self.createMenuItems(self))
        self.layout()

        # Tab information
        self.tabInfo = {}

        # Create tabs dynamically
        mainTabInfo = MainTabInfo(self)
        for name in mainTabInfo.tabNames:
            tabClass = globals().get("{}Tab".format(name))
            controlClass = mainTabInfo.controlMapping.get(name)

            if not tabClass and not controlClass:
                continue

            tabClass = tabClass(self.version,
                                self.mll2,
                                control=controlClass,
                                mLayout=self)

            self.tabInfo[name] = {"tab": tabClass, "name": name, "msg": tabClass.INFO}

        # Add tabs to main tab widget
        for name in mainTabInfo.tabNames:
            tabData = self.tabInfo.get(name)
            self.mainTabWidget.addTab(tabData["tab"].tabWidget, tabData["name"])

        self.mainTabWidget.setCurrentIndex(tabIndex)
        self.mainTabWidget.currentChanged.connect(lambda: self.switchInfoBar(self.tabInfo))

        self.windowPreferences = self._applyInitialConfig()

        self.selectionChangedCallback()
        self.initSelectionChangedCallback()

        ngLayerData = utils.getUnusedNgSkinLayerData()
        if ngLayerData:
            self.displayBar.warningUnusedNgLayerData(ngLayerData)
            log.info(ngLayerData)

    def _applyInitialConfig(self, **kwargs):
        """Derives the default configuration dictionary and applies the configuration to this window.

        :parameters:
            kwargs : dict
                A dictionary of defined configuration.
        """
        # get default class-defined configuration
        config = self.getDefaultConfig()

        # override default class configuration with input arguments
        config.update(kwargs)

        # override configuration with configuration in preferences
        try:
            config.update(self.loadPreferences(defaultData=config))
        except Exception as e:
            self.logger.exception("Error occurred while loading preferences: %s", e)

        layerData = config.get("layerPreset")
        presetTree = self.tabInfo["Build"]["tab"].widgets["preset"]
        database = layerManagerBase.LayerPresetData(presetTree)
        database.loadFile(layerData)

        self.setSize(config.get('width'), config.get('height'))
        self.setPosition(config.get('x'), config.get('y'))
        return config

    def showEvent(self, event):
        """Restore the window geometry once show events are sent just after the window system shows the window.

        :param event:
        """
        if os.path.exists(self.prefPath):
            settingsObj = QtCore.QSettings(self.prefPath, QtCore.QSettings.IniFormat)
            self.restoreGeometry(settingsObj.value("windowGeometry"))

    def closeEvent(self, event):
        """Close events are sent to widgets that the user wants to close,
        usually by choosing Close from the window menu, or by clicking the X title bar button

        :param event:
        """
        if self.prefPath:
            presetTree = self.tabInfo["Build"]["tab"].widgets["preset"]
            getter = layerManagerBase.TreeWidgetReader(presetTree)
            layerData = getter.getAllItems()
            self.windowPreferences.update(self.getWindowState())
            self.windowPreferences.update(layerPreset=layerData)
            self.savePreferences(prefData=self.windowPreferences)


class CopyPasteTab(tabWidget.CopyPasteTabBase):

    def __init__(self, version, mll, control=None, mLayout=None):
        super(CopyPasteTab, self).__init__(version, mll, control, mLayout)

        self.layerSetMainVLayout = QtWidgets.QVBoxLayout()
        self.layerSetSourceHLayout = QtWidgets.QHBoxLayout()
        self.layerSetDestinationHLayout = QtWidgets.QHBoxLayout()
        self.settingsGroupBoxHLayout = QtWidgets.QVBoxLayout(self.tabWidget)
        self.settingsGroupBox = QtWidgets.QGroupBox(self.tabWidget)
        self.settingMainVLayout = QtWidgets.QVBoxLayout(self.settingsGroupBox)

        self.settingsContentsVLayout = QtWidgets.QVBoxLayout(self.settingsGroupBox)
        self.settingHLayout1 = QtWidgets.QHBoxLayout(self.settingsGroupBox)
        self.settingHLayout2 = QtWidgets.QHBoxLayout(self.settingsGroupBox)

        self.srMainGroupBoxHLayout = QtWidgets.QVBoxLayout(self.tabWidget)
        self.srGroupBox = QtWidgets.QGroupBox(self.tabWidget)
        self.srMainVLayout = QtWidgets.QVBoxLayout(self.srGroupBox)
        self.srSubHLayout = QtWidgets.QHBoxLayout(self.srGroupBox)
        self.srOptionHLayout = QtWidgets.QHBoxLayout()
        self.srTableViewVLayout = QtWidgets.QVBoxLayout(self.srGroupBox)
        self.srToolsVLayout = QtWidgets.QVBoxLayout(self.srGroupBox)
        self.applyButtonHLayout = QtWidgets.QHBoxLayout()

        self.createWidget()
        self.layout()
        self.setSignals()

    def layout(self):
        self.layerSetLayout()
        self.settingsLayout()
        self.searchReplaceLayout()
        self.mainButtonLayout()

    def layerSetLayout(self):
        self.layerSetMainVLayout.setSpacing(2)
        self.layerSetMainVLayout.setContentsMargins(-1, 15, -1, 16)

        self.layerSetSourceHLayout.setSpacing(4)
        self.layerSetSourceHLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.layerSetSourceHLayout.setContentsMargins(45, -1, 70, -1)

        self.layerSetDestinationHLayout.setSpacing(4)
        self.layerSetDestinationHLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.layerSetDestinationHLayout.setContentsMargins(50, -1, 70, -1)

        self.layerSetSourceHLayout.addSpacing(25)
        self.layerSetSourceHLayout.addWidget(self.layerSet_source_label)
        self.layerSetSourceHLayout.addWidget(self.layerSet_source_lineEdit)
        self.layerSetSourceHLayout.addWidget(self.layerSet_source_pushButton)
        self.layerSetDestinationHLayout.addWidget(self.layerSet_destination_label)
        self.layerSetDestinationHLayout.addWidget(self.layerSet_destination_lineEdit)
        self.layerSetDestinationHLayout.addWidget(self.layerSet_destination_pushButton)
        self.layerSetMainVLayout.addLayout(self.layerSetSourceHLayout)
        self.layerSetMainVLayout.addLayout(self.layerSetDestinationHLayout)
        self.copyPasteTab_vLayout.addLayout(self.layerSetMainVLayout)

    def settingsLayout(self):
        self.settingsGroupBoxHLayout.setObjectName("settingsGroupBoxHLayout")
        self.settingsGroupBoxHLayout.setContentsMargins(20, 0, 20, 0)

        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(True)
        self.settingsGroupBox.setTitle("Settings:")
        self.settingsGroupBox.setObjectName("settingsGroupBox")
        self.settingsGroupBox.setFont(font)

        self.settingMainVLayout.setObjectName("settingMainVLayout")
        self.settingMainVLayout.setSpacing(3)
        self.settingMainVLayout.setContentsMargins(-1, 8, -1, 20)

        self.settingsContentsVLayout.setObjectName("settingsContentsVLayout")
        self.settingsContentsVLayout.setSpacing(12)
        self.settingsContentsVLayout.setContentsMargins(0, 2, 0, 0)

        self.settingHLayout1.setObjectName("settingHLayout1")
        self.settingHLayout1.setSpacing(2)
        self.settingHLayout1.setContentsMargins(60, -1, 50, -1)

        self.settingHLayout2.setObjectName("settingHLayout2")
        self.settingHLayout2.setSpacing(2)
        self.settingHLayout2.setContentsMargins(60, -1, 50, -1)

        self.settingHLayout1.addWidget(self.setting_replace_radioButton)
        self.settingHLayout1.addWidget(self.setting_add_radioButton)
        self.settingHLayout1.addWidget(self.setting_subtract_radioButton)
        self.settingHLayout1.addWidget(self.setting_cut_radioButton)
        self.settingHLayout2.addWidget(self.setting_applyMaskWeight_CB)
        self.settingsContentsVLayout.addLayout(self.settingHLayout1)
        self.settingsContentsVLayout.addLayout(self.settingHLayout2)
        self.settingMainVLayout.addLayout(self.settingsContentsVLayout)
        self.settingsGroupBoxHLayout.addWidget(self.settingsGroupBox)
        self.copyPasteTab_vLayout.addLayout(self.settingsGroupBoxHLayout)
        self.copyPasteTab_vLayout.addLayout(self.settingMainVLayout)

    def searchReplaceLayout(self):
        self.srMainGroupBoxHLayout.setObjectName("srMainGroupBoxHLayout")
        self.srMainGroupBoxHLayout.setContentsMargins(20, 0, 20, 0)

        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(True)
        self.srGroupBox.setTitle("Replacement Token :")
        self.srGroupBox.setObjectName("srGroupBox")
        self.srGroupBox.setFont(font)

        self.srMainVLayout.setSpacing(10)
        self.srMainVLayout.setContentsMargins(0, 12, 0, 30)

        self.srSubHLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.srSubHLayout.setContentsMargins(60, 0, 0, 0)

        self.srOptionHLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)

        self.srTableViewVLayout.setSpacing(2)
        self.srTableViewVLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)

        horizontalMatchSpacer = QtWidgets.QSpacerItem(40, 0, self.expanding, self.minimum)
        verticalToolsSpacer1 = QtWidgets.QSpacerItem(0, 80, self.minimum, self.expanding)
        verticalToolsSpacer2 = QtWidgets.QSpacerItem(0, 50, self.minimum, self.expanding)
        horizontalSpacerSub2 = QtWidgets.QSpacerItem(50, 0, self.expanding, self.minimum)
        verticalSpacerItemTable = QtWidgets.QSpacerItem(0, 1000, self.minimum, self.expanding)

        self.srToolsVLayout.setSpacing(4)
        self.srToolsVLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)

        self.srOptionHLayout.addWidget(self.sr_result_label)
        self.srTableViewVLayout.addLayout(self.srOptionHLayout)
        self.srTableViewVLayout.addWidget(self.sr_tableView)
        self.srTableViewVLayout.addWidget(self.sr_preset_PB)
        self.srToolsVLayout.addItem(verticalToolsSpacer1)
        self.srToolsVLayout.addWidget(self.import_pushButton)
        self.srToolsVLayout.addWidget(self.export_pushButton)
        self.srToolsVLayout.addWidget(self.plus_pushButton)
        self.srToolsVLayout.addWidget(self.clear_pushButton)
        self.srToolsVLayout.addItem(verticalToolsSpacer2)

        self.srMainGroupBoxHLayout.addWidget(self.srGroupBox)
        self.srSubHLayout.addLayout(self.srTableViewVLayout)
        self.srSubHLayout.addLayout(self.srToolsVLayout)
        self.srSubHLayout.addItem(horizontalSpacerSub2)
        self.srMainVLayout.addLayout(self.srSubHLayout)
        self.srMainVLayout.addItem(verticalSpacerItemTable)
        self.copyPasteTab_vLayout.addLayout(self.srMainGroupBoxHLayout)
        self.copyPasteTab_vLayout.addLayout(self.srMainVLayout)

    def mainButtonLayout(self):
        self.applyButtonHLayout.setObjectName("applyButtonHLayout")
        self.applyButtonHLayout.setSpacing(4)
        self.applyButtonHLayout.setContentsMargins(3, 8, 3, 8)

        self.applyButtonHLayout.addWidget(self.applyAndClose_pushButton)
        self.applyButtonHLayout.addWidget(self.apply_pushButton)
        self.applyButtonHLayout.addWidget(self.close_pushButton)

        self.copyPasteTab_vLayout.addLayout(self.applyButtonHLayout)


class BuildTab(tabWidget.BuildTabBase):

    def __init__(self, version, mll, control=None, mLayout=None):
        super(BuildTab, self).__init__(version, mll, control, mLayout)

        self.createWidets()
        self.layout()
        self.setSignals()

    def createWidets(self):
        self.createLayersWidget()
        self.assignInitialWeightWidget()

    def setSignals(self):
        self.presetTree.itemSelectionChanged.connect(self.setter.onItemChanged)
        self.presetTree.itemChanged.connect(lambda: self.setter.editPresetItem())
        self.layerTree.itemChanged.connect(lambda: self.setter.editLayerItem())
        self.buildReelfxHelpPb.clicked.connect(self.openHelpPage)
        self.buildReelfxPresetPb.clicked.connect(self.setLayerEffects)
        self.buildCreateButtonPb.clicked.connect(self.createLayers)
        self.menuSetting()

    def setLayerEffects(self):
        itemIndex = self.buildReelfxPresetCb.currentIndex()

        # Perform the desired action based on the selected item
        faceRegion = assignWeights.FaceRegionWeights()
        if itemIndex is 0:
            faceRegion.setBrow()
        elif itemIndex is 1:
            faceRegion.setBrowTwist()
        elif itemIndex is 2:
            faceRegion.setEyelid()
        elif itemIndex is 3:
            faceRegion.setSocket()
        elif itemIndex is 4:
            faceRegion.setSquint()
        elif itemIndex is 5:
            faceRegion.setLip()
        elif itemIndex is 6:
            faceRegion.setLipScale()


class MirrorTab(tabWidget.MirrorTabBase):

    def __init__(self, version, mll, control=None, mLayout=None):
        """Initirize for utils tab

        :param mLayout:
        """
        super(MirrorTab, self).__init__(version, mll, control, mLayout)

        self.leGroup = QtWidgets.QGroupBox(self.tabWidget)
        self.leVLayout = QtWidgets.QVBoxLayout(self.leGroup)

        self.leCbHLayout = QtWidgets.QHBoxLayout()
        self.leLabel = QtWidgets.QLabel(self.leGroup)
        self.leRadioGroup1 = QtWidgets.QButtonGroup()
        self.leCb1RadioBtn = QtWidgets.QRadioButton()
        self.leCb2RadioBtn = QtWidgets.QRadioButton()

        self.leTypeHLayout = QtWidgets.QHBoxLayout()
        self.leTypeLabel = QtWidgets.QLabel(self.leGroup)
        self.leCb = QtWidgets.QComboBox(self.leGroup)

        self.leSelectHLayout = QtWidgets.QHBoxLayout()
        self.leSelectLabel = QtWidgets.QLabel(self.leGroup)
        self.leRadioGroup2 = QtWidgets.QButtonGroup()
        self.leSelectCb1RadioBtn = QtWidgets.QRadioButton()
        self.leSelectCb2RadioBtn = QtWidgets.QRadioButton()

        self.leHLayout = QtWidgets.QHBoxLayout()
        self.leBtn = QtWidgets.QPushButton(self.leGroup)
        self.selectionMenu = QtWidgets.QMenu(self.leBtn)
        self.currentAction = QtWidgets.QAction("Current Layer", self.selectionMenu)
        self.allAction = QtWidgets.QAction("All Layers", self.selectionMenu)

        self.mirrorGroup = QtWidgets.QGroupBox(self.tabWidget)
        self.mirrorGroupVLayout = QtWidgets.QVBoxLayout(self.mirrorGroup)
        self.mirrorContentsVLayout = QtWidgets.QVBoxLayout()
        self.mirrorOptionHLayout = QtWidgets.QHBoxLayout()
        self.mirrorOptionLabel = QtWidgets.QLabel(self.mirrorGroup)
        self.mirrorOption1RadioBtn = QtWidgets.QRadioButton()
        self.mirrorOption2RadioBtn = QtWidgets.QRadioButton()
        self.mirrorBtnHLayout = QtWidgets.QHBoxLayout()
        self.mirrorBtn = QtWidgets.QPushButton(self.mirrorGroup)
        self.addTagBtn = QtWidgets.QPushButton(self.mirrorGroup)

        self.createWidgets()
        self.layout()
        self.setSignals()

    def createWidgets(self):
        """Construct all widgets in utils tab
        """
        self.mirrorLayerEffectsWidget()
        self.mirrorWidget()

    def mirrorLayerEffectsWidget(self):
        """Construct the mirror widgets
        """
        self.leGroup.setTitle("Mirror Layer Effects")
        self.leGroup.setObjectName("mirrorGroup")
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(True)
        self.leGroup.setFont(font)

        self.leVLayout.setSpacing(4)
        self.leVLayout.setContentsMargins(40, 20, 40, 20)
        self.leVLayout.setObjectName("mirrorGroupVLayout")

        self.leCbHLayout.setSpacing(5)
        self.leSelectHLayout.setSpacing(5)
        self.leTypeHLayout.setSpacing(5)

        self.leCbHLayout.setContentsMargins(60, 0, 30, 0)
        self.leSelectHLayout.setContentsMargins(16, 0, 24, 0)
        self.leHLayout.setContentsMargins(42, 20, 50, 0)

        self.leLabel.setText("Status:")
        self.leSelectLabel.setText("Selection layer:")
        self.leTypeLabel.setText("Layer effects type:")

        self.leRadioGroup1.addButton(self.leCb1RadioBtn)
        self.leRadioGroup1.addButton(self.leCb2RadioBtn)
        self.leCb1RadioBtn.setObjectName("leCb1RadioBtn")
        self.leCb1RadioBtn.setText("Enable")
        self.leCb1RadioBtn.setChecked(True)
        self.leCb2RadioBtn.setObjectName("leCb2RadioBtn")
        self.leCb2RadioBtn.setText("Disable")

        self.leRadioGroup2.addButton(self.leSelectCb1RadioBtn)
        self.leRadioGroup2.addButton(self.leSelectCb2RadioBtn)
        self.leSelectCb1RadioBtn.setText("Selected")
        self.leSelectCb2RadioBtn.setText("All Layer")
        self.leSelectCb2RadioBtn.setChecked(True)

        self.leCb.setMinimumSize(QtCore.QSize(30, 25))
        self.leCb.setObjectName("leCb")
        self.leCb.addItem("All")
        self.leCb.addItem("Weights")
        self.leCb.addItem("Layer Mask")
        self.leCb.addItem("DQ Weights")

        self.leBtn.setObjectName("layerEffectBtn")
        self.leBtn.setText("Set Layer Effects")
        self.leBtn.setToolTip("Sets the effects status of a specified layer")
        self.leBtn.setMinimumSize(QtCore.QSize(180, 25))
        self.leBtn.setStyleSheet(
            "QPushButton { background-color: #5D5D5D; border-radius: 4px;}"
            "QPushButton:pressed { background-color: #00A6F3;}"
            "QPushButton:hover:!pressed { background-color: #707070;}")

    def mirrorWidget(self):
        """Construct the mirror widgets
        """
        self.mirrorGroup.setTitle("Mirror Influences in All Layers")
        self.mirrorGroup.setObjectName("mirrorGroup")
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(True)
        self.mirrorGroup.setFont(font)

        self.mirrorGroupVLayout.setSpacing(0)
        self.mirrorGroupVLayout.setContentsMargins(0, 10, 0, 20)
        self.mirrorGroupVLayout.setObjectName("mirrorGroupVLayout")

        self.mirrorContentsVLayout.setSpacing(0)
        self.mirrorContentsVLayout.setContentsMargins(0, 10, 0, 10)
        self.mirrorContentsVLayout.setObjectName("mirrorContentsVLayout")

        bookmarkIcon = QIcon()
        bookmarkIcon.addPixmap(QtGui.QPixmap(common.getIconPath("bookmark.png")), QIcon.Normal, QIcon.Off)
        self.addTagBtn.setObjectName("addTagBtn")
        self.addTagBtn.setIcon(bookmarkIcon)
        self.addTagBtn.setToolTip("Add a tag name to ignore mirroring on the selected layer")
        self.addTagBtn.setMinimumSize(QtCore.QSize(23, 25))
        self.addTagBtn.setStyleSheet(
            "QPushButton { background-color: #5D5D5D; border-radius: 4px;}"
            "QPushButton:pressed { background-color: #00A6F3;}"
            "QPushButton:hover:!pressed { background-color: #707070;}")

        self.mirrorOptionHLayout.setSpacing(5)
        self.mirrorOptionHLayout.setContentsMargins(60, 0, 20, 0)
        self.mirrorOptionHLayout.setObjectName("mirrorOptionHLayout")

        self.mirrorOptionLabel.setText("Selection Type:")

        self.mirrorOption1RadioBtn.setObjectName("mirrorOption1RadioBtn")
        self.mirrorOption1RadioBtn.setText("Selected")
        self.mirrorOption1RadioBtn.setChecked(True)

        self.mirrorOption2RadioBtn.setObjectName("mirrorOption2RadioBtn")
        self.mirrorOption2RadioBtn.setText("Scene")

        self.mirrorBtnHLayout.setSpacing(0)
        self.mirrorBtnHLayout.setObjectName("mirrorBtnHLayout")

        self.mirrorBtn.setObjectName("mirrorBtn")
        self.mirrorBtn.setText("Mirror")
        self.mirrorBtn.setToolTip("Mirror all influences on all layers at once")
        self.mirrorBtn.setMinimumSize(QtCore.QSize(160, 25))
        self.mirrorBtn.setStyleSheet(
            "QPushButton { background-color: #5D5D5D; border-radius: 4px;}"
            "QPushButton:pressed { background-color: #00A6F3;}"
            "QPushButton:hover:!pressed { background-color: #707070;}")

    def setLayerEffects(self):
        status = None, None
        if self.leCb1RadioBtn.isChecked():
            status = True, "Enabled"
        elif self.leCb2RadioBtn.isChecked():
            status = False, "Disabled"

        selectType = None
        if self.leSelectCb1RadioBtn.isChecked():
            selectType = "current"
        elif self.leSelectCb2RadioBtn.isChecked():
            selectType = "all"

        # Perform the desired action based on the selected item
        num = 0
        itemIndex = self.leCb.currentIndex()

        mirrorEffects = mirrorHelper.MirrorLayerEffects(selectType, self.mLayout)
        if itemIndex == 0:
            num = mirrorEffects.setLayerEffects(status[0], everything=True)
        elif itemIndex == 1:
            num = mirrorEffects.setLayerEffects(status[0], weight=True)
        elif itemIndex == 2:
            num = mirrorEffects.setLayerEffects(status[0], mask=True)
        elif itemIndex == 3:
            num = mirrorEffects.setLayerEffects(status[0], dq=True)

        if num > 1:
            message = "{} the layer effects for each of the {} layers"
        else:
            message = "{} the layer effects for the {} layer"

        self.mLayout.displayBar.successScreen(message.format(status[1], num))

        self.timer.singleShot(3000, self.changeInfoInitScreen)

    def mirror(self):
        """Call mirror function once pushing button
        """
        meshes = None
        # selection mode
        if self.mirrorOption1RadioBtn.isChecked():
            meshes = utils.getNgSkinnedMesh(mode=1)
        # all skinned-meshes mode
        elif self.mirrorOption2RadioBtn.isChecked():
            meshes = utils.getNgSkinnedMesh(mode=2)

        if not meshes:
            message = "Please select any ng-skinned mesh"
            self.mLayout.displayBar.errorScreen(message)
            self.timer.singleShot(2000, self.changeInfoInitScreen)
            return

        # mirror function
        for mesh in meshes:
            # the mesh needs to be selected for the mirror process
            if self.mirrorOption2RadioBtn.isChecked():
                cmds.select(cl=True)
                cmds.select(mesh)

            self.control.mirror(mesh, self.control.getNumberOfLayers(meshes))

        self.timer.singleShot(3000, self.changeInfoInitScreen)

        self.mLayout.displayBar.successMirror(meshes)

    def addTagName(self):
        """Call addTagName function once pushing button
        """
        mesh = utils.getNgSkinnedMesh(mode=1)[0]
        self.control.addTagName(mesh)

    def setSignals(self):
        """Set each of signals
        """
        self.leBtn.clicked.connect(self.setLayerEffects)
        self.addTagBtn.clicked.connect(self.addTagName)
        self.mirrorBtn.clicked.connect(self.mirror)

    def animation(self):
        # set an easing curve for animation
        easingCurve = QtCore.QEasingCurve(QtCore.QEasingCurve.InCubic)

        self.anim.setDuration(3000)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.setEasingCurve(easingCurve)
        self.anim.start()

    def layout(self):
        self.leCbHLayout.addWidget(self.leLabel)
        self.leCbHLayout.addWidget(self.leCb1RadioBtn)
        self.leCbHLayout.addWidget(self.leCb2RadioBtn)
        self.leCbHLayout.addStretch()

        self.leSelectHLayout.addWidget(self.leSelectLabel)
        self.leSelectHLayout.addWidget(self.leSelectCb1RadioBtn)
        self.leSelectHLayout.addWidget(self.leSelectCb2RadioBtn)
        self.leSelectHLayout.addStretch()

        self.leTypeHLayout.addWidget(self.leTypeLabel)
        self.leTypeHLayout.addWidget(self.leCb)
        self.leTypeHLayout.addStretch()

        self.leHLayout.addStretch()
        self.leHLayout.addWidget(self.leBtn)
        self.leHLayout.addStretch()

        self.leVLayout.addLayout(self.leCbHLayout)
        self.leVLayout.addLayout(self.leSelectHLayout)
        self.leVLayout.addLayout(self.leTypeHLayout)
        self.leVLayout.addLayout(self.leHLayout)

        self.mirrorOptionHLayout.addWidget(self.mirrorOptionLabel)
        self.mirrorOptionHLayout.addWidget(self.mirrorOption1RadioBtn)
        self.mirrorOptionHLayout.addWidget(self.mirrorOption2RadioBtn)
        self.mirrorOptionHLayout.addStretch()

        self.mirrorBtnHLayout.addStretch(30)
        self.mirrorBtnHLayout.addWidget(self.mirrorBtn)
        self.mirrorBtnHLayout.addSpacing(2)
        self.mirrorBtnHLayout.addWidget(self.addTagBtn)
        self.mirrorBtnHLayout.addStretch(30)

        self.mirrorContentsVLayout.addLayout(self.mirrorOptionHLayout)
        self.mirrorGroupVLayout.addLayout(self.mirrorContentsVLayout)
        self.mirrorGroupVLayout.addLayout(self.mirrorBtnHLayout)

        self.mirrorMainVLayout.addWidget(self.leGroup)
        self.mirrorMainVLayout.addWidget(self.mirrorGroup)
        self.mirrorMainVLayout.addStretch()

        self.tabWidget.setLayout(self.mirrorMainVLayout)


class UtilsTab(tabWidget.UtilTabBase):

    def __init__(self, version, mll, control=None, mLayout=None):
        """Initirize for utils tab

        :param mLayout:
        """
        super(UtilsTab, self).__init__(version, mll, control, mLayout)

        self.weightList = None

        self.clipboardGroup = QtWidgets.QGroupBox(self.tabWidget)
        self.clipboardVLayout = QtWidgets.QVBoxLayout(self.clipboardGroup)

        self.cbBtnHLayout = QtWidgets.QHBoxLayout(self.clipboardGroup)
        self.cbBtn = QtWidgets.QPushButton(self.clipboardGroup)
        self.cbMenu = QtWidgets.QMenu(self.cbBtn)

        self.createWidgets()
        self.layout()
        self.setSignals()

        # make animation object
        self.anim = QtCore.QPropertyAnimation(self.convertLayerDataGroup, b"opacity")

    def createWidgets(self):
        """Construct all widgets in utils tab
        """
        self.clipboardWidget()
        self.convertWidget()

    def clipboardWidget(self):
        self.clipboardGroup.setTitle("Weight Clipboard")
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(True)
        self.clipboardGroup.setFont(font)

        self.clipboardVLayout.setSpacing(0)
        self.clipboardVLayout.setContentsMargins(0, 10, 0, 20)
        self.clipboardVLayout.setObjectName("clipboardVLayout")

        self.cbBtnHLayout.setContentsMargins(95, 10, 95, 10)
        self.cbBtnHLayout.setObjectName("cbBtnHLayout")

        self.cbBtn.setObjectName("cbBtn")
        self.cbBtn.setText("Weight Clipboard")
        self.cbBtn.setToolTip("Copy paste operation")
        self.cbBtn.setMenu(self.cbMenu)
        self.cbBtn.setMinimumSize(QtCore.QSize(160, 25))
        self.cbBtn.setStyleSheet(
            "QPushButton { background-color: #5D5D5D; border-radius: 4px;}"
            "QPushButton:pressed { background-color: #00A6F3;}"
            "QPushButton:hover:!pressed { background-color: #707070;}")

        cutAction = QtWidgets.QAction("Cut weights to clipboard", self.cbMenu)
        cutAction.triggered.connect(lambda: self.clipboardAction("cut"))
        self.cbMenu.addAction(cutAction)
        copyAction = QtWidgets.QAction("Copy weights to clipboard", self.cbMenu)
        copyAction.triggered.connect(lambda: self.clipboardAction("copy"))
        self.cbMenu.addAction(copyAction)
        paste1Action = QtWidgets.QAction("Paste weights (replace existing)", self.cbMenu)
        paste1Action.triggered.connect(lambda: self.clipboardAction("pasteReplace", mode=1))
        self.cbMenu.addAction(paste1Action)
        paste2Action = QtWidgets.QAction("Paste weights (addd to existing)", self.cbMenu)
        paste2Action.triggered.connect(lambda: self.clipboardAction("pasteAdd", mode=1))
        self.cbMenu.addAction(paste2Action)
        paste3Action = QtWidgets.QAction("Paste weights (subtract from existing)", self.cbMenu)
        paste3Action.triggered.connect(lambda: self.clipboardAction("pasteSubtract", mode=1))
        self.cbMenu.addAction(paste3Action)

    def clipboardAction(self, operation, mode=0):
        clip = clipboardWeights.ClipboardOperation()
        if mode == 0:
            if operation is "copy":
                clip.copyWeights(operation)
            elif operation is "cut":
                clip.copyWeights(operation)
            self.weightList = clip.weightClip

        elif mode == 1:
            if operation is clip.REPLACE:
                clip.pasteWeights(clip.REPLACE, self.weightList)
            elif operation is clip.ADD:
                clip.pasteWeights(clip.ADD, self.weightList)
            elif operation is clip.SUBTRACT:
                clip.pasteWeights(clip.SUBTRACT, self.weightList)

    def setSignals(self):
        """Set each of signals
        """
        self.convertBtn.clicked.connect(self.convert)

    def animation(self):
        # set an easing curve for animation
        easingCurve = QtCore.QEasingCurve(QtCore.QEasingCurve.InCubic)

        self.anim.setDuration(3000)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.setEasingCurve(easingCurve)
        self.anim.start()

    def layout(self):
        self.convertLaunchCBHLayout.addStretch()
        self.convertLaunchCBHLayout.addWidget(self.convertLaunchCB)
        self.convertLaunchCBHLayout.addStretch()
        self.convertSeparatorLine1HLayout.addWidget(self.convertSeparatorLine1)

        self.convertBtnHLayout.addStretch(20)
        self.convertBtnHLayout.addWidget(self.convertBtn)
        self.convertBtnHLayout.addStretch(20)

        self.convertOptionHLayout.addStretch()
        self.convertOptionHLayout.addWidget(self.convertOption1RadioBtn)
        self.convertOptionHLayout.addWidget(self.convertOption2RadioBtn)
        self.convertOptionHLayout.addStretch()

        # self.convertGroupVLayout.addLayout(self.convertLabelHLayout)
        self.convertGroupVLayout.addLayout(self.convertLaunchCBHLayout)
        self.convertGroupVLayout.addLayout(self.convertSeparatorLine1HLayout)
        self.convertGroupVLayout.addSpacing(5)
        self.convertGroupVLayout.addLayout(self.convertOptionHLayout)
        self.convertGroupVLayout.addLayout(self.convertBtnHLayout)

        self.cbBtnHLayout.addStretch()
        self.cbBtnHLayout.addWidget(self.cbBtn)
        self.cbBtnHLayout.addStretch()
        self.clipboardVLayout.addLayout(self.cbBtnHLayout)

        self.utilMainVLayout.addWidget(self.convertLayerDataGroup)
        self.utilMainVLayout.addWidget(self.clipboardGroup)
        self.utilMainVLayout.addStretch()

        self.tabWidget.setLayout(self.utilMainVLayout)


def main(tabIndex=0):
    mayaWindow = OpenMayaUI.MQtUtil.mainWindow()
    mayaWrapper = pyqt_util.wrapinstance(mayaWindow)
    view = MainWindow(tabIndex, parent=mayaWrapper)
    view.showUI()
