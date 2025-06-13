# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt
import uuid
from ui.ImportSamplesUI import Ui_Dialog


class ImportSamplesDialog(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)  # 调用setupUi方法初始化界面
        
        # 在这里添加你的逻辑代码
        from os.path import join
        from DeeplearningSystem import base_dir
        icon_Segment = join(base_dir, 'settings/icon', 'label_import1.png') 
        icon = QIcon()
        icon.addPixmap(QPixmap(icon_Segment), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)
        self.setWindowFlags(self.windowFlags() & ~(Qt.WindowContextHelpButtonHint))
        self.comboBox_labelGSD.addItems([ "meter", "submeter", "meter_submeter" ])
        self.comboBox_labelGSD.setCurrentIndex(-1)
        self.comboBox_class.addItems([ "building", "road", "mine", "water", "forest", "pv", "greenhouse", "desert" ])
        self.comboBox_class.setCurrentIndex(-1)
        self.comboBox_labelSize.addItems([ "256", "512", "1024" ])
        self.comboBox_labelSize.setCurrentIndex(-1)
        self.comboBox_labelType.addItems([ "Sat", "Uav" ])
        self.comboBox_labelType.setCurrentIndex(-1)

        self.pushButton_Browser.clicked.connect(self.open_clicked)
        self.lineEdit_SamplesPath.textChanged.connect(self.text_changed)

    def open_clicked(self,Dialog):
        from qgis.PyQt.QtWidgets import QFileDialog
        folder_selected = QFileDialog.getExistingDirectory(None, "Select Folder to Open")
        if  folder_selected:
            self.lineEdit_SamplesPath.setText(folder_selected)

    def text_changed(self,text):
        samplePath = self.lineEdit_SamplesPath.text()#E:\DeepLearning\Samples\Building\256x256\Sat\Meter\negative_411702_202001_yicheng_city\crop
        result = samplePath.rsplit('/', 6)
        index = self.comboBox_class.findText(result[1].lower())
        if index >= 0:
            self.comboBox_class.setCurrentIndex(index)
        index = self.comboBox_labelSize.findText(result[2].split('x')[0])
        if index >= 0:
            self.comboBox_labelSize.setCurrentIndex(index)
        index = self.comboBox_labelType.findText(result[3])
        if index >= 0:
            self.comboBox_labelType.setCurrentIndex(index)
        index = self.comboBox_labelGSD.findText(result[4].lower())
        if index >= 0:
            self.comboBox_labelGSD.setCurrentIndex(index)      
        self.lineEdit_labelName.setText(result[5])
        index_file = samplePath + '/average_index.csv'
        from os.path import exists,dirname
        if exists(index_file):
            with open(index_file,"r") as f:
                lines = f.readline()
                lines = f.readline()
                index = lines.split(",")
                self.lineEdit_labelAcc.setText(index[0])
                self.lineEdit_labelRecall.setText(index[1])
                self.lineEdit_labelIOU.setText(index[2])
        valset_file = dirname(samplePath)+'/split/val_set.txt'
        if exists(valset_file):
            with open(valset_file,"r") as f:
                lines = f.readline()
                self.lineEdit_labelValNums.setText(lines.strip())
