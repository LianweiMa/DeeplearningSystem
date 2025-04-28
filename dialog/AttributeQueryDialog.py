# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QDialog, QListView
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QStringListModel
from ui.AttributeQueryUI import Ui_Dialog


class AttributeQueryDialog(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setupUi(self)  # 调用setupUi方法初始化界面
        
        # 在这里添加你的逻辑代码
        from os.path import join
        from DeeplearningSystem import base_dir
        png = join(base_dir, 'settings/icon', 'VectorEditor_AttributeEdit.png') 
        icon = QIcon()
        icon.addPixmap(QPixmap(png), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)
        self.setWindowFlags(self.windowFlags() & ~(Qt.WindowContextHelpButtonHint))

        self.attributeListModel = QStringListModel()
        self.listView_AttributeList.setModel(self.attributeListModel)  # 绑定模型
        self.valueListModel = QStringListModel()
        self.listView_ValueList.setModel(self.valueListModel)  # 绑定模型

        # 初始数据
        self.attributeListModel.setStringList(["名称", "类别", "地市", "县区/景", "类型", "时相", "分辨率", "数量", "备注", "训练集", "验证集", "训:验", "查准", "查全", "IOU"])
        self.listView_AttributeList.setEditTriggers(QListView.NoEditTriggers)  # 完全禁止编辑
        self.listView_ValueList.setEditTriggers(QListView.NoEditTriggers)  # 完全禁止编辑

        # 在初始化代码中连接信号 
        self.pushButton_equal.clicked.connect(self.equal)
        self.pushButton_noEqual.clicked.connect(self.noEqual)
        self.pushButton_Like.clicked.connect(self.like)
        self.pushButton_LessThan.clicked.connect(self.LessThan)
        self.pushButton_LTorE.clicked.connect(self.LTorE)
        self.pushButton_Or.clicked.connect(self.Or)
        self.pushButton_GTorE.clicked.connect(self.GTorE)
        self.pushButton_GreaterThan.clicked.connect(self.GreaterThan)
        self.pushButton_Not.clicked.connect(self.Not)
        self.pushButton_BETWEEN.clicked.connect(self.BETWEEN)
        self.pushButton_IsNull.clicked.connect(self.IsNull)
        self.pushButton_And.clicked.connect(self.And)               
        self.pushButton_Clear.clicked.connect(self.Clear)
        self.listView_AttributeList.doubleClicked.connect(self.on_attributelist_double_clicked)
        self.listView_ValueList.doubleClicked.connect(self.on_valuelist_double_clicked)
        self.pushButton_GetValues.clicked.connect(self.GetValues)


    # 定义槽函数
    def equal(self):
        self.SetCussorText(' = ')

    def noEqual(self):
        self.SetCussorText(' <> ')

    def like(self):
        self.SetCussorText(' LIKE ')

    def LessThan(self):
        self.SetCussorText(' < ')

    def LTorE(self):
        self.SetCussorText(' <= ')

    def Or(self):
        self.SetCussorText(' OR ')

    def GTorE(self):
        self.SetCussorText(' >= ')
    
    def GreaterThan(self):
        self.SetCussorText(' > ')   
    
    def Not(self):
        self.SetCussorText(' NOT ')

    def BETWEEN(self):
        self.SetCussorText(' BETWEEN ')

    def IsNull(self):
        self.SetCussorText(' IS NULL')

    def And(self):
        self.SetCussorText(' AND ')
    
    def Clear(self):
        self.textEdit_Code.clear()

    def on_attributelist_double_clicked(self, index):
        value = index.data()  # 获取双击项的文本
        print("双击的值:", value)
        self.SetCussorText(value)

    def on_valuelist_double_clicked(self, index):
        value = index.data()  # 获取双击项的文本
        print("双击的值:", value)
        self.SetCussorText(f' "{value}"')

    def GetValues(self):
        selected_indexes = self.listView_AttributeList.selectedIndexes()
        if selected_indexes:  # 确保有选中项
            selected_value = selected_indexes[0].data()  # 获取第一项的文本
            print("选中的值:", selected_value)
            for col in range(self.parent.sampleModel.columnCount()):
                header_data = self.parent.sampleModel.headerData(col, Qt.Horizontal)  # 获取列名
                if header_data == selected_value:
                    values = []
                    for row in range(self.parent.sampleModel.rowCount()):
                        index = self.parent.sampleModel.index(row, col)
                        value = self.parent.sampleModel.data(index)
                        values.append(str(value))
                    self.valueListModel.setStringList(list(set(values)))
                    return
                
    def SetCussorText(self,text):
        # 获取当前光标
        cursor = self.textEdit_Code.textCursor()
        
        # 在光标位置插入文本
        cursor.insertText(text)
        
        # 将修改后的光标设置回文本编辑框
        self.textEdit_Code.setTextCursor(cursor)
