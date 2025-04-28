# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon, QPixmap
from PyQt5.QtCore import Qt
from lxml import etree
from os.path import basename
# XML文件的路径
from DeeplearningSystem import model_cofing_path
from tools.CommonTool import show_info_message
from ui.DeleteModelsUI import Ui_Dialog


class DeleteModelsDialog(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)  # 调用setupUi方法初始化界面
        
        # 在这里添加你的逻辑代码
        from os.path import join
        from DeeplearningSystem import base_dir
        icon_Segment = join(base_dir, 'settings/icon', 'net_delete.png') 
        icon = QIcon()
        icon.addPixmap(QPixmap(icon_Segment), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)
        self.setWindowFlags(self.windowFlags() & ~(Qt.WindowContextHelpButtonHint))

        self.comboBox_Class.activated.connect(self.comboBox_Class_activated)# 将 QComboBox 的 currentIndexChanged 信号连接到槽函数
        self.pushButton_Query.clicked.connect(self.query_clicked)

        # 初始化
        tree = etree.parse(model_cofing_path)
        root = tree.getroot()
        for child in root.iterchildren():
            self.comboBox_Class.addItem(child.get('EnglishName'))      
        self.comboBox_Class.setCurrentIndex(-1)
        self.checkBox.stateChanged.connect(self.onHeaderCheckBoxStateChanged) 
        # 创建模型并设置数据
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["选择", "名称", "类别", "分辨率", "网络", "轮数", "损失(train)", "精度(train)", "损失(val)", "查准(val)", "查全(val)", "IOU(val)"])  # 设置列头标签
        # 创建表格视图
        self.tableView_List.setModel(self.model)
        self.tableView_List.resizeColumnsToContents()        
        # 设置 QTableView 的列头可排序
        self.tableView_List.horizontalHeader().setSectionsClickable(True)
        self.tableView_List.horizontalHeader().setSortIndicatorShown(True)

    def query_clicked(self):        
        Class = self.comboBox_Class.currentText()
        self.list = []        
        # 解析XML文件
        tree = etree.parse(model_cofing_path)
        node = tree.xpath(f'//ModelClass[@EnglishName="{Class}"]')[0]# 默认一个
        if node is None:
            show_info_message(None, '提示', f"没有找到类别为{Class}的样本库！\n请检查后，重新选择！")
            return
        for child in node.iterchildren():
            modelName = basename(child.text).rsplit('.',1)[0]
            s = modelName.split('_')
            Net = s[1]  
            epoch = s[3].split('=')[1]
            trainloss = s[4].split('=')[1]
            trainacc = s[5].split('=')[1]
            valloss = s[6].split('=')[1]
            valacc = s[7].split('=')[1]
            valrecall = s[8].split('=')[1]
            valiou = s[9].split('=')[1]        
            checkbox_item = QStandardItem()
            checkbox_item.setCheckable(True)                             
            row = [checkbox_item, QStandardItem(child.get('Name')), QStandardItem(Class), QStandardItem(child.get('GSD')), QStandardItem(Net), QStandardItem(epoch), QStandardItem(trainloss), 
                   QStandardItem(trainacc), QStandardItem(valloss), QStandardItem(valacc), QStandardItem(valrecall), QStandardItem(valiou)]
            self.list.append(child.get('Name'))
            # 将复选框项添加到行列表中（假设您想在列表的末尾添加它）
            self.model.appendRow(row)
        self.tableView_List.resizeColumnsToContents()  

    def onHeaderCheckBoxStateChanged(self, state):
        # 根据表头复选框的状态遍历模型中的所有行，并设置相应列的复选框项
        column_index = 4  # 假设复选框项在第三列（索引为4）
        # 获取选择模型
        selection_model = self.tableView_List.selectionModel()
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
       
        show_info_message(None, '提示', f"共选择{number_of_selected_rows}模型！")

    def comboBox_Class_activated(self,index):         
        self.model.removeRows(0, self.model.rowCount())
        self.tableView_List.resizeColumnsToContents()