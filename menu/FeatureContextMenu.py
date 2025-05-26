from qgis.core import edit, QgsProject, QgsVectorLayer, QgsMapLayer, QgsMapLayerType, QgsFeature, QgsCoordinateTransform, QgsGeometry,QgsVectorDataProvider,QgsWkbTypes
from qgis.gui import QgsMapToolIdentifyFeature, QgsRubberBand
from PyQt5.QtWidgets import QAction, QMenu
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QCursor, QColor
from tools.CommonTool import show_info_message


class SelectToolWithMenu(QgsMapToolIdentifyFeature):
    def __init__(self, canvas, parent):
        super().__init__(canvas)
        self.parent = parent
        self.rubber_band = QgsRubberBand(self.canvas(), QgsWkbTypes.PolygonGeometry)
        self.rubber_band.setColor(QColor(255, 0, 0, 50))  # 降低透明度提升性能
        from os.path import join
        from DeeplearningSystem import base_dir
        self.cursor = QCursor(QPixmap(join(base_dir, 'settings/icon', 'select.cur')), hotX=0, hotY=0)  # hotX/Y指定热点位置
        self.move_cursor = QCursor(QPixmap(join(base_dir, 'settings/icon', 'select_move.cur')),hotX=0, hotY=0)
        self.setCursor(self.cursor)
        self.last_identified_features = []  # 存储最后一次识别的要素
        self.is_moving_features = False     # 是否处于平移模式
        self.start_move_pos = None         # 平移起始位置
        self.original_geometries = {}       # 存储要素原始几何图形
        self.original_rubber = {}       # 存储橡皮筋原始几何图形
        self.moving_features = []           # 正在平移的要素
        self.moving_layer = None           # 正在平移的要素所在图层
        self.dragging = False  # 新增：跟踪是否正在拖动
        self._transform_cache = None  # 新增转换缓存
        self._last_update_time = 0
        
    def canvasReleaseEvent(self, event):
        # 如果在平移模式下释放鼠标
        if self.is_moving_features and event.button() == Qt.LeftButton:
            if self.dragging:  # 只有实际拖动后才完成移动               
                try:
                    # 转换为地图坐标偏移量
                    current_map_point = self.toMapCoordinates(event.pos())
                    last_map_point = self.toMapCoordinates(self.start_move_pos)
                    
                    map_dx = current_map_point.x() - last_map_point.x()
                    map_dy = current_map_point.y() - last_map_point.y()
                    
                    with edit(self.moving_layer):
                        for feature in self.moving_features:
                            original_geom = self.original_geometries.get(feature.id())
                            if original_geom:
                                new_geom = QgsGeometry(original_geom)
                                if new_geom.translate(map_dx, map_dy) == 0:
                                    self.moving_layer.changeGeometry(feature.id(), new_geom)              
                    self.canvas().refresh()                   
                except Exception as e:
                    print(f"移动要素时出错: {str(e)}")
                    self.cancelMovingFeatures()

                self.finishMovingFeatures()
            else:  # 如果只是点击没有拖动，则取消移动
                self.cancelMovingFeatures()
            self.dragging = False
            return
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
    
    def canvasMoveEvent(self, event):
        if self.is_moving_features and self.dragging:
            self.moveFeatures(event.pos())
            #current_time = time.time()
            #if current_time - self._last_update_time > 0.05:  # 保持20FPS限制
            #    self.moveFeatures(event.pos())
            #    self._last_update_time = current_time
            return
        super().canvasMoveEvent(event)

    def canvasPressEvent(self, event):
        if event.button() == Qt.LeftButton:
            layer = self.parent.tocView.currentLayer()
            if layer and layer.type() == QgsMapLayer.VectorLayer:
                # 检查是否已有选中要素
                if layer.selectedFeatureCount() > 0:
                    self.startMovingFeatures()
                    self.dragging = True
                    self.start_move_pos = event.pos()
                    self.last_pos = event.pos()
                    return  # 阻止父类处理
        
        super().canvasPressEvent(event)
            
    def keyPressEvent(self, event):
        # 按ESC键取消平移操作
        if event.key() == Qt.Key_Escape and self.is_moving_features:
            self.cancelMovingFeatures()
            
        super().keyPressEvent(event)

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
            # 平移功能（当有选中要素时）
            #move_action = QAction("平移要素", menu)
            #move_action.triggered.connect(self.startMovingFeatures)
            #menu.addAction(move_action)
        
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
    
    def startMovingFeatures(self):
        layer = self.parent.tocView.currentLayer()
        if not layer or layer.type() != QgsMapLayer.VectorLayer:
            return
        # 检查是否有选中要素
        self.moving_features = list(layer.selectedFeatures())
        if not self.moving_features:
            return        
        # 初始化移动状态
        self.moving_layer = layer
        # 深拷贝原始几何图形
        self.original_geometries = {
            f.id(): QgsGeometry(f.geometry().constGet().clone()) 
            for f in self.moving_features 
            if f.hasGeometry()
        }
        self.original_rubber = {
            f.id(): QgsGeometry(f.geometry().constGet().clone()) 
            for f in self.moving_features 
            if f.hasGeometry()
        }
        # 初始化橡皮筋
        self.rubber_band.reset(QgsWkbTypes.PolygonGeometry)
        for fid, geom in self.original_geometries.items():
            self.rubber_band.addGeometry(geom, layer, True)

        self.is_moving_features = True
        self.dragging = False
        
        # 设置移动光标      
        self.setCursor(self.move_cursor)
        self.parent.progress_bar.setText("平移模式: 拖动鼠标移动要素，按ESC取消")     

    def moveFeatures(self, pos):
        if not (self.is_moving_features and self.dragging and self.moving_layer):
            return
            
        try:          
            # 转换为地图坐标偏移量
            current_map_point = self.toMapCoordinates(pos)
            last_map_point = self.toMapCoordinates(self.last_pos)
            
            map_dx = current_map_point.x() - last_map_point.x()
            map_dy = current_map_point.y() - last_map_point.y()
            
            self.rubber_band.reset(QgsWkbTypes.PolygonGeometry)
            for feature in self.moving_features:
                original_geom = self.original_rubber.get(feature.id())
                if original_geom:
                    # 创建新的几何图形
                    new_geom = QgsGeometry(original_geom)
                    if new_geom.translate(map_dx, map_dy) == 0:  # 0表示成功
                        geom_copy = QgsGeometry(new_geom.constGet().clone())
                        self.original_rubber[feature.id()] = geom_copy
                        # 更新橡皮筋
                        self.rubber_band.addGeometry(new_geom, self.moving_layer,True)
            self.last_pos = pos
            self.canvas().refresh()
            
        except Exception as e:
            print(f"移动要素时出错: {str(e)}")
            self.cancelMovingFeatures()

    def finishMovingFeatures(self):
        """完成要素平移"""
        if hasattr(self, 'rubber_band'):
            self.rubber_band.reset()      
        if hasattr(self, '_transform_cache'):
            self._transform_cache = None    
        self.is_moving_features = False
        self.start_move_pos = None
        self.last_pos = None
        self.original_geometries = {}
        self.moving_features = []
        self.setCursor(self.cursor)
        self.parent.progress_bar.setText("要素平移完成")
        if self.moving_layer:
            self.moving_layer.triggerRepaint()
            self.moving_layer = None

    def cancelMovingFeatures(self):
        """取消要素平移"""
        if hasattr(self, 'rubber_band'):
            self.rubber_band.reset()
        if not self.is_moving_features or not self.moving_layer:
            return
            
        # 恢复原始几何图形
        if self.moving_layer.isEditable():
            for fid, geom in self.original_geometries.items():
                self.moving_layer.changeGeometry(fid, geom)
        
        self.is_moving_features = False
        self.start_move_pos = None
        self.last_pos = None
        self.original_geometries = {}
        self.moving_features = []
        self.setCursor(Qt.ArrowCursor)
        self.moving_layer.triggerRepaint()
        self.parent.progress_bar.setText("已取消要素平移")
        self.moving_layer = None

    def deactivate(self):
        if hasattr(self, 'rubber_band'):
            self.rubber_band.reset()
        self.cancelMovingFeatures()
        super().deactivate()

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