# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt
from lxml import etree
# XML文件的路径
from DeeplearningSystem import sample_cofing_path
from ui.QuerySamplesUI import Ui_Dialog
from xml.dom import minidom

class QuerySamplesDialog(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)  # 调用setupUi方法初始化界面
        
        # 在这里添加你的逻辑代码
        from os.path import join
        from DeeplearningSystem import base_dir
        png = join(base_dir, 'settings/icon', 'label_query.png') 
        icon = QIcon()
        icon.addPixmap(QPixmap(png), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)
        self.setWindowFlags(self.windowFlags() & ~(Qt.WindowContextHelpButtonHint))

        self.comboBox_Type.activated.connect(self.comboBox_Type_activated)# 将 QComboBox 的 currentIndexChanged 信号连接到槽函数
        self.comboBox_Class.activated.connect(self.comboBox_Class_activated)# 将 QComboBox 的 currentIndexChanged 信号连接到槽函数
        self.comboBox_Size.activated.connect(self.comboBox_Size_activated)# 将 QComboBox 的 currentIndexChanged 信号连接到槽函数
        self.comboBox_GSD.activated.connect(self.comboBox_GSD_activated)# 将 QComboBox 的 currentIndexChanged 信号连接到槽函数

        # 初始化     
        tree = etree.parse(sample_cofing_path)
        root = tree.getroot()# Samples
        for child in root.iterchildren():
            self.comboBox_Class.addItem(child.get('EnglishName'))           
        self.comboBox_Class.setCurrentIndex(-1)

    # 定义槽函数，用于响应 QComboBox 的选择变化
    def comboBox_Class_activated(self, index):
        self.comboBox_Size.clear()
        self.comboBox_Type.clear()
        self.comboBox_GSD.clear()
        self.comboBox_Name.clear()
        self.comboBox_Size.setEnabled(True)       
        selected_text = self.comboBox_Class.currentText()  # 获取当前选中的文本
        # 解析XML文件
        tree = etree.parse(sample_cofing_path)
        # 查找特定ID的节点
        node = tree.xpath(f'//SampleClass[@EnglishName="{selected_text}"]')[0]
        # 遍历所有节点
        for child in node.iterchildren():
            if self.comboBox_Size.findText(child.get('Size')) == -1:  # 检查是否已存在
                self.comboBox_Size.addItem(child.get('Size'))
        self.comboBox_Size.setCurrentIndex(-1)

    def comboBox_Size_activated(self, index):
        self.comboBox_Type.clear()
        self.comboBox_GSD.clear()
        self.comboBox_Name.clear()
        self.comboBox_Type.setEnabled(True)
        selected_text = self.comboBox_Class.currentText()  # 获取当前选中的文本
        # 解析XML文件
        tree = etree.parse(sample_cofing_path)
        # 查找特定ID的节点
        node = tree.xpath(f'//SampleClass[@EnglishName="{selected_text}"]')[0]
        nodes = node.xpath(f'//SamplePath[@Size="{self.comboBox_Size.currentText()}"]')
        # 遍历所有节点
        for element in nodes:
            if self.comboBox_Type.findText(element.get('Type')) == -1:  # 检查是否已存在
                self.comboBox_Type.addItem(element.get('Type'))
        self.comboBox_Type.setCurrentIndex(-1)

    def comboBox_Type_activated(self, index):
        self.comboBox_GSD.clear()
        self.comboBox_Name.clear()
        self.comboBox_GSD.setEnabled(True)
        selected_text = self.comboBox_Class.currentText()  # 获取当前选中的文本
        # 解析XML文件
        tree = etree.parse(sample_cofing_path)
        # 查找特定ID的节点
        node = tree.xpath(f'//SampleClass[@EnglishName="{selected_text}"]')[0]
        nodes = node.xpath(f'//SamplePath[@Type="{self.comboBox_Type.currentText()}" and @Size="{self.comboBox_Size.currentText()}"]')
        # 遍历所有节点
        for element in nodes:
            if self.comboBox_GSD.findText(element.get('GSD')) == -1:  # 检查是否已存在
                self.comboBox_GSD.addItem(element.get('GSD'))
        self.comboBox_GSD.setCurrentIndex(-1)

    def comboBox_GSD_activated(self, index):
        self.comboBox_Name.clear()
        self.comboBox_Name.setEnabled(True)
        selected_text = self.comboBox_Class.currentText()  # 获取当前选中的文本
        samplesType = self.comboBox_Type.currentText()
        samplesGSD = self.comboBox_GSD.currentText()
        samplesSize = self.comboBox_Size.currentText()
        # XML文件的路径
        from DeeplearningSystem import sample_cofing_path
        # 加载现有 XML
        tree = etree.parse(sample_cofing_path)
        # 查找特定ID的节点
        node = tree.xpath(f'//SampleClass[@EnglishName="{selected_text}"]')[0]
        items = node.xpath(f'./SamplePath[@Type="{samplesType}" and @Size="{samplesSize}" and @GSD="{samplesGSD}"]')
        # 遍历所有节点
        for item in items:
            # 获取节点文本内容
            #text = item.text
            # 获取属性
            item_id = item.get('Name')
            if self.comboBox_Name.findText(item_id) == -1:  # 检查是否已存在
                self.comboBox_Name.addItem(item_id)
        
        self.comboBox_Name.setCurrentIndex(-1)