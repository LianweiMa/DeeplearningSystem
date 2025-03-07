
from dialog.mapToolInputAttr import Ui_Dialog
from PyQt5 import QtCore,QtWidgets
from PyQt5.QtWidgets import QMenu, QAction,QDesktopWidget,QDialog,QColorDialog,QMessageBox,QSizePolicy,QDockWidget,QLineEdit
from PyQt5.QtGui import QColor
from qgis.PyQt.QtCore import Qt
from qgis.core import QgsLayerTreeNode, QgsLayerTree, QgsMapLayerType,\
    QgsVectorLayer, QgsProject,QgsMarkerSymbol,QgsFillSymbol,QgsLineSymbol,\
    QgsFeatureRenderer,QgsSingleSymbolRenderer,QgsApplication,QgsSimpleLineSymbolLayer,\
    QgsRasterLayer,QgsTaskManager, QgsMessageLog,QgsProcessingAlgRunnerTask, QgsApplication,\
    QgsProcessingContext, QgsProcessingFeedback,QgsProject,QgsTask,Qgis,QgsColorRampShader,QgsPalettedRasterRenderer,\
    QgsRasterShader,QgsSingleBandPseudoColorRenderer,QgsFeature,QgsGeometry,QgsPointXY

PROJECT = QgsProject.instance()

class inputAttrWindowClass(QDialog,Ui_Dialog):
    def __init__(self,mapTool,feat,mainWindow):
        super(inputAttrWindowClass, self).__init__(mainWindow)
        self.setupUi(self)
        self.mapTool = mapTool
        self.feat : QgsFeature = feat
        self.mainWindow = mainWindow
        self.initUI()
        self.connectFunc()
        self.center()

    def center(self):
        # 获取屏幕的尺寸信息
        screen = QDesktopWidget().screenGeometry()
        # 获取窗口的尺寸信息
        size = self.geometry()
        # 将窗口移动到指定位置
        self.move(int((screen.width() - size.width()) / 2), int((screen.height() - size.height()) / 2))

    def closeEvent(self, e):
        self.mapTool.reset()
        e.accept()

    def addLayoutBotton(self,fieldName):
        #print(fieldName)
        #tempLayout = QtWidgets.QGridLayout()
        #tempLayout.setObjectName("tempLayout")
        row_count = self.gridLayout.rowCount()
        label = QtWidgets.QLabel(fieldName)
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)  # 右对齐，垂直居中
        #label.setObjectName(f"{fieldName}_label")
        #tempLayout.addWidget(label)
        self.gridLayout.addWidget(label,row_count,0)
        lineEdit = QtWidgets.QLineEdit()
        #lineEdit.setObjectName(f"{fieldName}_lineEdit")
        #tempLayout.addWidget(lineEdit)
        self.gridLayout.addWidget(lineEdit,row_count,1)
        #self.attrsLayout.addLayout(tempLayout)
        #spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        #self.attrsLayout.addItem(spacerItem)
        self.gridLayoutWidget_2.adjustSize()       
        # 手动调整窗口大小
        new_width = self.width()
        new_height = self.gridLayoutWidget_2.height() + 30  # 每行增加 30 像素高度
        self.resize(new_width, new_height)
        #self.adjustSize()
        self.attrLineDir[fieldName] = lineEdit

    def addFeature(self):
        for name in self.feat.fields().names():
            tempLine : QLineEdit = self.attrLineDir[name]
            if tempLine.text() != "None":
                self.feat.setAttribute(name,tempLine.text())
        if self.mapTool.wkbType == "rectangle":
            self.feat.setGeometry(self.mapTool.r)
        elif self.mapTool.wkbType == "polygon":
            self.feat.setGeometry(self.mapTool.p)
        elif self.mapTool.wkbType == "circle":
            pointsXY = [[]]
            for point in self.mapTool.points[0:-1]:
                pointsXY[0].append(QgsPointXY(point))
            self.feat.setGeometry(QgsGeometry.fromPolygonXY(pointsXY))
        self.mapTool.editLayer.addFeature(self.feat)
        # self.editLayer.updateExtents()
        self.mapTool.canvas.refresh()
        self.mapTool.reset()
        # 动态更新撤销重做
        #self.mainWindow.updateShpUndoRedoButton()
        self.close()

    def initUI(self):
        #self.setFixedSize(self.size())
        self.setWindowTitle("属性编辑")
        self.attrLineDir = {}
        for name in self.feat.fields().names():
            self.addLayoutBotton(name)

    def connectFunc(self):
        self.add.clicked.connect(self.addFeature)
        self.cancel.clicked.connect(self.close)