# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon, QPixmap
from PyQt5.QtCore import Qt
from ui.SplitDatasetUI import Ui_Dialog


class SplitDatasetDialog(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)  # 调用setupUi方法初始化界面
        
        # 在这里添加你的逻辑代码
        from os.path import join
        from DeeplearningSystem import base_dir
        icon_Segment = join(base_dir, 'settings/icon', 'SplitDataset.png') 
        icon = QIcon()
        icon.addPixmap(QPixmap(icon_Segment), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)
        self.setWindowFlags(self.windowFlags() & ~(Qt.WindowContextHelpButtonHint))
        self.pushButton_QuerySample.clicked.connect(self.querySample_clicked)
        self.lineEdit_valset.textEdited.connect(self.valset_text_changed)
        self.lineEdit_testset.textEdited.connect(self.testset_text_changed)

        self.comboBox_sampleClass.setCurrentIndex(-1)
        #self.checkBox.stateChanged.connect(self.onHeaderCheckBoxStateChanged) 
        # 创建模型并设置数据
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["名称", "类别", "尺寸", "数量", "选择"])  # 设置列头标签
        # 创建表格视图
        self.tableView_sampleList.setModel(self.model)
        self.tableView_sampleList.resizeColumnsToContents()        
        # 设置 QTableView 的列头可排序
        self.tableView_sampleList.horizontalHeader().setSectionsClickable(True)
        self.tableView_sampleList.horizontalHeader().setSortIndicatorShown(True)
        # 点击时触发单选逻辑
        self.tableView_sampleList.clicked.connect(self.setCheckedItem)

        # 初始化
        from lxml import etree
        # XML文件的路径
        from DeeplearningSystem import sample_cofing_path
        tree = etree.parse(sample_cofing_path)
        root = tree.getroot()# Samples
        for child in root.iterchildren():
            self.comboBox_sampleClass.addItem(child.get('EnglishName'))           
        self.comboBox_sampleClass.setCurrentIndex(-1)

    def querySample_clicked(self):
        samplesClass = self.comboBox_sampleClass.currentText()
        self.sampleList = []
        self.sampleNums = []
        #print(f"sampleClass={sampleClass}")    
        # XML文件的路径
        from DeeplearningSystem import sample_cofing_path
        # 解析XML文件
        from lxml import etree
        # 加载现有 XML
        tree = etree.parse(sample_cofing_path)
        # 查找特定ID的节点
        node = tree.xpath(f'//SampleClass[@EnglishName="{samplesClass}"]')[0]
        # 遍历所有节点
        for child in node.iterchildren():
            samplePath = child.text
            from glob import glob
            count = len(glob(f'{samplePath}/image/*.tif')) + len(glob(f'{samplePath}/image/*.tiff'))
            checkbox_item = QStandardItem()
            checkbox_item.setCheckable(True)
            #checkbox_item.setCheckState(Qt.Unchecked)  # 可选：设置初始检查状态                               
            row = [QStandardItem(child.get('Name')), QStandardItem(child.get('Type')), QStandardItem(child.get('Size')), QStandardItem(str(count)),checkbox_item]
            self.sampleList.append(samplePath)
            self.sampleNums.append(count)
            # 将复选框项添加到行列表中（假设您想在列表的末尾添加它）
            self.model.appendRow(row)
        self.tableView_sampleList.resizeColumnsToContents() 

    def setCheckedItem(self, index):
        column_index = 4
        row = index.row()
        #print(index.row(),index.column())
        self.model.item(row, column_index).setCheckState(Qt.Checked)
        valsetNums = int(self.lineEdit_valset.text())
        testsetNums = int(self.lineEdit_testset.text())
        self.lineEdit_trainset.setText(str(int(self.sampleNums[row])-valsetNums-testsetNums))
        for row_index in range(self.model.rowCount()): 
            self.model.item(row_index, column_index).setCheckState(2 if row_index == row else 0)  # 2=选中, 0=未选 

    def valset_text_changed(self,text):
        valsetNums = int(text)
        testsetNums = int(self.lineEdit_testset.text())
        column_index = 4
        for row_index in range(self.model.rowCount()):             
            check_state = self.model.item(row_index, column_index).checkState()
            if check_state == Qt.Checked:
                self.lineEdit_trainset.setText(str(int(self.sampleNums[row_index])-valsetNums-testsetNums))
                return

    def testset_text_changed(self,text):
        valsetNums = int(self.lineEdit_valset.text())
        testsetNums = int(text)
        column_index = 4
        for row_index in range(self.model.rowCount()):             
            check_state = self.model.item(row_index, column_index).checkState()
            if check_state == Qt.Checked:
                self.lineEdit_trainset.setText(str(int(self.sampleNums[row_index])-valsetNums-testsetNums))
                return
