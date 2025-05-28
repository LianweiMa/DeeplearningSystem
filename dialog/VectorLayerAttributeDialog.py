
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QDialog, QDesktopWidget
from qgis.core import QgsVectorLayerCache,QgsVectorLayer,QgsExpression, QgsExpressionContext,QgsExpressionContextUtils, QgsFeatureRequest
from qgis.gui import QgsAttributeTableView, QgsAttributeTableModel, QgsAttributeTableFilterModel
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt,QItemSelection,QTimer,QItemSelectionModel
from ui.VectorLayerAttributeUI import Ui_Dialog
from tools.CommonTool import show_info_message


class VectorLayerAttributeDialog(QDialog, Ui_Dialog):
    def __init__(self, mainWindows, layer):
        #mainWindows : MainWindow
        super(VectorLayerAttributeDialog, self).__init__(mainWindows)
        self.setupUi(self)  # 调用setupUi方法初始化界面
        self.mainWindows = mainWindows
        self.mapCanvas = self.mainWindows.canvas
        self.layer : QgsVectorLayer = layer
        #self.center()
     
        self.layerCache = QgsVectorLayerCache(self.layer, self.layer.featureCount())
        self.tableModel = QgsAttributeTableModel(self.layerCache)      
        self.tableModel.loadLayer()
        self.tableFilterModel = QgsAttributeTableFilterModel(self.mapCanvas, self.tableModel, self.tableModel) 
        self.tableView = QgsAttributeTableView(self) 
        self.tableView.setModel(self.tableFilterModel)
        self.scrollArea.setWidget(self.tableView)
        self.label.setText(f'共计要素：{self.tableModel.rowCount()}个') 

        # 在这里添加你的逻辑代码
        from os.path import join
        from DeeplearningSystem import base_dir
        png = join(base_dir, 'settings/icon', 'VectorEditor_BatchAttributeEdit.png') 
        icon = QIcon()
        icon.addPixmap(QPixmap(png), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)
        self.setWindowFlags(self.windowFlags() & ~(Qt.WindowContextHelpButtonHint))
        self.setWindowTitle("属性表 - " + self.layer.name())
        # 按键
        self.toolButton_AttributeSelect.clicked.connect(self.AttributeSelect)
        self.toolButton_ClearSelect.clicked.connect(self.ClearSelect)
        self.toolButton_FieldCalculator.clicked.connect(self.FieldCalculator)
        # 事件
        self.tableView.doubleClicked.connect(self.double_click)# 连接双击信号到槽函数  

    def double_click(self,index):
        # 获取当前选中的行
        #row = index.row()
        # 获取当前行的属性值
        #layer = self.tableView.layer()
        #feature = layer.getFeature(row)
        if not self.layer.isEditable():
            show_info_message(self.tableView, "信息", "如要编辑属性，请打开图层编辑状态！")

    def AttributeSelect(self):   
        if not self.layer.isValid():
            show_info_message(self, "图层错误", "当前图层无效")
            return    
        from dialog.AttributeSelectDialog import AttributeSelectDialog
        self.attributeQueryDialog = AttributeSelectDialog(self)
        self.attributeQueryDialog.attributeListModel.setStringList(self.layer.fields().names())
        result = self.attributeQueryDialog.exec_()
        if result == QDialog.Accepted:          
            """执行自定义查询"""
            query_text = self.attributeQueryDialog.textEdit_Code.toPlainText()          
            if not query_text.strip():
                show_info_message(self, "输入错误", "请输入有效的查询表达式")
                return
            self.toolButton_ClearSelect.setEnabled(True)    
            # 设置过滤模式
            self.tableFilterModel.setFilterMode(QgsAttributeTableFilterModel.ShowSelected)
            # 应用过滤条件
            request = QgsFeatureRequest().setFilterExpression(query_text)
            ids = [f.id() for f in self.layer.getFeatures(request)]  # 提取所有匹配要素的 ID
            self.tableFilterModel.setFilteredFeatures(ids)
            
            # 更新显示           
            self.tableView.viewport().update()
            self.label.setText(f"找到 {len(ids)} 条匹配记录")            
            # 如果有匹配结果，滚动到第一条记录
            if len(ids) > 0:
                self.tableView.scrollToTop()
        elif result == QDialog.Rejected:
            print("User clicked Close or pressed Escape")
   
    def ClearSelect(self):
        """重置显示所有数据"""
        # 设置过滤模式（显示过滤结果）
        self.tableFilterModel.setFilterMode(QgsAttributeTableFilterModel.ShowAll)      
        # 刷新视图
        self.tableView.viewport().update()
        self.label.setText(f'共计要素：{self.tableModel.rowCount()}个')
        self.toolButton_ClearSelect.setEnabled(False)

    def FieldCalculator(self):
        if not self.layer.isValid():
            show_info_message(self, "图层错误", "当前图层无效")
            return    
        from dialog.FieldCalculatorDialog import FieldCalculatorDialog
        self.fieldCalculatorDialog = FieldCalculatorDialog(self)
        self.fieldCalculatorDialog.attributeListModel.setStringList(self.layer.fields().names())
        result = self.fieldCalculatorDialog.exec_()
        if result == QDialog.Accepted:          
            """执行自定义查询"""
            query_text = self.fieldCalculatorDialog.textEdit_Code.toPlainText()                    
            if "=" in query_text and not query_text.strip().startswith("'") and not query_text.strip().startswith('"'):
                # 如果用户误输入了比较表达式而非赋值表达式，提示修正
                show_info_message(self, "输入错误", "请直接输入要赋的值或完整表达式，如：412702 或 if(条件,值,默认值)")
                return
            try:
                if not self.layer.isEditable():
                    self.layer.startEditing()  # 确保进入编辑状态
                
                # 添加/获取字段
                selected_indexes = self.fieldCalculatorDialog.listView_AttributeList.selectedIndexes()
                if not selected_indexes:
                    show_info_message(self, "错误", "未选择目标字段")
                    return
                selected_field = selected_indexes[0].data() 
                field_index = self.layer.fields().indexFromName(selected_field)
                # 添加调试信息
                print(f"Editing mode: {self.layer.isEditable()}")
                print(f"Selected field: {selected_field}, index: {field_index}")
                # 准备表达式
                expression = QgsExpression(query_text)
                if expression.hasParserError():
                    show_info_message(self, "表达式错误", f"表达式解析错误: {expression.parserErrorString()}")
                    return
                # 在评估表达式前添加
                print(f"Expression text: '{query_text}'")
                print(f"Parser error: {expression.parserErrorString()}")
                context = QgsExpressionContext()
                context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(self.layer))
                
                # 遍历要素并更新
                updated_count = 0
                for i, feature in enumerate(self.layer.getFeatures()):                  
                    context.setFeature(feature)
                    value = expression.evaluate(context)
                    print(f"Feature {i}: Original value: {feature[selected_field]}, New value: {value}")
                    if expression.hasEvalError():
                        raise ValueError(f"表达式执行错误: {expression.evalErrorString()}")
                    # 转换类型以匹配字段类型
                    field_type = self.layer.fields().field(field_index).type()
                    converted_value = self.convert_value_to_field_type(value, field_index, field_type)
                    print(f"Converted value: {converted_value}")
                    # 检查转换后的值是否有效
                    if converted_value is None:
                        print(f"Warning: Converted value is None for feature {feature.id()}")
                    
                    success = self.layer.changeAttributeValue(feature.id(), field_index, converted_value)
                    if not success:
                        print(f"Failed to update feature {feature.id()}")
                    else:
                        updated_count += 1
                print(f"Layer is valid: {self.layer.isValid()}")
                print(f"Layer is editable: {self.layer.isEditable()}")
                # 检查编辑缓冲区和更改状态
                edit_buffer = self.layer.editBuffer()
                if edit_buffer:
                    print(f"Changed attributes: {edit_buffer.changedAttributeValues()}")
                else:
                    print("Warning: No edit buffer exists after starting edit mode")                  
                # 提交更改
                if not self.layer.commitChanges():
                    errors = self.layer.commitErrors()
                    raise Exception(f"提交更改失败: {errors if errors else '未知错误'}")
                else:
                    print("Changes committed successfully")
                    
                show_info_message(self, "成功", f"成功更新 {updated_count} 条记录的字段 [{selected_field}]")
                self.tableView.viewport().update()
                self.label.setText(f"字段计算完成 - 更新了 {updated_count} 条记录")    
            except Exception as e:
                self.layer.rollBack()
                show_info_message(self, "计算错误", f"字段计算失败: {str(e)}")
                return                     
        elif result == QDialog.Rejected:
            print("User clicked Close or pressed Escape")

    def convert_value_to_field_type(self, value, field_index, field_type):
        """将值转换为匹配字段类型的适当格式"""
        from qgis.PyQt.QtCore import QVariant
        
        # 获取字段定义以检查是否允许NULL
        field = self.layer.fields().at(field_index)
        allow_null = field.typeName().lower() in ('string', 'text') or field.length() == 0
        
        if value is None:
            return None if allow_null else self.get_default_value(field_type)
        
        try:
            if field_type == QVariant.Int:
                return int(value) if str(value).strip() not in ('', 'NULL') else (None if allow_null else 0)
            elif field_type == QVariant.Double:
                return float(value) if str(value).strip() not in ('', 'NULL') else (None if allow_null else 0.0)
            elif field_type == QVariant.String:
                return str(value) if value is not None else ("" if not allow_null else None)
            # 其他类型处理...
        except Exception as e:
            print(f"Conversion error: {str(e)}")
            return None if allow_null else self.get_default_value(field_type)

    def get_default_value(self, field_type):
        """返回字段类型的默认值"""
        from qgis.PyQt.QtCore import QVariant
        if field_type == QVariant.Int:
            return 0
        elif field_type == QVariant.Double:
            return 0.0
        elif field_type == QVariant.String:
            return ""
        # 其他类型...
        return None

    def center(self):
        # 获取屏幕的尺寸信息
        screen = QDesktopWidget().screenGeometry()
        # 获取窗口的尺寸信息
        size = self.geometry()
        # 将窗口移动到指定位置
        self.move(int((screen.width() - size.width()) / 2), int((screen.height() - size.height()) / 2))