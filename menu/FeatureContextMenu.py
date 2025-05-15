from qgis.core import edit, QgsProject, QgsVectorLayer, QgsMapLayer, QgsMapLayerType, QgsFeature, QgsCoordinateTransform
from qgis.gui import QgsMapToolIdentifyFeature
from PyQt5.QtWidgets import QAction, QMenu, QApplication
from PyQt5.QtCore import Qt
from tools.CommonTool import show_info_message

class SelectToolWithMenu(QgsMapToolIdentifyFeature):
    def __init__(self, canvas, parent):
        super().__init__(canvas)
        self.parent = parent
        self.setCursor(Qt.ArrowCursor)
        self.last_identified_features = []  # 存储最后一次识别的要素
    
    def canvasReleaseEvent(self, event):
        # 右键点击显示菜单
        if event.button() == Qt.RightButton:
            layer = self.parent.tocView.currentLayer()
            if layer and layer.type() == QgsMapLayer.VectorLayer:
                # 识别点击位置的所有要素
                self.last_identified_features = self.identify(
                    event.x(), event.y(), 
                    [layer], 
                    QgsMapToolIdentifyFeature.TopDownAll
                )
                self.showContextMenu(event.pos())
            return
        
        # 左键点击保持原有选择逻辑
        super().canvasReleaseEvent(event)
    
    def showContextMenu(self, pos):
        menu = QMenu()
        
        # 选择要素菜单（仅在点击到要素时显示）
        if self.last_identified_features:
            select_menu = menu.addMenu("选择要素")
            
            # 添加全选选项，并显示要素数量
            select_all_action = QAction(f"全选（共{len(self.last_identified_features)}个）", menu)
            select_all_action.triggered.connect(self.selectAllIdentified)
            select_menu.addAction(select_all_action)
            
            # 添加分隔线
            select_menu.addSeparator()
            
            # 为每个识别到的要素添加单独选择选项
            for i, identified_feature in enumerate(self.last_identified_features, 1):
                feature = identified_feature.mFeature
                layer = identified_feature.mLayer
                
                # 获取要素的显示名称（如果有的话），否则使用要素ID
                display_name = f"要素 {feature.id()}"
                action = QAction(f"{display_name}", menu)
                action.setData((layer, feature.id()))  # 存储图层和要素ID
                action.triggered.connect(lambda checked, a=action: self.selectSingleFeature(a))
                select_menu.addAction(action)
        
        # 如果没有识别到要素，添加一个禁用的菜单项
        else:
            no_selection_action = QAction("无要素可选择", menu)
            no_selection_action.setEnabled(False)
            menu.addAction(no_selection_action)
        
        # 复制功能（当有选中要素时）
        layer = self.parent.tocView.currentLayer()
        if layer and layer.selectedFeatureCount() > 0:
            menu.addSeparator()
            copy_action = QAction("复制要素", menu)
            copy_action.triggered.connect(self.copyFeatures)
            menu.addAction(copy_action)
        
        # 粘贴功能（当有复制内容且当前是矢量图层时）
        if self.parent.copied_features and layer and layer.type() == QgsMapLayer.VectorLayer:
            paste_action = QAction("粘贴要素", menu)
            paste_action.triggered.connect(lambda: self.pasteFeatures(pos))
            menu.addAction(paste_action)
        
        # 删除功能（当有选中要素时）
        if layer and layer.selectedFeatureCount() > 0:
            menu.addSeparator()
            delete_action = QAction("删除选中要素", menu)
            delete_action.triggered.connect(self.deleteSelectedFeatures)
            menu.addAction(delete_action)
        
        # 缩放功能（当有选中要素时）
        if layer and layer.selectedFeatureCount() > 0:
            zoom_action = QAction("缩放至选中要素", menu)
            zoom_action.triggered.connect(self.zoomToSelected)
            menu.addAction(zoom_action)
        
        # 显示菜单
        menu.exec_(self.canvas().mapToGlobal(pos))
    
    def selectAllIdentified(self):
        """全选所有识别到的要素"""
        if not self.last_identified_features:
            return
        
        # 清除当前选择
        layer = self.last_identified_features[0].mLayer
        layer.removeSelection()
        
        # 选择所有识别到的要素
        feature_ids = [f.mFeature.id() for f in self.last_identified_features]
        layer.select(feature_ids)
        
        # 刷新画布
        self.canvas().refresh()
        self.parent.progress_bar.setText(f"已选择 {len(feature_ids)} 个要素")
    
    def selectSingleFeature(self, action):
        """选择单个要素"""
        layer, feature_id = action.data()
        if layer and feature_id:
            # 清除当前选择
            layer.removeSelection()
            
            # 选择指定的要素
            layer.select(feature_id)
            
            # 刷新画布
            self.canvas().refresh()
            self.parent.progress_bar.setText("已选择 1 个要素")
    
    def copyFeatures(self):
        """复制当前选中的要素"""
        layer = self.parent.tocView.currentLayer()
        if layer and layer.selectedFeatureCount() > 0:
            # 存储复制的要素、图层和坐标系
            self.parent.copied_features = [f for f in layer.selectedFeatures()]
            self.parent.copied_layer = layer
            self.parent.copied_crs = layer.crs()
            
            # 显示反馈信息
            self.parent.progress_bar.setText(f"已复制 {len(self.parent.copied_features)} 个要素") 
    
    def pasteFeatures(self, pos):
        """按原始坐标粘贴复制的要素"""
        if not self.parent.copied_features or not self.parent.copied_layer:
            return
        
        target_layer = self.parent.tocView.currentLayer()
        if not target_layer or target_layer.type() != QgsMapLayer.VectorLayer:
            return
        
        # 开始编辑会话
        if not target_layer.isEditable():
            show_info_message(self.parent,'提示','选中矢量图层未打开编辑！')
            return
        # 处理每个复制的要素
        for feature in self.parent.copied_features:
            new_feature = QgsFeature(target_layer.fields())
            
            # 复制属性
            for field in target_layer.fields().names():
                if field in feature.fields().names():
                    new_feature[field] = feature[field]
            
            # 处理几何图形
            if feature.hasGeometry():
                geom = feature.geometry()
                
                # 如果坐标系不同，进行坐标转换
                if target_layer.crs() != self.parent.copied_crs:
                    transform = QgsCoordinateTransform(
                        self.parent.copied_crs,
                        target_layer.crs(),
                        QgsProject.instance()
                    )
                    geom.transform(transform)
                
                new_feature.setGeometry(geom)
            
            # 添加新要素
            target_layer.addFeature(new_feature)
        
        # 显示反馈信息
        self.parent.progress_bar.setText(f"已粘贴 {len(self.parent.copied_features)} 个要素")
        # 刷新画布
        target_layer.triggerRepaint()
    
    def deleteSelectedFeatures(self):
        """删除选中的要素"""
        layer = self.parent.tocView.currentLayer()
        if layer and layer.type() == QgsMapLayer.VectorLayer:
            with edit(layer):
                layer.deleteSelectedFeatures()
            layer.removeSelection()
            self.canvas().refresh()
    
    def zoomToSelected(self):
        """缩放至选中要素"""
        layer = self.parent.tocView.currentLayer()
        if layer and layer.selectedFeatureCount() > 0:
            self.canvas().zoomToSelected(layer)