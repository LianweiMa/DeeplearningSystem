# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'PostProcessUI.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(477, 167)
        Dialog.setMinimumSize(QtCore.QSize(477, 167))
        Dialog.setMaximumSize(QtCore.QSize(477, 167))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("settings/icon/ImgClass_Post_Clump.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
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
        self.horizontalLayout_openImage.addWidget(self.pushButton_openImage)
        self.verticalLayoutMain.addLayout(self.horizontalLayout_openImage)
        self.horizontalLayout_saveImage = QtWidgets.QHBoxLayout()
        self.horizontalLayout_saveImage.setObjectName("horizontalLayout_saveImage")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_saveImage.addWidget(self.label_2)
        self.lineEdit_saveImage = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_saveImage.setMinimumSize(QtCore.QSize(308, 20))
        self.lineEdit_saveImage.setMaximumSize(QtCore.QSize(308, 20))
        self.lineEdit_saveImage.setObjectName("lineEdit_saveImage")
        self.horizontalLayout_saveImage.addWidget(self.lineEdit_saveImage)
        self.pushButton_saveImage = QtWidgets.QPushButton(Dialog)
        self.pushButton_saveImage.setObjectName("pushButton_saveImage")
        self.horizontalLayout_saveImage.addWidget(self.pushButton_saveImage)
        self.verticalLayoutMain.addLayout(self.horizontalLayout_saveImage)
        self.groupBox_setParas = QtWidgets.QGroupBox(Dialog)
        self.groupBox_setParas.setObjectName("groupBox_setParas")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox_setParas)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_3 = QtWidgets.QLabel(self.groupBox_setParas)
        self.label_3.setObjectName("label_3")
        self.gridLayout_2.addWidget(self.label_3, 0, 2, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(60, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem, 0, 4, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.groupBox_setParas)
        self.label_6.setObjectName("label_6")
        self.gridLayout_2.addWidget(self.label_6, 0, 0, 1, 1)
        self.lineEdit_kernel = QtWidgets.QLineEdit(self.groupBox_setParas)
        self.lineEdit_kernel.setObjectName("lineEdit_kernel")
        self.gridLayout_2.addWidget(self.lineEdit_kernel, 0, 1, 1, 1)
        self.lineEdit_labelSize = QtWidgets.QLineEdit(self.groupBox_setParas)
        self.lineEdit_labelSize.setObjectName("lineEdit_labelSize")
        self.gridLayout_2.addWidget(self.lineEdit_labelSize, 0, 3, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout_2)
        self.verticalLayoutMain.addWidget(self.groupBox_setParas)
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

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "聚类"))
        self.label.setText(_translate("Dialog", "打开影像："))
        self.pushButton_openImage.setText(_translate("Dialog", "浏览..."))
        self.label_2.setText(_translate("Dialog", "保存影像："))
        self.pushButton_saveImage.setText(_translate("Dialog", "浏览..."))
        self.groupBox_setParas.setTitle(_translate("Dialog", "参数设置："))
        self.label_3.setText(_translate("Dialog", "分块大小："))
        self.label_6.setText(_translate("Dialog", "核大小："))
        self.lineEdit_kernel.setText(_translate("Dialog", "7"))
        self.lineEdit_labelSize.setText(_translate("Dialog", "256"))
        self.pushButton_process.setText(_translate("Dialog", "开始处理"))
