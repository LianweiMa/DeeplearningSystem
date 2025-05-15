from qgis.gui import QgsMapToolIdentify, QgsMapToolIdentifyFeature, QgsAttributeForm
from qgis.core import QgsProject, QgsRectangle, QgsWkbTypes, QgsMapLayer, edit
from PyQt5.QtWidgets import QMenu, QAction, QInputDialog, QFileDialog
from PyQt5.QtCore import Qt, QPoint

class FeatureContextMenuMapTool(QgsMapToolIdentify):
    def __init__(self, canvas):
        super().__init__(canvas)
        self.canvas = canvas
        self.selected_feature = None
        self.selected_layer = None
    
    def canvasReleaseEvent(self, event):
        if event.button() == Qt.RightButton and self.selected_feature:
            self.show_context_menu(event.pos())
        elif event.button() == Qt.LeftButton:
            # 左键点击识别要素
            self.selected_feature = None
            self.selected_layer = None
            
            # 在所有可见的矢量图层中识别要素
            layers = [layer for layer in QgsProject.instance().mapLayers().values() 
                     if layer.type() == QgsMapLayer.VectorLayer and layer.isSpatial()]
            
            if not layers:
                return
                
            # 识别要素
            results = self.identify(event.x(), event.y(), layers, self.TopDownAll)
            
            if results:
                self.selected_layer = results[0].mLayer
                self.selected_feature = results[0].mFeature
    
    def show_context_menu(self, pos):
        if not self.selected_feature or not self.selected_layer:
            return
            
        menu = QMenu()
        layer = self.selected_layer
        feature = self.selected_feature
        
        # 添加菜单标题
        title_action = QAction(f"{layer.name()} (ID: {feature.id()})", menu)
        title_action.setEnabled(False)
        menu.addAction(title_action)
        menu.addSeparator()
        
        # 1. 基本操作
        zoom_action = QAction("缩放到要素", menu)
        zoom_action.triggered.connect(lambda: self.zoom_to_feature(layer, feature))
        menu.addAction(zoom_action)
        
        attr_action = QAction("显示属性", menu)
        attr_action.triggered.connect(lambda: self.show_attributes(layer, feature))
        menu.addAction(attr_action)
        
        # 2. 空间分析
        spatial_menu = menu.addMenu("空间分析")
        buffer_action = QAction("创建缓冲区", spatial_menu)
        buffer_action.triggered.connect(lambda: self.create_buffer(layer, feature))
        spatial_menu.addAction(buffer_action)
        
        # 3. 数据操作
        data_menu = menu.addMenu("数据操作")
        export_action = QAction("导出要素", data_menu)
        export_action.triggered.connect(lambda: self.export_feature(layer, feature))
        data_menu.addAction(export_action)
        
        # 4. 编辑操作（如果图层可编辑）
        if layer.isEditable():
            edit_menu = menu.addMenu("编辑")
            delete_action = QAction("删除要素", edit_menu)
            delete_action.triggered.connect(lambda: self.delete_feature(layer, feature))
            edit_menu.addAction(delete_action)
            
            move_action = QAction("移动要素", edit_menu)
            move_action.triggered.connect(lambda: self.start_move_feature(layer, feature))
            edit_menu.addAction(move_action)
        
        menu.exec_(self.canvas.mapToGlobal(pos))
    
    def zoom_to_feature(self, layer, feature):
        if feature.hasGeometry():
            self.canvas.setExtent(feature.geometry().boundingBox())
            self.canvas.refresh()
    
    def show_attributes(self, layer, feature):
        self.form = QgsAttributeForm(layer, feature)
        self.form.show()
    
    def create_buffer(self, layer, feature):
        if not feature.hasGeometry():
            return
            
        distance, ok = QInputDialog.getDouble(
            None, "创建缓冲区", "缓冲距离（米）:", 100.0, 0.1, 10000.0, 1
        )
        if ok:
            buffer = feature.geometry().buffer(distance, 5)
            # 这里可以添加创建缓冲区的实际代码
    
    def export_feature(self, layer, feature):
        filename, _ = QFileDialog.getSaveFileName(
            None, "导出要素", "", "GeoJSON (*.geojson);;Shapefile (*.shp)"
        )
        if filename:
            # 这里可以添加导出要素的实际代码
            print(f"导出要素到 {filename}")
    
    def delete_feature(self, layer, feature):
        layer.deleteFeature(feature.id())
        layer.triggerRepaint()
        self.selected_feature = None
    
    def start_move_feature(self, layer, feature):
        # 这里可以添加移动要素的代码
        print(f"准备移动要素 {feature.id()}")

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