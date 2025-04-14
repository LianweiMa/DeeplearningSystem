# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QDesktopWidget, QDialog, QLineEdit, QLabel, QDialogButtonBox, QLayout
from PyQt5.QtGui import  QIcon, QPixmap
from PyQt5.QtCore import Qt
from qgis.core import QgsFeature,QgsGeometry,QgsPointXY
from ui.FeatureAttributeUI import Ui_Dialog


class FeatureAttributeDialog(QDialog, Ui_Dialog):
    def __init__(self, mapTool, feat, mainWindow):
        super().__init__(mainWindow)
        self.setupUi(self)  # 调用setupUi方法初始化界面
        self.mapTool = mapTool
        self.feat : QgsFeature = feat
        self.mainWindow = mainWindow
        self.initUI()
        self.connectFunc()
        self.center()
        
        # 在这里添加你的逻辑代码
        from os.path import join
        from DeeplearningSystem import base_dir
        icon_Segment = join(base_dir, 'settings/icon', 'VectorEditor_AttributeEdit.png') 
        icon = QIcon()
        icon.addPixmap(QPixmap(icon_Segment), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)
        self.setWindowFlags(self.windowFlags() & ~(Qt.WindowContextHelpButtonHint))
        # 手动设置按钮文本
        self.buttonBox.button(QDialogButtonBox.Ok).setText("确定")
        self.buttonBox.button(QDialogButtonBox.Cancel).setText("取消")

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
        lineEdit = QLineEdit()
        self.formLayout.addRow(fieldName,lineEdit)
        self.adjustSize()   
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
        #self.setWindowTitle("属性编辑")
        self.attrLineDir = {}
        for name in self.feat.fields().names():
            self.addLayoutBotton(name)

    def connectFunc(self):
        #self.add.clicked.connect(self.addFeature)
        #self.cancel.clicked.connect(self.close)
        self.buttonBox.accepted.connect(self.addFeature)
        self.buttonBox.rejected.connect(self.close)