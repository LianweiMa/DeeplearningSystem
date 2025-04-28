# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon, QPixmap
from PyQt5.QtCore import Qt
from ui.TrainUI import Ui_Dialog


class TrainDialog(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)  # 调用setupUi方法初始化界面
        
        # 在这里添加你的逻辑代码
        from os.path import join
        from DeeplearningSystem import base_dir
        png = join(base_dir, 'settings/icon', 'Train_Start.png') 
        icon = QIcon()
        icon.addPixmap(QPixmap(png), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)
        self.setWindowFlags(self.windowFlags() & ~(Qt.WindowContextHelpButtonHint))
        self.comboBox_modelNet.addItems([ "AUNet", "UNet", "DeepLabV3Plus" ])
        self.pushButton_QuerySample.clicked.connect(self.querySample_clicked)
        self.pushButton_saveModel.clicked.connect(self.saveModel_clicked)

        self.comboBox_sampleClass.setCurrentIndex(-1)
        self.checkBox.stateChanged.connect(self.onHeaderCheckBoxStateChanged) 
        # 创建模型并设置数据
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["名称", "类别", "尺寸", "数量", "选择"])  # 设置列头标签
        # 创建表格视图
        self.tableView_sampleList.setModel(self.model)
        self.tableView_sampleList.resizeColumnsToContents()        
        # 设置 QTableView 的列头可排序
        self.tableView_sampleList.horizontalHeader().setSectionsClickable(True)
        self.tableView_sampleList.horizontalHeader().setSortIndicatorShown(True)

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
            # 将复选框项添加到行列表中（假设您想在列表的末尾添加它）
            self.model.appendRow(row)
        self.tableView_sampleList.resizeColumnsToContents() 

    def onHeaderCheckBoxStateChanged(self, state):
        # 根据表头复选框的状态遍历模型中的所有行，并设置相应列的复选框项
        column_index = 4  # 假设复选框项在第三列（索引为4）
        # 获取选择模型
        selection_model = self.tableView_sampleList.selectionModel()
        # 获取所有选中的行索引（这里我们假设关心的是顶层项的选中情况，所以传入 0 作为列号）
        selected_rows = selection_model.selectedRows(0)       
        # 计算选中的行数
        number_of_selected_rows = len(selected_rows)       
        #print(f"Number of selected rows: {number_of_selected_rows}")
        if number_of_selected_rows>0:
            # 检查目标行是否在选中的行中
            for index in selected_rows:
                checkbox_item = self.model.item(index.row(), column_index)
                if checkbox_item.isCheckable():
                    checkbox_item.setCheckState(state)
        else:
            number_of_selected_rows = 0
            for row_index in range(self.model.rowCount()):
                
                checkbox_item = self.model.item(row_index, column_index)
                if checkbox_item.isCheckable():
                    checkbox_item.setCheckState(state)
                    
                check_state = self.model.item(row_index, column_index).checkState()
                if check_state == Qt.Checked:
                    number_of_selected_rows+=1

        from tools.CommonTool import show_info_message
        show_info_message(self, '样本选择', f"共选择{number_of_selected_rows}样本分库！")

    def saveModel_clicked(self,Dialog):
        from qgis.PyQt.QtWidgets import QFileDialog
        folder_selected = QFileDialog.getExistingDirectory(None, "Select Folder to Save")
        if  folder_selected:
            self.lineEdit_saveModelPath.setText(folder_selected)
