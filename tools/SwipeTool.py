
from qgis.PyQt.QtCore import Qt, QRectF
from qgis.core import QgsProject, QgsMapSettings, QgsMapRendererParallelJob
from qgis.gui import QgsMapTool, QgsMapCanvasItem
from qgis.PyQt.QtWidgets import QAction, QComboBox, QToolBar
from PyQt5.QtGui import QColor, QPen, QCursor, QIcon, QPixmap
from os.path import join
from DeeplearningSystem import base_dir

class SwipeMapTool(QgsMapTool):
    def __init__(self, canvas, layer_combo):
        super().__init__(canvas)
        self.canvas = canvas
        self.layer_combo = layer_combo
        self.swipe_item = SwipeCanvasItem(canvas)
        self.is_swiping = False
        self.current_direction = None
        
        # 设置光标
        self.cursorSV = QCursor(QPixmap(join(base_dir, 'settings/icon/split_v.png')))
        self.cursorSH = QCursor(QPixmap(join(base_dir, 'settings/icon/split_h.png')))
        self.cursorUP = QCursor(QPixmap(join(base_dir, 'settings/icon/up.png')))
        self.cursorDOWN = QCursor(QPixmap(join(base_dir, 'settings/icon/down.png')))
        self.cursorLEFT = QCursor(QPixmap(join(base_dir, 'settings/icon/left.png')))
        self.cursorRIGHT = QCursor(QPixmap(join(base_dir, 'settings/icon/right.png')))

        self.default_cursor = QCursor(Qt.CrossCursor)
        self.h_cursor = QCursor(Qt.SplitHCursor)
        self.v_cursor = QCursor(Qt.SplitVCursor)
        
        # 监听图层变化
        QgsProject.instance().layersAdded.connect(self._update_layers)
        QgsProject.instance().layersRemoved.connect(self._update_layers)
        layer_combo.currentIndexChanged.connect(self._update_layers)
    
    def _update_layers(self):
        """更新要对比的图层"""
        current_layer_name = self.layer_combo.currentText()
        all_layers = QgsProject.instance().mapLayers().values()
        
        layers = [
            layer for layer in all_layers 
            if layer.name() != current_layer_name
        ]
        
        self.swipe_item.set_layers(layers)
    
    def activate(self):
        self.canvas.setCursor(self.default_cursor)
        self._update_layers()
        self.swipe_item.show()
        
    def deactivate(self):
        if hasattr(self, 'swipe_item') and self.swipe_item:
            try:
                self.swipe_item.clear_position()
                self.swipe_item.hide()
            except RuntimeError:  # 如果 canvas 已被销毁
                pass
    
    def canvasPressEvent(self, event):
        pos = event.pos()
        rect = self.canvas.rect()
        
        # 根据点击位置确定卷帘方向
        if pos.x() < rect.width() * 0.33:  # 左侧1/3区域
            self.current_direction = 'left'
            self.canvas.setCursor(self.cursorRIGHT)
        elif pos.x() > rect.width() * 0.66:  # 右侧1/3区域
            self.current_direction = 'right'
            self.canvas.setCursor(self.cursorLEFT)
        elif pos.y() < rect.height() * 0.33:  # 上方1/3区域
            self.current_direction = 'top'
            self.canvas.setCursor(self.cursorDOWN)
        else:  # 下方1/3区域
            self.current_direction = 'bottom'
            self.canvas.setCursor(self.cursorUP)
        
        self.is_swiping = True
        self.swipe_item.set_position(pos, self.current_direction)
    
    def canvasReleaseEvent(self, event):
        self.is_swiping = False
        self.canvas.setCursor(self.default_cursor)
        self.swipe_item.clear_position()
    
    def canvasMoveEvent(self, event):
        if not self.is_swiping:
            # 更新光标样式
            pos = event.pos()
            rect = self.canvas.rect()
            
            if pos.x() < rect.width() * 0.33:
                self.canvas.setCursor(self.cursorSV)
            elif pos.x() > rect.width() * 0.66:
                self.canvas.setCursor(self.cursorSV)
            elif pos.y() < rect.height() * 0.33:
                self.canvas.setCursor(self.cursorSH)
            else:
                self.canvas.setCursor(self.cursorSH)
            return
            
        # 更新卷帘位置
        self.swipe_item.set_position(event.pos(), self.current_direction)
class SwipeCanvasItem(QgsMapCanvasItem):
    def __init__(self, canvas):
        super().__init__(canvas)
        self.canvas = canvas
        self.image = None
        self.position = None
        self.direction = None
        self.layers = []
        
        self.line_pen = QPen(QColor(0, 0, 255))
        self.line_pen.setWidth(2)
        self.line_pen.setStyle(Qt.DashLine)
    
    def set_layers(self, layers):
        self.layers = layers
        self._render_layers()
    
    def set_position(self, pos, direction):
        self.position = pos
        self.direction = direction
        self.update()
        self.canvas.refresh()
    
    def clear_position(self):
        if not self.canvas:
            return
            
        self.position = None
        self.update()
        try:
            self.canvas.refresh()
        except RuntimeError:
            pass
    
    def _render_layers(self):
        if not self.layers:
            return
            
        settings = QgsMapSettings(self.canvas.mapSettings())
        settings.setLayers(self.layers)
        
        self._render_job = QgsMapRendererParallelJob(settings)
        
        def rendering_finished():
            self.image = self._render_job.renderedImage()
            self.update()
            self.canvas.refresh()
        
        self._render_job.finished.connect(rendering_finished)
        self._render_job.start()
    
    def paint(self, painter, *args):
        if not self.position or not self.image or not self.direction:
            return
            
        canvas_size = self.canvas.size()
        width = canvas_size.width()
        height = canvas_size.height()
        
        if self.direction in ['left', 'right']:
            split_pos = max(0, min(int(self.position.x()), width))
            
            # 绘制分割线
            painter.setPen(self.line_pen)
            painter.drawLine(split_pos, 0, split_pos, height)
            
            # 根据方向绘制对比图层
            if self.direction == 'left':
                # 从左侧卷帘，显示右侧图像
                painter.drawImage(
                    QRectF(0, 0, split_pos, height),
                    self.image,
                    QRectF(0, 0, split_pos, height))
            else:
                # 从右侧卷帘，显示左侧图像
                painter.drawImage(
                    QRectF(split_pos, 0, width - split_pos, height),
                    self.image,
                    QRectF(split_pos, 0, width - split_pos, height))
                
        elif self.direction in ['top', 'bottom']:
            split_pos = max(0, min(int(self.position.y()), height))
            
            # 绘制分割线
            painter.setPen(self.line_pen)
            painter.drawLine(0, split_pos, width, split_pos)
            
            # 根据方向绘制对比图层
            if self.direction == 'top':
                # 从上方卷帘，显示下方图像
                painter.drawImage(
                    QRectF(0, 0, width, split_pos),
                    self.image,
                    QRectF(0, 0, width, split_pos))
            else:
                # 从下方卷帘，显示上方图像
                painter.drawImage(
                    QRectF(0, split_pos, width, height - split_pos),
                    self.image,
                    QRectF(0, split_pos, width, height - split_pos))
    
    def boundingRect(self):
        size = self.canvas.size()
        return QRectF(0, 0, size.width(), size.height())
class SwipeToolController:
    _instance = None  # 单例模式

    def __new__(cls, mainWindow):
        if not cls._instance:
            cls._instance = super(SwipeToolController, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, mainWindow):
        if not self._initialized:
            self.mainWindow = mainWindow
            self.canvas = mainWindow.canvas
            
            # 1. 先创建 UI 元素（确保 layer_combo 存在）
            self._create_ui()
            
            # 2. 再填充图层下拉框
            self._populate_layer_combo()
            
            # 3. 最后更新图层
            self._update_layers()
            
            self._initialized = True

    def _create_ui(self):
        """创建工具栏和UI元素"""
        # 检查是否已经存在工具栏
        existing_toolbars = [tb for tb in self.mainWindow.findChildren(QToolBar) 
                           if tb.windowTitle() == "卷帘工具"]
        if existing_toolbars:
            self.toolbar = existing_toolbars[0]
            return
        
        # 创建图层选择器
        self.layer_combo = QComboBox()
        self.layer_combo.setMinimumWidth(150)
        
        # 创建卷帘工具
        self.swipe_tool = SwipeMapTool(self.canvas, self.layer_combo)
        
        # 创建工具栏动作
        self.swipe_action = QAction("卷帘工具", self.mainWindow)
        self._set_icon()
        self.swipe_action.setCheckable(True)
        self.swipe_action.toggled.connect(self._toggle_swipe_tool)
        
        # 创建工具栏
        self.toolbar = self.mainWindow.addToolBar("卷帘工具")
        self.toolbar.addWidget(self.layer_combo)
        self.toolbar.addAction(self.swipe_action)
        
        # 监听图层变化
        QgsProject.instance().layersAdded.connect(self._populate_layer_combo)
        QgsProject.instance().layersRemoved.connect(self._populate_layer_combo)

    def _populate_layer_combo(self):
        """填充图层下拉框"""
        if not hasattr(self, 'layer_combo'):  # 确保 layer_combo 存在
            return
            
        self.layer_combo.clear()
        all_layers = QgsProject.instance().mapLayers().values()
        for layer in all_layers:
            self.layer_combo.addItem(layer.name(), layer)

    def _update_layers(self):
        """手动触发图层更新"""
        if hasattr(self, 'swipe_tool'):  # 确保 swipe_tool 存在
            self.swipe_tool._update_layers()

    def _toggle_swipe_tool(self, checked):
        """切换卷帘工具状态"""
        if checked:
            self.canvas.setMapTool(self.swipe_tool)
        else:
            self.canvas.unsetMapTool(self.swipe_tool)

    def _set_icon(self):
        """设置图标"""     
        png = join(base_dir, 'settings/icon', 'Swip.png') 
        self.swipe_action.setIcon(QIcon(png))

    def unload(self):
        """清理资源"""
        if hasattr(self, 'swipe_tool'):
            self.swipe_tool.deactivate()
            self.canvas.unsetMapTool(self.swipe_tool)
            del self.swipe_tool

# 使用方法
# 在QGIS Python控制台或插件中调用:
# swipe_controller = SwipeToolController(mainWindow)