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
# Third party
from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtGui import QIcon

# Local modules
from rig_tools.tool.ngSkinHelperTool.util import common


class InformationWidget(QtWidgets.QWidget):

    def __init__(self):
        """InformationWidget is a custom QWidget base class that can display various types of information to the user.
        It can be used to show text, images, or a combination of both.
        The widget can be customized with different fonts, colors, and styles to match the application's theme.

        """
        super(InformationWidget, self).__init__()

        self.alertSheet = "QLabel { color: white;}"
        self.frameHeight = 40
        self.btnHeight = 20
        self.iconSize = 16

        self.iconFrame = QtWidgets.QFrame()
        self.displayLabel = QtWidgets.QLabel(self.iconFrame)
        self.ngLabel = QtWidgets.QLabel(self.iconFrame)
        self.message = QtWidgets.QLabel(self.iconFrame)
        self.displayIcon = QtWidgets.QLabel(self.iconFrame)
        self.button = QtWidgets.QPushButton(self.iconFrame)

    def createLabel(self):
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        self.displayLabel.setObjectName("infoLabel")
        self.displayLabel.setMinimumHeight(15)
        self.displayLabel.setFont(font)
        self.displayLabel.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.displayLabel.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.displayLabel.setFrameShadow(QtWidgets.QFrame.Plain)

        font = QtGui.QFont()
        font.setPointSize(7)
        font.setBold(True)
        font.setFamily("Heiti SC")
        # font.setUnderline(True)
        # self.ngLabel.setText("ngSkinTools1")
        self.ngLabel.setObjectName("ngLabel")
        self.ngLabel.setMinimumHeight(15)
        self.ngLabel.setFont(font)
        self.ngLabel.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.ngLabel.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.ngLabel.setFrameShadow(QtWidgets.QFrame.Plain)

    def createMessage(self):
        font = QtGui.QFont()
        font.setPointSize(8)
        self.message.setObjectName("message")
        self.message.setMinimumHeight(15)
        self.message.setFont(font)
        self.message.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.message.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.message.setFrameShadow(QtWidgets.QFrame.Plain)

    def createIcon(self):
        self.displayIcon.setMinimumHeight(15)
        self.displayIcon.setMaximumSize(QtCore.QSize(self.iconSize, self.iconSize))
        self.displayIcon.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.displayIcon.setScaledContents(True)

    def createFrame(self):
        self.iconFrame.setMaximumHeight(self.frameHeight)
        self.iconFrame.setObjectName("infoFrame")

    def createButton(self, name=""):
        self.button.setMinimumHeight(15)
        self.button.setText(name)
        self.button.setVisible(False)


class DisplayBar(InformationWidget):

    def __init__(self):
        """InformationWidget is a custom QWidget sub class that can display various types of information to the user.
        It can be used to show text, images, or a combination of both.
        The widget can be customized with different fonts, colors, and styles to match the application's theme.
        """
        super(DisplayBar, self).__init__()

        self.currentType = None

        self.infoFrameHBoxLayout = QtWidgets.QHBoxLayout(self.iconFrame)
        self.infoMainVBoxLayout = QtWidgets.QVBoxLayout(self.iconFrame)
        self.infoSubHBoxLayout1 = QtWidgets.QHBoxLayout(self.iconFrame)
        self.infoSubHBoxLayout2 = QtWidgets.QHBoxLayout(self.iconFrame)

        self.expanding = QtWidgets.QSizePolicy.Expanding
        self.preferred = QtWidgets.QSizePolicy.Preferred
        self.minimum = QtWidgets.QSizePolicy.Minimum
        self.fixed = QtWidgets.QSizePolicy.Fixed

        self.createFrame()
        self.createIcon()
        self.createLabel()
        self.createMessage()
        self.createButton()

    def initScreen(self, message):
        self.currentType = "info"
        self.iconFrame.setStyleSheet("QFrame { background-color : #202020; border-radius: 2px;}")
        iconPath = QIcon(common.getIconPath("info.png"))
        iconPixmap = iconPath.pixmap(self.iconSize, self.iconSize, QIcon.Active, QIcon.On)
        self.displayIcon.setPixmap(iconPixmap)

        self.displayLabel.setText("Info:")
        self.displayLabel.setStyleSheet("QLabel { color: white;}")

        self.message.setText(message)
        self.message.setStyleSheet("QLabel { color: #999999;}")

        self.button.setVisible(False)

    def successScreen(self, message):
        self.currentType = "success"
        self.iconFrame.setStyleSheet("QFrame { background-color : #002704; border-width: 2px; border-radius: 2px;}")
        iconPath = QIcon(common.getIconPath("success.png"))
        iconPixmap = iconPath.pixmap(self.iconSize, self.iconSize, QIcon.Active, QIcon.On)
        self.displayIcon.setPixmap(iconPixmap)
        self.displayIcon.setFrameShape(QtWidgets.QFrame.NoFrame)

        self.displayLabel.setText("Success:")
        self.displayLabel.setStyleSheet("QLabel { color: white;}")
        self.displayLabel.setFrameShape(QtWidgets.QFrame.NoFrame)

        self.message.setText(message)
        self.message.setStyleSheet("QLabel { color: #6fb36f;}")
        self.message.setFrameShape(QtWidgets.QFrame.NoFrame)

    def warningScreen(self, message):
        self.currentType = "warning"
        self.iconFrame.setStyleSheet("QFrame { background-color : #FD841F; border-radius: 2px;}")
        iconPath = QIcon(common.getIconPath("alert.png"))
        iconPixmap = iconPath.pixmap(self.iconSize, self.iconSize, QIcon.Active, QIcon.On)
        self.displayIcon.setPixmap(iconPixmap)

        self.displayLabel.setText("Warning:")
        self.displayLabel.setStyleSheet(self.alertSheet)

        self.message.setText(message)
        self.message.setStyleSheet("QLabel { color: white;}")

    def errorScreen(self, message):
        self.currentType = "error"
        self.iconFrame.setStyleSheet("QFrame { background-color : #800000; border-radius: 2px;}")
        iconPath = QIcon(common.getIconPath("error.png"))
        iconPixmap = iconPath.pixmap(self.iconSize, self.iconSize, QIcon.Active, QIcon.On)
        self.displayIcon.setPixmap(iconPixmap)

        self.displayLabel.setText("Error:")
        self.displayLabel.setStyleSheet(self.alertSheet)

        self.message.setText(message)
        self.message.setStyleSheet("QLabel { color: white;}")

    def layout(self):
        hSpace1 = QtWidgets.QSpacerItem(5, 0, self.minimum, self.minimum)
        hSpace2 = QtWidgets.QSpacerItem(80, 0, self.fixed, self.minimum)
        hSpace3 = QtWidgets.QSpacerItem(40, 0, self.minimum, self.minimum)
        hSpace4 = QtWidgets.QSpacerItem(40, 0, self.minimum, self.minimum)
        hSpace5 = QtWidgets.QSpacerItem(50, 0, self.expanding, self.minimum)
        hSpace6 = QtWidgets.QSpacerItem(30, 0, self.minimum, self.minimum)
        hSpace7 = QtWidgets.QSpacerItem(30, 0, self.expanding, self.minimum)
        hSpace8 = QtWidgets.QSpacerItem(30, 0, self.expanding, self.minimum)

        self.infoFrameHBoxLayout.setContentsMargins(0, 5, 0, 5)

        self.infoMainVBoxLayout.setSpacing(4)
        self.infoMainVBoxLayout.setContentsMargins(0, 0, 0, 5)

        self.infoSubHBoxLayout1.setSpacing(0)
        self.infoSubHBoxLayout1.setContentsMargins(0, 0, 0, 0)

        self.infoSubHBoxLayout2.setSpacing(0)
        self.infoSubHBoxLayout2.setContentsMargins(0, 0, 0, 0)

        self.infoSubHBoxLayout1.addWidget(self.displayIcon)
        self.infoSubHBoxLayout1.addItem(hSpace1)
        self.infoSubHBoxLayout1.addWidget(self.displayLabel)
        self.infoSubHBoxLayout1.addItem(hSpace2)
        self.infoSubHBoxLayout1.addWidget(self.ngLabel)
        self.infoSubHBoxLayout1.addItem(hSpace8)

        self.infoFrameHBoxLayout.addItem(hSpace6)
        self.infoMainVBoxLayout.addLayout(self.infoSubHBoxLayout1)

        self.infoSubHBoxLayout2.addItem(hSpace3)
        self.infoSubHBoxLayout2.addWidget(self.message)
        self.infoSubHBoxLayout2.addItem(hSpace4)
        self.infoSubHBoxLayout2.addWidget(self.button)
        self.infoSubHBoxLayout2.addItem(hSpace5)
        self.infoMainVBoxLayout.addLayout(self.infoSubHBoxLayout2)

        self.infoFrameHBoxLayout.addLayout(self.infoMainVBoxLayout)
        self.infoMainVBoxLayout.addItem(hSpace7)


class DisplayFactory(DisplayBar):

    def __init__(self):
        super(DisplayFactory, self).__init__()

    def infoSelectedGeo(self, geo):
        messageText = "{} is set".format(geo)
        self.displayLabel.setText(messageText)
        self.displayLabel.setStyleSheet(self.black)
        self.button.setVisible(False)
        self.initScreen(messageText)

    def warningUnusedNgLayerData(self, ngLayerData):
        self.button.setText("Delete")
        self.button.setVisible(True)
        self.button.setStyleSheet(
            "QPushButton { color: white;"
                          "background-color: #b36f00;"
                          "border-style: outset;"
                          "border-width: 1px;"
                          "border-radius: 7px;"
                          "min-width: 6em;"
                          "border-color: white;}"
            "QPushButton:hover:!pressed { background-color: #e59356;}")

        messageText = "Found {} unused ngLayerData nodes!"
        self.warningScreen(messageText.format(len(ngLayerData)))

    def infoInitialState(self):
        messageText = "Select a ng-skinned-mesh, then set each layers"
        self.initScreen(messageText)
        self.button.setVisible(False)

    def successCopyPaste(self, opType):
        message = None
        token = "{} each weights from {} to {} layer"
        if opType == "replace":
            message = token.format("Replaced", "source", "destination")
        elif opType == "add":
            message = token.format("Added", "source", "destination")
        elif opType == "subtract":
            message = "Subtracted each weights from destination layer"
        elif opType == "cut":
            message = token.format("Cut", "source", "destination")
        self.successScreen(message)

    def successMirror(self, geo):
        if len(geo) > 1:
            meshStr = "meshes"
        else:
            meshStr = "mesh"

        message = "The weights of {} {} are mirrored across all layers"
        self.successScreen(message.format(len(geo), meshStr))

    def successConvert(self, version):
        if version is "ngSkinTools1":
            message = "Converted V1 into V2 in the selected mesh"
        else:
            message = "Converted V2 into V1 in the selected mesh"

        self.successScreen(message)

    def infoMirrorProcess(self):
        message = "Mirror Process starts"
        self.initScreen(message)

    def errorNoSkinCluster(self, geo):
        message = 'No attached skin cluster in {}'
        self.errorScreen(message.format(geo))

    def errorNoSkinLayer(self, geo):
        message = 'No exist skin layer in {}'
        self.errorScreen(message.format(geo))
