# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon, QPixmap
from PyQt5.QtCore import Qt
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.core import QgsProject, QgsRasterLayer
from lxml import etree
# XML文件的路径
from DeeplearningSystem import model_cofing_path
from tools.CommonTool import show_info_message
from ui.SegmentUI import Ui_Dialog


class SegmentDialog(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)  # 调用setupUi方法初始化界面
        
        # 在这里添加你的逻辑代码
        from os.path import join
        from DeeplearningSystem import base_dir
        png = join(base_dir, 'settings/icon', 'Segment.png') 
        icon = QIcon()
        icon.addPixmap(QPixmap(png), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)
        self.setWindowFlags(self.windowFlags() & ~(Qt.WindowContextHelpButtonHint))

        self.pushButton_openImage.clicked.connect(self.on_openImage_clicked)     
        self.pushButton_saveImage.clicked.connect(self.on_saveImage_clicked)    
        self.pushButton_queryModel.clicked.connect(self.on_queryModel_clicked) 
        self.comboBox_modelClass.activated.connect(self.on_comboBox_modelClass_activated)      
        
        # 初始化数据
        self.comboBox_openImage.clear()
        self.comboBox_openImage.currentIndex = -1
        for layer_name, layer in QgsProject.instance().mapLayers().items():
            if isinstance(layer, QgsRasterLayer):
                filepath = layer.dataProvider().dataSourceUri()
                self.comboBox_openImage.addItem(filepath)   
        # 初始化类别
        # 加载现有 XML
        tree = etree.parse(model_cofing_path)
        root = tree.getroot()# Samples
        for child in root.iterchildren():
            self.comboBox_modelClass.addItem(child.get('EnglishName'))         
        self.comboBox_modelClass.setCurrentIndex(-1)       
        
     # 初始化网络
    def on_comboBox_modelClass_activated(self):
        self.comboBox_modelNet.clear()
        modelClass = self.comboBox_modelClass.currentText()
         # 加载现有 XML
        tree = etree.parse(model_cofing_path)
        root = tree.getroot()# Models
        # 查找特定ID的节点
        node = tree.xpath(f'//ModelClass[@EnglishName="{modelClass}"]')[0]
        for child in node.iterchildren():
            self.comboBox_modelNet.addItem(child.get('Name'))         
        self.comboBox_modelNet.setCurrentIndex(-1)
                                                                            
    def on_openImage_clicked(self,Dialog):
        from qgis.PyQt.QtWidgets import QFileDialog
        path_to_tif,_ = QFileDialog.getOpenFileName(None, '打开', '', 'Raster Files (*.tif;*.tiff;*.img;*.dat);;All Files (*.*)')
        if  path_to_tif=="":
            return
        self.comboBox_openImage.setCurrentText(path_to_tif)

    def on_saveImage_clicked(self,Dialog):
        from qgis.PyQt.QtWidgets import QFileDialog
        path_to_tif,_ = QFileDialog.getSaveFileName(None, '保存', '', 'Raster Files (*.img);;All Files (*.*)')
        if  path_to_tif=="":
            return
        self.lineEdit_saveImage.setText(path_to_tif)

    def on_queryModel_clicked(self):
        #清空
        self.comboBox_modelList.clear()
        modelClass = self.comboBox_modelClass.currentText()
        modelNet = self.comboBox_modelNet.currentText()
        # 加载现有 XML
        tree = etree.parse(model_cofing_path)
        # 查找特定ID的节点
        node = tree.xpath(f'//ModelClass[@EnglishName="{modelClass}"]')[0]
        node1 = node.xpath(f'//ModelType[@Name="{modelNet}"]')[0]
        if node1 is not None:
            from os.path import basename,exists
            self.m_modelFile = node1.text
            self.comboBox_modelList.addItem(basename(self.m_modelFile))
            if not exists(self.m_modelFile):
                show_info_message(self, '提示', f"查询不到模型文件，请检查其是否存在！\n{self.m_modelFile}")
        else:                                     
            show_info_message(self, '提示', "查询不到模型，请选择其它模型！")
        self.comboBox_modelList.setCurrentIndex(-1)