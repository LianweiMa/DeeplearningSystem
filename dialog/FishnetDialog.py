# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QDialog, QFileDialog
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt
from qgis.core import QgsProject
from os.path import basename
import uuid
from ui.FishnetUI import Ui_Dialog


class FishnetDialog(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)  # 调用setupUi方法初始化界面
        self.parent = parent
        
        # 在这里添加你的逻辑代码
        from os.path import join
        from DeeplearningSystem import base_dir
        png = join(base_dir, 'settings/icon', 'create_fishnet.png') 
        icon = QIcon()
        icon.addPixmap(QPixmap(png), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)
        self.setWindowFlags(self.windowFlags() & ~(Qt.WindowContextHelpButtonHint))

        # 初始化数据
        self.layerlist = []
        self.comboBox_dataList.clear()      
        for layer_name, layer in QgsProject.instance().mapLayers().items():          
            self.comboBox_dataList.addItem(layer.name())
            self.layerlist.append(layer)
        self.comboBox_dataList.setCurrentIndex(-1)

        self.pushButton_output.clicked.connect(self.output_clicked)    
        self.comboBox_dataList.activated.connect(self.comboBox_dataList_activated)   
        self.lineEdit_width.textEdited.connect(self.width_text_changed)
        self.lineEdit_height.textEdited.connect(self.height_text_changed)
        self.pushButton_clear.clicked.connect(self.clear_clicked)   

    def output_clicked(self,Dialog):
        from qgis.PyQt.QtWidgets import QFileDialog
        path,_ = QFileDialog.getSaveFileName(None, '保存', '', 'Shape Files (*.shp);;All Files (*.*)')
        if  path=="":
            return
        self.lineEdit_output.setText(path)

     # 初始化网络
    def comboBox_dataList_activated(self):
        extent = self.layerlist[self.comboBox_dataList.currentIndex()].extent()
        print(extent)
        self.lineEdit_top.setText(str(extent.yMaximum()))
        self.lineEdit_bottom.setText(str(extent.yMinimum()))
        self.lineEdit_left.setText(str(extent.xMinimum()))
        self.lineEdit_right.setText(str(extent.xMaximum()))

    def width_text_changed(self,text):
        xmin = float(self.lineEdit_left.text())
        xmax = float(self.lineEdit_right.text())
        cols = int((xmax - xmin) / float(text))
        self.lineEdit_cols.setText(str(cols))

    def height_text_changed(self,text):
        ymin = float(self.lineEdit_bottom.text())
        ymax = float(self.lineEdit_top.text())
        rows = int((ymax - ymin) / float(text))
        self.lineEdit_rows.setText(str(rows))
    
    def clear_clicked(self):
        self.lineEdit_bottom.clear()
        self.lineEdit_left.clear()
        self.lineEdit_right.clear()
        self.lineEdit_top.clear()