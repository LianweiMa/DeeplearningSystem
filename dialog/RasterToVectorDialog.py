# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'RasterToVector.ui'
#
# Created by: qgis.PyQt UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from qgis.PyQt import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setWindowFlags(Dialog.windowFlags() & ~(QtCore.Qt.WindowContextHelpButtonHint))# 隐藏对话框标题栏默认的问号按钮
        Dialog.setObjectName("Dialog")
        Dialog.resize(477, 114)
        Dialog.setMinimumSize(QtCore.QSize(0, 0))
        Dialog.setMaximumSize(QtCore.QSize(16777215, 16777215))
        icon = QtGui.QIcon()
        from os.path import join
        from DeeplearningSystem import base_dir
        icon_RasterToVector = join(base_dir, 'settings/icon', 'Utility_RasterToVector.png') 
        icon.addPixmap(QtGui.QPixmap(icon_RasterToVector), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog.setWindowIcon(icon)
        self.gridLayout_3 = QtWidgets.QGridLayout(Dialog)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.verticalLayoutMain = QtWidgets.QVBoxLayout()
        self.verticalLayoutMain.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.verticalLayoutMain.setObjectName("verticalLayoutMain")
        self.horizontalLayout_openImage = QtWidgets.QHBoxLayout()
        self.horizontalLayout_openImage.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.horizontalLayout_openImage.setSpacing(6)
        self.horizontalLayout_openImage.setObjectName("horizontalLayout_openImage")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setObjectName("label")
        self.horizontalLayout_openImage.addWidget(self.label, 0, QtCore.Qt.AlignLeft)
        self.comboBox_openImage = QtWidgets.QComboBox(Dialog)
        self.comboBox_openImage.setEnabled(True)
        self.comboBox_openImage.setMinimumSize(QtCore.QSize(308, 20))
        self.comboBox_openImage.setMaximumSize(QtCore.QSize(308, 20))
        self.comboBox_openImage.setEditable(True)
        self.comboBox_openImage.setObjectName("comboBox_openImage")
        self.horizontalLayout_openImage.addWidget(self.comboBox_openImage, 0, QtCore.Qt.AlignLeft)
        self.pushButton_openImage = QtWidgets.QPushButton(Dialog)
        self.pushButton_openImage.setObjectName("pushButton_openImage")
        self.pushButton_openImage.clicked.connect(self.on_openImage_clicked)####################
        self.horizontalLayout_openImage.addWidget(self.pushButton_openImage)
        self.verticalLayoutMain.addLayout(self.horizontalLayout_openImage)
        self.horizontalLayout_saveVector = QtWidgets.QHBoxLayout()
        self.horizontalLayout_saveVector.setObjectName("horizontalLayout_saveVector")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_saveVector.addWidget(self.label_2)
        self.lineEdit_saveVector = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_saveVector.setMinimumSize(QtCore.QSize(308, 20))
        self.lineEdit_saveVector.setMaximumSize(QtCore.QSize(308, 20))
        self.lineEdit_saveVector.setObjectName("lineEdit_saveVector")
        self.horizontalLayout_saveVector.addWidget(self.lineEdit_saveVector)
        self.pushButton_saveVector = QtWidgets.QPushButton(Dialog)
        self.pushButton_saveVector.setObjectName("pushButton_saveVector")
        self.pushButton_saveVector.clicked.connect(self.on_saveVector_clicked)###################
        self.horizontalLayout_saveVector.addWidget(self.pushButton_saveVector)
        self.verticalLayoutMain.addLayout(self.horizontalLayout_saveVector)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.pushButton_process = QtWidgets.QPushButton(Dialog)
        self.pushButton_process.setObjectName("pushButton_process")
        self.verticalLayout.addWidget(self.pushButton_process, 0, QtCore.Qt.AlignHCenter)
        self.verticalLayoutMain.addLayout(self.verticalLayout)
        self.gridLayout_3.addLayout(self.verticalLayoutMain, 0, 0, 1, 1)

        self.retranslateUi(Dialog)
        self.pushButton_process.clicked.connect(Dialog.accept) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(Dialog)

        self.__initial__()

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "栅格转矢量"))
        self.label.setText(_translate("Dialog", "栅格路径："))
        self.pushButton_openImage.setText(_translate("Dialog", "浏览..."))
        self.label_2.setText(_translate("Dialog", "矢量路径："))
        self.pushButton_saveVector.setText(_translate("Dialog", "浏览..."))
        self.pushButton_process.setText(_translate("Dialog", "开始处理"))

    def __initial__(self):
        from qgis.core import QgsProject, QgsRasterLayer, QgsVectorLayer
        #清空
        self.comboBox_openImage.clear()
        self.comboBox_openImage.currentIndex = -1
        for layer_name, layer in QgsProject.instance().mapLayers().items():
            if isinstance(layer, QgsRasterLayer):
                filepath = layer.dataProvider().dataSourceUri()
                self.comboBox_openImage.addItem(filepath)

    def on_openImage_clicked(self,Dialog):
        from qgis.PyQt.QtWidgets import QFileDialog
        path_to_tif,_ = QFileDialog.getOpenFileName(None, '打开', '', 'Raster Files (*.tif;*.tiff;*.img;*.dat);;All Files (*.*)')
        if  path_to_tif=="":
            return
        self.comboBox_openImage.setCurrentText(path_to_tif)

    def on_saveVector_clicked(self,Dialog):
        from qgis.PyQt.QtWidgets import QFileDialog
        path_to_tif,_ = QFileDialog.getSaveFileName(None, '保存', '', 'Vector Files (*.shp);;All Files (*.*)')
        if  path_to_tif=="":
            return
        self.lineEdit_saveVector.setText(path_to_tif)
