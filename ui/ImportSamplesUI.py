# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ImportSamplesUI.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(481, 199)
        Dialog.setMinimumSize(QtCore.QSize(481, 199))
        Dialog.setMaximumSize(QtCore.QSize(481, 199))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("settings/icon/ImgClass_Post_Clump.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog.setWindowIcon(icon)
        self.gridLayout_3 = QtWidgets.QGridLayout(Dialog)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.verticalLayoutMain = QtWidgets.QVBoxLayout()
        self.verticalLayoutMain.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.verticalLayoutMain.setObjectName("verticalLayoutMain")
        self.horizontalLayout_saveImage = QtWidgets.QHBoxLayout()
        self.horizontalLayout_saveImage.setObjectName("horizontalLayout_saveImage")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_saveImage.addWidget(self.label_2)
        self.lineEdit_SamplesPath = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_SamplesPath.setMinimumSize(QtCore.QSize(300, 20))
        self.lineEdit_SamplesPath.setMaximumSize(QtCore.QSize(308, 20))
        self.lineEdit_SamplesPath.setObjectName("lineEdit_SamplesPath")
        self.horizontalLayout_saveImage.addWidget(self.lineEdit_SamplesPath)
        self.pushButton_Browser = QtWidgets.QPushButton(Dialog)
        self.pushButton_Browser.setObjectName("pushButton_Browser")
        self.horizontalLayout_saveImage.addWidget(self.pushButton_Browser)
        self.verticalLayoutMain.addLayout(self.horizontalLayout_saveImage)
        self.groupBox_setParas = QtWidgets.QGroupBox(Dialog)
        self.groupBox_setParas.setObjectName("groupBox_setParas")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox_setParas)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_3 = QtWidgets.QLabel(self.groupBox_setParas)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.gridLayout_2.addWidget(self.label_3, 0, 2, 1, 1)
        self.lineEdit_labelAcc = QtWidgets.QLineEdit(self.groupBox_setParas)
        self.lineEdit_labelAcc.setObjectName("lineEdit_labelAcc")
        self.gridLayout_2.addWidget(self.lineEdit_labelAcc, 1, 1, 1, 1)
        self.lineEdit_labelRecall = QtWidgets.QLineEdit(self.groupBox_setParas)
        self.lineEdit_labelRecall.setObjectName("lineEdit_labelRecall")
        self.gridLayout_2.addWidget(self.lineEdit_labelRecall, 1, 3, 1, 1)
        self.lineEdit_labelIOU = QtWidgets.QLineEdit(self.groupBox_setParas)
        self.lineEdit_labelIOU.setObjectName("lineEdit_labelIOU")
        self.gridLayout_2.addWidget(self.lineEdit_labelIOU, 1, 5, 1, 1)
        self.label_9 = QtWidgets.QLabel(self.groupBox_setParas)
        self.label_9.setObjectName("label_9")
        self.gridLayout_2.addWidget(self.label_9, 2, 4, 1, 1)
        self.label_7 = QtWidgets.QLabel(self.groupBox_setParas)
        self.label_7.setAlignment(QtCore.Qt.AlignCenter)
        self.label_7.setObjectName("label_7")
        self.gridLayout_2.addWidget(self.label_7, 1, 4, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.groupBox_setParas)
        self.label_5.setAlignment(QtCore.Qt.AlignCenter)
        self.label_5.setObjectName("label_5")
        self.gridLayout_2.addWidget(self.label_5, 1, 2, 1, 1)
        self.label = QtWidgets.QLabel(self.groupBox_setParas)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 0, 4, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.groupBox_setParas)
        self.label_6.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_6.setAlignment(QtCore.Qt.AlignCenter)
        self.label_6.setObjectName("label_6")
        self.gridLayout_2.addWidget(self.label_6, 0, 0, 1, 1)
        self.lineEdit_labelValNums = QtWidgets.QLineEdit(self.groupBox_setParas)
        self.lineEdit_labelValNums.setObjectName("lineEdit_labelValNums")
        self.gridLayout_2.addWidget(self.lineEdit_labelValNums, 2, 5, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.groupBox_setParas)
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName("label_4")
        self.gridLayout_2.addWidget(self.label_4, 1, 0, 1, 1)
        self.lineEdit_labelName = QtWidgets.QLineEdit(self.groupBox_setParas)
        self.lineEdit_labelName.setObjectName("lineEdit_labelName")
        self.gridLayout_2.addWidget(self.lineEdit_labelName, 2, 3, 1, 1)
        self.label_8 = QtWidgets.QLabel(self.groupBox_setParas)
        self.label_8.setObjectName("label_8")
        self.gridLayout_2.addWidget(self.label_8, 2, 2, 1, 1)
        self.label_10 = QtWidgets.QLabel(self.groupBox_setParas)
        self.label_10.setObjectName("label_10")
        self.gridLayout_2.addWidget(self.label_10, 2, 0, 1, 1)
        self.comboBox_labelType = QtWidgets.QComboBox(self.groupBox_setParas)
        self.comboBox_labelType.setObjectName("comboBox_labelType")
        self.gridLayout_2.addWidget(self.comboBox_labelType, 0, 1, 1, 1)
        self.comboBox_labelSize = QtWidgets.QComboBox(self.groupBox_setParas)
        self.comboBox_labelSize.setObjectName("comboBox_labelSize")
        self.gridLayout_2.addWidget(self.comboBox_labelSize, 0, 3, 1, 1)
        self.comboBox_labelGSD = QtWidgets.QComboBox(self.groupBox_setParas)
        self.comboBox_labelGSD.setObjectName("comboBox_labelGSD")
        self.gridLayout_2.addWidget(self.comboBox_labelGSD, 0, 5, 1, 1)
        self.comboBox_class = QtWidgets.QComboBox(self.groupBox_setParas)
        self.comboBox_class.setObjectName("comboBox_class")
        self.gridLayout_2.addWidget(self.comboBox_class, 2, 1, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout_2)
        self.verticalLayoutMain.addWidget(self.groupBox_setParas)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.pushButton_import = QtWidgets.QPushButton(Dialog)
        self.pushButton_import.setObjectName("pushButton_import")
        self.verticalLayout.addWidget(self.pushButton_import, 0, QtCore.Qt.AlignHCenter)
        self.verticalLayoutMain.addLayout(self.verticalLayout)
        self.gridLayout_3.addLayout(self.verticalLayoutMain, 0, 0, 1, 1)

        self.retranslateUi(Dialog)
        self.pushButton_import.clicked.connect(Dialog.accept) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "导入样本库"))
        self.label_2.setText(_translate("Dialog", "样本库路径："))
        self.pushButton_Browser.setText(_translate("Dialog", "浏览..."))
        self.groupBox_setParas.setTitle(_translate("Dialog", "样本库信息："))
        self.label_3.setText(_translate("Dialog", "尺寸："))
        self.label_9.setText(_translate("Dialog", "验证集："))
        self.label_7.setText(_translate("Dialog", "IOU："))
        self.label_5.setText(_translate("Dialog", "Recall："))
        self.label.setText(_translate("Dialog", "分辨率："))
        self.label_6.setText(_translate("Dialog", "类别："))
        self.label_4.setText(_translate("Dialog", "Acc："))
        self.label_8.setText(_translate("Dialog", "名称："))
        self.label_10.setText(_translate("Dialog", "类型："))
        self.pushButton_import.setText(_translate("Dialog", "确定"))
