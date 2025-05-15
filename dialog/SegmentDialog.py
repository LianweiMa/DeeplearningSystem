# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt
from qgis.core import QgsProject, QgsRasterLayer
from lxml import etree
from os.path import exists
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

        self.pushButton_openImage.clicked.connect(self.openImage_clicked)     
        self.pushButton_saveImage.clicked.connect(self.saveImage_clicked)    
        self.pushButton_queryModel.clicked.connect(self.queryModel_clicked) 
        self.comboBox_modelClass.activated.connect(self.comboBox_modelClass_activated)      
        
        # 初始化数据
        self.comboBox_openImage.clear()
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
    def comboBox_modelClass_activated(self):
        self.comboBox_modelNet.clear()
        modelClass = self.comboBox_modelClass.currentText()
        # 加载现有 XML
        tree = etree.parse(model_cofing_path)
        # 查找特定ID的节点
        node = tree.xpath(f'//ModelClass[@EnglishName="{modelClass}"]')
        if node:
            for child in node[0].iterchildren():
                self.comboBox_modelNet.addItem(child.get('Net'))           
            self.comboBox_modelNet.setCurrentIndex(-1)      
        else:                                     
            show_info_message(self, '提示', f"未找到 EnglishName='{modelClass}' 的 ModelClass 节点") 
                                                                            
    def openImage_clicked(self,Dialog):
        from qgis.PyQt.QtWidgets import QFileDialog
        path_to_tif,_ = QFileDialog.getOpenFileName(None, '打开', '', 'Raster Files (*.tif;*.tiff;*.img;*.dat);;All Files (*.*)')
        if  path_to_tif=="":
            return
        self.comboBox_openImage.setCurrentText(path_to_tif)

    def saveImage_clicked(self,Dialog):
        from qgis.PyQt.QtWidgets import QFileDialog
        path_to_tif,_ = QFileDialog.getSaveFileName(None, '保存', '', 'Raster Files (*.img);;All Files (*.*)')
        if  path_to_tif=="":
            return
        self.lineEdit_saveImage.setText(path_to_tif)

    def queryModel_clicked(self):
        #清空
        self.comboBox_modelList.clear()
        self.m_modelFile = []
        modelClass = self.comboBox_modelClass.currentText()
        modelNet = self.comboBox_modelNet.currentText()
        # 加载现有 XML
        tree = etree.parse(model_cofing_path)
        # 查找特定ID的节点
        node = tree.xpath(f'//ModelClass[@EnglishName="{modelClass}"]')[0]
        node1 = node.xpath(f'.//ModelPath[@Net="{modelNet}"]')
        if node1 is not None:
            for element in node1:           
                self.m_modelFile.append(element.text)
                paras = element.text.split('_')
                self.comboBox_modelList.addItem(f"{element.get('Name')}({'_'.join(paras[3:]).rsplit('.',1)[0]})")
                if not exists(element.text):
                    show_info_message(self, '提示', f"查询不到模型文件，请检查其是否存在！\n{element.text}")         
            self.comboBox_modelList.setCurrentIndex(-1)
            # 计算最长文本的宽度，并设置下拉列表的最小宽度
            self.comboBox_modelList.view().setMinimumWidth(
                self.comboBox_modelList.fontMetrics().boundingRect(
                    max((self.comboBox_modelList.itemText(i) for i in range(self.comboBox_modelList.count())), key=len)
                ).width() + 20  # 加 20 像素的边距
            )          
        else:                                     
            show_info_message(self, '提示', "查询不到模型，请选择其它模型！") 