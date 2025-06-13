# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon, QPixmap
from PyQt5.QtCore import Qt, QSortFilterProxyModel
from lxml import etree
from PyQt5.QtSql import QSqlDatabase, QSqlQueryModel
# XML文件的路径
from DeeplearningSystem import sample_cofing_path
from tools.CommonTool import show_info_message
from ui.SamplesStatisticUI import Ui_Dialog


class SamplesStatisticDialog(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)  # 调用setupUi方法初始化界面
        
        # 在这里添加你的逻辑代码
        from os.path import join
        from DeeplearningSystem import base_dir
        png = join(base_dir, 'settings/icon', 'label_statistic.png') 
        icon = QIcon()
        icon.addPixmap(QPixmap(png), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)
        self.setWindowFlags(self.windowFlags() & ~(Qt.WindowContextHelpButtonHint))   

        # 创建数据库连接
        self.connection_name = "samples_conn1"  # 使用唯一连接名
        self.db = QSqlDatabase.addDatabase("QSQLITE", self.connection_name)
        dbs = join(base_dir, 'settings/db', 'databae_samples.db') 
        self.db.setDatabaseName(dbs)  # 数据库文件路径
        if not self.db.open():
            print("无法连接数据库")
            return False
        self.sampleModel = QSqlQueryModel()
        self.sampleModel.setQuery("SELECT * FROM imported_data", self.db)  # 执行SQL查询

        # 检查是否有错误
        if self.sampleModel.lastError().isValid():
            print("查询错误:", self.sampleModel.lastError().text())
        self.tableView.verticalHeader().setHidden(True)  # 等同于 setVisible(False)
        self.tableView.setModel(self.sampleModel)# 创建表格视图
        self.tableView.resizeColumnsToContents()       
        self.tableView.horizontalHeader().setSectionsClickable(True)# 设置 QTableView 的列头可排序
        self.toolButton_AttributeSelect.clicked.connect(self.AttributeSelect)
        self.toolButton_ClearSelect.clicked.connect(self.ClearSelect)
       
        self.label.setText(f'共计样本量：{sum_column(self.tableView,8)}个')
    def bak(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)  # 调用setupUi方法初始化界面
        
        # 在这里添加你的逻辑代码
        from os.path import join
        from DeeplearningSystem import base_dir
        png = join(base_dir, 'settings/icon', 'VectorEditor_AttributeEdit.png') 
        icon = QIcon()
        icon.addPixmap(QPixmap(png), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)
        self.setWindowFlags(self.windowFlags() & ~(Qt.WindowContextHelpButtonHint))

        self.sampleModel = QStandardItemModel() # 创建模型并设置数据
        self.sampleModel.setHorizontalHeaderLabels(["名称", "类别", "地市", "县区/景", "类型", "时相", "分辨率", "数量", "备注", "训练集", "验证集", "训:验", "查准", "查全", "IOU"])  # 设置列头标签       
        self.tableView.setModel(self.sampleModel)# 创建表格视图
        self.tableView.resizeColumnsToContents()       
        self.tableView.horizontalHeader().setSectionsClickable(True)# 设置 QTableView 的列头可排序
        self.toolButton_AttributeSelect.clicked.connect(self.AttributeSelect)
        self.toolButton_ClearSelect.clicked.connect(self.ClearSelect)

    def closeEvent(self, event):    
        if self.db and self.db.isOpen():
                self.db.close()
        del self.sampleModel, self.db
        # 确保移除连接
        if self.connection_name in QSqlDatabase.connectionNames():
            QSqlDatabase.removeDatabase(self.connection_name)
         # 最后调用父类关闭事件处理
        super().closeEvent(event)
        
    def AttributeSelect(self):       
        from dialog.AttributeQueryDialog import AttributeQueryDialog
        self.attributeQueryDialog = AttributeQueryDialog(self)
        result = self.attributeQueryDialog.exec_()
        if result == QDialog.Accepted:
            self.toolButton_ClearSelect.setEnabled(True)
            """执行自定义查询"""
            query_text = "SELECT * FROM imported_data WHERE " + self.attributeQueryDialog.textEdit_Code.toPlainText()
            print(query_text)
                
            self.sampleModel.setQuery(query_text, self.db)
            
            if self.sampleModel.lastError().isValid():
                print("查询错误:", self.sampleModel.lastError().text())
            else:
                """设置表格视图的公共方法"""
                self.tableView.setModel(self.sampleModel)
                self.tableView.resizeColumnsToContents()
            sum = sum_column(self.tableView,8)
            self.label.setText(f'共计样本量：{sum}个')
            self.tableView.resizeColumnsToContents()  
        elif result == QDialog.Rejected:
            print("User clicked Close or pressed Escape")   
   
    def ClearSelect(self):
        """重置显示所有数据"""
        self.sampleModel.setQuery("SELECT * FROM imported_data", self.db)
        if self.sampleModel.lastError().isValid():
            print("查询错误:", self.sampleModel.lastError().text())
        else:
            """设置表格视图的公共方法"""
            self.tableView.setModel(self.sampleModel)
            self.tableView.resizeColumnsToContents()
        sum = sum_column(self.tableView,8)
        self.label.setText(f'共计样本量：{sum}个')
        self.toolButton_ClearSelect.setEnabled(False)

def sum_column(table_view, column_index):
        model = table_view.model()
        total = 0
        for row in range(model.rowCount()):
            index = model.index(row, column_index)
            value = model.data(index)  # 获取单元格数据
            try:
                total += int(value)  # 转换为数值并累加
            except (ValueError, TypeError):
                continue  # 忽略非数值单元格
        return total
