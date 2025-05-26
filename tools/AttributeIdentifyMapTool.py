from qgis.gui import QgsAttributeEditorContext, QgsMapToolIdentifyFeature, QgsAttributeDialog,QgsGui
from qgis.core import QgsProject, QgsRectangle, QgsWkbTypes, QgsMapLayer, edit
from PyQt5.QtWidgets import QMenu, QAction, QInputDialog, QFileDialog
from PyQt5.QtCore import Qt, QPoint
from tools.CommonTool import show_info_message

class AttributeIdentifyMapTool(QgsMapToolIdentifyFeature):
    def __init__(self, canvas, parent):
        super().__init__(canvas)
        self.parent = parent
        self.canvas = canvas
        self.selected_feature = None
        self.selected_layer = None
        from os.path import join
        from DeeplearningSystem import base_dir
        from PyQt5.QtGui import QPixmap, QCursor
        self.cursor = QCursor(QPixmap(join(base_dir, 'settings/icon', 'FeatureIdentify.cur')), hotX=0, hotY=0)
        self.setCursor(self.cursor)      
        QgsGui.editorWidgetRegistry().initEditors(self.canvas)
    
    def canvasReleaseEvent(self, event):
        if event.button() == Qt.RightButton and self.selected_feature:
            self.show_context_menu(event.pos())
        elif event.button() == Qt.LeftButton:
            # 左键点击识别要素
            self.selected_feature = None
            self.selected_layer = None
            layer = self.parent.tocView.currentLayer()
                
            # 识别要素
            results = self.identify(event.x(), event.y(), [layer], self.TopDownAll)
            
            if results:
                self.selected_layer = results[0].mLayer
                self.selected_feature = results[0].mFeature

            self.show_attributes(self.selected_layer,self.selected_feature)
              
    def show_attributes(self, layer, feature):
        """显示要素属性表单"""
        if not layer or not feature:
            return
        
        try:
            # 方法1：使用QgsAttributeDialog（推荐）
            self.dialog:QgsAttributeDialog = QgsAttributeDialog(layer, feature, True, self.parent,False)
            self.dialog.setWindowFlags(self.dialog.windowFlags() & ~(Qt.WindowContextHelpButtonHint))
            self.dialog.setWindowTitle(f"要素属性 - ID: {feature.id()}")
            self.dialog.show()
            
        except Exception as e:
            print(f"显示属性表单出错: {str(e)}")
            # 回退到简单显示
            attributes = {field.name(): value for field, value in zip(layer.fields(), feature.attributes())}
            show_info_message(self.parent, "要素属性", str(attributes))  

# 使用示例
'''
def init_feature_menu_tool():
    canvas = iface.mapCanvas()
    tool = FeatureContextMenuMapTool(canvas)
    canvas.setMapTool(tool)
    return tool

# 初始化工具
feature_menu_tool = init_feature_menu_tool()
'''