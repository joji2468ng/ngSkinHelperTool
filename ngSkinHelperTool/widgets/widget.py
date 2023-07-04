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
import pickle
import webbrowser

# Third party
from maya import cmds
from pymel.util.path import path as PmPath
from PySide2 import QtCore, QtWidgets
from PySide2.QtWidgets import QDialog

# Local modules
from rig_tools.tool.ngSkinHelperTool.widgets import messageBox
from rig_tools.tool.ngSkinHelperTool.util import utils
from rig_tools.tool.ngSkinHelperTool.tabInternal import layerManagerBase

# ----------------------------------------------------------------- GLOBALS --#


class MainWidget(QDialog):
    DARK_GREY = 202020
    WINDOW_NAME = "ngSkinHelperTool"
    PREF_NAME = "ngSkinHelperTool_prefs"
    WEB_BROWSER_PATH = "https://confluence.reelfx.com/display/RIG/ngSkinHelperTool"

    def __init__(self, parent=None):
        super(MainWidget, self).__init__(parent=parent)

        self.parent = parent

        self.displayBar = messageBox.DisplayFactory()
        self.displayBar.infoInitialState()
        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.mainTabWidget = QtWidgets.QTabWidget(self)

        self.widthSize = 420
        self.heightSize = 580

    def _deleteInstances(self):
        """Delete the window if it is already opened
        """
        currentClass = "{}WorkspaceControl".format(self.__class__.WINDOW_NAME)
        if cmds.window(currentClass, exists=1):
            cmds.deleteUI(currentClass)
        if cmds.window(self.__class__.WINDOW_NAME, exists=1):
            cmds.deleteUI(self.__class__.WINDOW_NAME)

    def _baseLayout(self):
        """Generates a base layout on the main window
        """
        self.mainLayout.setObjectName("mainLayout")
        self.mainLayout.setSpacing(0)
        self.mainLayout.setContentsMargins(-1, 0, -1, 10)
        self.setLayout(self.mainLayout)

    def _infoTopWidget(self):
        """Generates the information bar on top of the window
        """
        self.progressBar = QtWidgets.QProgressBar()
        self.progressBar.setVisible(False)
        self.progressBar.setMinimumHeight(10)
        self.progressBar.setInvertedAppearance(False)
        self.progressBar.setObjectName("progressBar")

    def _mainTabWidget(self):
        """Generatea main content tabs
        """
        self.mainTabWidget.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.mainTabWidget.setUsesScrollButtons(False)
        self.mainTabWidget.setDocumentMode(False)
        self.mainTabWidget.setMovable(False)
        self.mainTabWidget.setObjectName("mainTabWidget")

    def createWidgets(self):
        """Generates each of widgets needed for the main window
        """
        self._baseLayout()
        self._infoTopWidget()
        self._mainTabWidget()

    def setWindowFlagPreference(self):
        windowFlags = QtCore.Qt.WindowFlags()

        if cmds.about(ntOS=True):
            windowFlags ^= QtCore.Qt.WindowContextHelpButtonHint
        elif cmds.about(macOS=True):
            pass

        windowFlags |= QtCore.Qt.Window
        self.setWindowFlags(windowFlags)

    def getPrefPath(self, name):
        """Construct a preference files path with the specified name.

        :param
            name: strings
                the file name
        :return: the path of a preference file
        """
        path = PmPath('~/.prefs/').expanduser()
        return path.joinpath('{0}.dat'.format(name))

    def getDefaultConfig(self):
        """Get the default configuration dictionary for this window.
        """
        pos = self.getCenterWindow()
        data = layerManagerBase.LayerPresetData()

        config = dict(width=self.widthSize,
                      height=self.heightSize,
                      x=pos.x(),
                      y=pos.y(),
                      layerPreset=data.load(filePath=data.filePath))
        return config

    def getWindowState(self):
        """Get a current window status

        :return: dict
        """
        return dict(x=self.x(), y=self.y(), width=self.width(), height=self.height())

    def renameTitle(self, title, verName=None):
        """Swap out the window title with the current version's name

        :param
            verName: str
                the version name of either ngSkinTools1 or ngSkinTools2

        :return: str
            the tool name + version name
        """
        title = "{}{}".format(title, " " * 3)
        if verName is None:
            return title

        return "{}- [{}]".format(title, verName)


class MainLayout(MainWidget):

    def __init__(self, title, parent=None):
        MainWidget.__init__(self, parent=parent)

        self.title = title
        self.parent = parent
        self.logger = logging.getLogger(__name__)

        self._deleteInstances()
        self.setObjectName(self.WINDOW_NAME)
        self.setWindowFlagPreference()
        self.setMinimumSize(QtCore.QSize(self.widthSize, self.heightSize))

        self.prefPath = self.getPrefPath(self.PREF_NAME)

    def setSize(self, w=None, h=None):
        """Sets size of the main window during applying the configuration

        :parameter:
            w : int
                Size of width for the main window
            h : int
                Size of hight for the main window
        """
        if w is None:
            w = self.width()
        if h is None:
            h = self.height()
        self.resize(w, h)

    def setPosition(self, x=None, y=None):
        """Sets position of the main window during applying the configuration

        :parameter:
            x : int
                Position where places the main window along X axis
            y : int
                Position where places the main window along Y axis
        """
        if x is None:
            x = self.x()
        if y is None:
            y = self.y()
        self.move(x, y)

    def bringToFront(self):
        """Raises the window above other windows,
        """
        self.raise_()
        self.activateWindow()
        self.showNormal()
        self.setFocus()

    def layout(self):
        """Makes the main layout including all widgets
        """
        self.displayBar.layout()
        self.mainLayout.addWidget(self.displayBar.iconFrame)
        self.mainLayout.addLayout(self.displayBar.infoFrameHBoxLayout)
        self.mainLayout.addWidget(self.progressBar)
        self.mainLayout.addWidget(self.mainTabWidget)

    def getScreenCenter(self, screenNumber=None):
        """Gets the center position of the specified screen snumber.

        :parameters:
            screenNumber : int
                Display to get center of (defaults to primary screen).

        :rtype: QPoint
        """
        app = QtWidgets.QApplication.instance()
        desktop = app.desktop()
        if screenNumber is None:
            screenNumber = desktop.primaryScreen()
        screen_geo = desktop.availableGeometry(screenNumber)
        center_x = screen_geo.x() + int(screen_geo.width() // 2)
        center_y = screen_geo.y() + int(screen_geo.height() // 2)
        return QtCore.QPoint(center_x, center_y)

    def getCenterWindow(self, screenNumber=None):
        """Get a center window position
        :param
            screenNumber: int
                Display to get center of (defaults to primary screen).
        :return:
        """
        centerPoint = self.getScreenCenter(screenNumber)
        halfSize = QtCore.QPoint(self.width() // 2, self.height() // 2)
        position = centerPoint - halfSize
        return position

    def loadPreferences(self, defaultData=None):
        """Load the default configuratoin from the path constructed

        :param
            defaultData: dict
                if None, gets the pre-user-defined config

        :return: dict
            data of configuration
        """
        if not defaultData:
            defaultData = self.getDefaultConfig()

        if not self.prefPath.exists():
            log.error('Preference file was empty. Contents may have been reset: '
                      '{}\n Using default preference data.'.format(prefPath))
            return defaultData

        with open(self.prefPath, 'r') as fd:
            prefData = pickle.load(fd)

        if not prefData:
            return defaultData

        layerPreset = prefData["layerPreset"]
        if layerPreset is None:
            prefData["layerPreset"] = defaultData["layerPreset"]

        return prefData

    def savePreferences(self, prefData=None):
        """Save a preference file

        :param
            prefData: dict
                data of preference
        :return: path of preference
        """
        with open(self.prefPath, 'w') as fd:
            pickle.dump(prefData, fd)

        return self.prefPath

    def selectionChangedCallback(self):
        """Call the selection changed callback
        """
        mesh = utils.getNgSkinnedMesh(mode=1)

        if not mesh:
            self.setWindowTitle(self.title)
            return

        verName = utils.getToolVersion(mesh[0])
        tittle = self.renameTitle(self.title, verName)
        self.setWindowTitle(tittle)

    def matchResultChangedCallback(self):
        """Call match result changed callback
        """
        num = self.control.getNumberMatchedJoint()
        self.sr_result_label.setTittle("{} matches".format(num))

    def initSelectionChangedCallback(self):
        """Make a scriptJob with a selection changed event

        :return:
        """
        # Just in case.
        utils.killScriptJob(self.selectionChangedCallback)

        # Make new scriptJobs.
        cmds.scriptJob(
            event=("SelectionChanged", self.selectionChangedCallback),
            killWithScene=False
        )

    def openHelpPage(self):
        """Open a confluence page for the tool
        """
        webbrowser.open(self.WEB_BROWSER_PATH)

    def switchInfoBar(self, tabInfo):
        """Sends the message to the information bar

        :return:
        """
        displayType = self.displayBar.currentType
        if displayType == "warning":
            return

        index = self.mainTabWidget.currentIndex()

        tabData = None
        if index == 0:
            tabData = tabInfo["CopyPaste"]
        elif index == 1:
            tabData = tabInfo["Build"]
        elif index == 2:
            tabData = tabInfo["Mirror"]
        elif index == 3:
            tabData = tabInfo["Utils"]
        self.displayBar.initScreen(tabData["msg"])

    def resetAll(self):
        """Restore settigs to their original defaults
        """
        self._copyTab.layerSet_source_lineEdit.clear()
        self._copyTab.layerSet_destination_lineEdit.clear()
        self._copyTab.setting_replace_radioButton.setChecked(True)
        self._copyTab.setting_applyMaskWeight_CB.setChecked(True)
        self._copyTab.sr_tableView.clearContents()
        self._copyTab.resetResultMatch()
        self._copyTab.changeInfoInitScreen()
        self.setWindowTitle(self.TITLE_NAME)

    def createMenuItems(self, parent):
        """Generates menu items in the main window
        :param
            parent:
                layout object
        :return:
        """
        menubar = QtWidgets.QMenuBar(parent=parent)
        resetAllAction = QtWidgets.QAction("Reset All", parent)
        resetAllAction.triggered.connect(self.resetAll)

        confluencePageAction = QtWidgets.QAction("Confluence Page", parent)
        confluencePageAction.triggered.connect(self.openHelpPage)

        menuEdit = menubar.addMenu("Edit")
        menuEdit.addAction(resetAllAction)

        menuHelp = menubar.addMenu("Help")
        menuHelp.addAction(confluencePageAction)
        return menubar

    def showUI(self):
        """Launch the window
        """
        self.bringToFront()
        self.show()
