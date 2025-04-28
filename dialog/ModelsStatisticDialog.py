# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QCoreApplication
from PyQt5.QtSql import QSqlDatabase, QSqlQueryModel
from lxml import etree
# XML文件的路径
from DeeplearningSystem import sample_cofing_path
from tools.CommonTool import show_info_message
from ui.ModelsStatisticUI import Ui_Dialog


class ModelsStatisticDialog(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
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
        # 连接 finished 信号（参数是对话框的返回值，如 Accepted/Rejected）
        self.finished.connect(self.on_dialog_closed)

        # 创建数据库连接
        self.connection_name = "connection_ModelsStatistic"  # 自定义连接名称
        self.db = QSqlDatabase.addDatabase("QSQLITE",self.connection_name)  # 使用SQLite，也可以是QMYSQL、QPSQL等
        self.db.setDatabaseName("databae_models.db")  # 数据库文件路径
        if not self.db.open():
            print("无法连接数据库")
            return False
        self.netModel = QSqlQueryModel()
        self.netModel.setQuery("SELECT * FROM imported_data", self.db)  # 执行SQL查询

        # 检查是否有错误
        if self.netModel.lastError().isValid():
            print("查询错误:", self.netModel.lastError().text())
        self.tableView.verticalHeader().setHidden(True)  # 等同于 setVisible(False)
        self.tableView.setModel(self.netModel)# 创建表格视图
        self.tableView.resizeColumnsToContents()       
        self.tableView.horizontalHeader().setSectionsClickable(True)# 设置 QTableView 的列头可排序
        self.toolButton_AttributeSelect.clicked.connect(self.AttributeSelect)
        self.toolButton_ClearSelect.clicked.connect(self.ClearSelect)   
    def on_dialog_closed(self, result):
        """对话框关闭时的回调
        print(f"对话框已关闭，返回值: {result}")
        if result == QDialog.Accepted:
            print("用户点击了确定或类似按钮")
        else:
            print("用户取消或直接关闭")
        """
        
        self.db.close()
        QSqlDatabase.removeDatabase(self.connection_name)  # 移除自定义名称的连接

    def AttributeSelect(self):       
        from dialog.ModelQueryDialog import ModelQueryDialog
        self.modelQueryDialog = ModelQueryDialog(self)
        result = self.modelQueryDialog.exec_()
        if result == QDialog.Accepted:
            self.toolButton_ClearSelect.setEnabled(True)
            """执行自定义查询"""
            query_text = "SELECT * FROM imported_data WHERE " + self.modelQueryDialog.textEdit_Code.toPlainText()
            print(query_text)
                
            self.netModel.setQuery(query_text, self.db)
            
            if self.netModel.lastError().isValid():
                print("查询错误:", self.netModel.lastError().text())
            else:
                """设置表格视图的公共方法"""
                self.tableView.setModel(self.netModel)
                self.tableView.resizeColumnsToContents()
            self.tableView.resizeColumnsToContents()  
        elif result == QDialog.Rejected:
            print("User clicked Close or pressed Escape")   
   
    def ClearSelect(self):
        """重置显示所有数据"""
        self.netModel.setQuery("SELECT * FROM imported_data", self.db)
        if self.netModel.lastError().isValid():
            print("查询错误:", self.netModel.lastError().text())
        else:
            """设置表格视图的公共方法"""
            self.tableView.setModel(self.netModel)
            self.tableView.resizeColumnsToContents()
        self.toolButton_ClearSelect.setEnabled(False)
