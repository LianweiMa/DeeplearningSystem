# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt
from ui.ImportSamplesUI import Ui_Dialog


class ImportSamplesDialog(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)  # 调用setupUi方法初始化界面
        
        # 在这里添加你的逻辑代码
        from os.path import join
        from DeeplearningSystem import base_dir
        icon_Segment = join(base_dir, 'settings/icon', 'label_import.png') 
        icon = QIcon()
        icon.addPixmap(QPixmap(icon_Segment), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)
        self.setWindowFlags(self.windowFlags() & ~(Qt.WindowContextHelpButtonHint))

        self.pushButton_Browser.clicked.connect(self.on_open_clicked)
        self.lineEdit_SamplesPath.textChanged.connect(self.on_text_changed)

    def on_open_clicked(self,Dialog):
        from qgis.PyQt.QtWidgets import QFileDialog
        folder_selected = QFileDialog.getExistingDirectory(None, "Select Folder to Open")
        if  folder_selected:
            self.lineEdit_SamplesPath.setText(folder_selected)

    def on_text_changed(self,text):
        samplePath = self.lineEdit_SamplesPath.text()#E:\DeepLearning\Samples\Building\256x256\Sat\Meter\negative_411702_202001_yicheng_city\crop
        result = samplePath.rsplit('/', 6)
        self.lineEdit_Class.setText(result[1].lower())
        self.lineEdit_labelSize.setText(result[2].split('x')[0])
        self.lineEdit_labelType.setText(result[3])
        self.lineEdit_labelGSD.setText(result[4].lower())
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
