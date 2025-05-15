# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QComboBox, QCheckBox, QWidget, QHBoxLayout
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt
from qgis.core import QgsProject
from os.path import basename
import uuid
from ui.CreateShapeUI import Ui_Dialog


class CreateShapeDialog(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)  # 调用setupUi方法初始化界面
        self.parent = parent
        
        # 在这里添加你的逻辑代码
        from os.path import join
        from DeeplearningSystem import base_dir
        png = join(base_dir, 'settings/icon', 'VectorEditor_CreateLayer.png') 
        icon = QIcon()
        icon.addPixmap(QPixmap(png), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)
        self.setWindowFlags(self.windowFlags() & ~(Qt.WindowContextHelpButtonHint))
        self.comboBox_featureType.addItems([ "点", "线", "面" ])
        self.comboBox_featureType.setCurrentIndex(-1)    
        # 5.0 样本管理栏(右) 
        '''    
        self.model = QStandardItemModel() # 创建模型并设置数据
        self.model.setHorizontalHeaderLabels(["名称", "类型", "宽度", "精度", "编辑"])  # 设置列头标签       
        self.tableView.setModel(self.model)# 创建表格视图
        self.tableView.resizeColumnsToContents()       
        self.tableView.horizontalHeader().setSectionsClickable(True)# 设置 QTableView 的列头可排序   
        '''

        self.pushButton_output.clicked.connect(self.output_clicked)    
        self.pushButton_openCrs.clicked.connect(self.openCrs_clicked)  
        self.pushButton_add.clicked.connect(self.add_clicked)
        self.pushButton_del.clicked.connect(self.del_clicked)

    def output_clicked(self,Dialog):
        from qgis.PyQt.QtWidgets import QFileDialog
        path,_ = QFileDialog.getSaveFileName(None, '保存', '', 'Shape Files (*.shp);;All Files (*.*)')
        if  path=="":
            return
        self.lineEdit_output.setText(path)

    def openCrs_clicked(self):
        from qgis.gui import QgsProjectionSelectionDialog
        dialog = QgsProjectionSelectionDialog(self)
        if dialog.exec_():
            selected_crs = dialog.crs()
            self.lineEdit_crs.setText(f"{selected_crs.authid()}")
            print(f"选择的坐标系: {selected_crs.authid()}")

    def add_clicked(self):
        row_count = self.tableWidget.rowCount()
        self.tableWidget.insertRow(row_count)  # 这会增加行数
        # 添加带ComboBox的单元格
        combo = QComboBox()
        combo.addItems(["整数", "浮点数", "布尔值", "字符串"])
        combo.setCurrentIndex(-1)
        self.tableWidget.setCellWidget(row_count, 1, combo)
        checkbox = QCheckBox()
        checkbox.setChecked(False)  
        # 创建容器widget和布局
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setAlignment(Qt.AlignCenter)  # 设置布局居中
        layout.setContentsMargins(0, 0, 0, 0)  # 去除边距     
        layout.addWidget(checkbox)                    
        self.tableWidget.setCellWidget(row_count, 4, widget)

    def del_clicked(self):
        # 获取行列数
        row_count = self.tableWidget.rowCount()
        # 遍历所有单元格
        for row in range(row_count):
            # 获取单元格中的widget
            widget = self.tableWidget.cellWidget(row, 4)
            # 从widget中查找QCheckBox
            checkbox = widget.findChild(QCheckBox)  # 返回第一个找到的QCheckBox
            check_state = checkbox.checkState()
            if check_state == Qt.Checked:
                self.tableWidget.removeRow(row)