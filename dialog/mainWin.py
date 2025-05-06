# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QDialog,QMainWindow,QHBoxLayout,QFileDialog,QMessageBox,QLabel,QWidget
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtSql import QSqlDatabase, QSqlQuery
from qgis.core import QgsProject, QgsLayerTreeModel, QgsRasterLayer, QgsVectorLayer, QgsMapLayer, QgsCoordinateReferenceSystem, QgsMapLayerType, QgsMapSettings, QgsRectangle, QgsFillSymbol, QgsSingleSymbolRenderer,QgsInvertedPolygonRenderer
from qgis.gui import QgsMapCanvas, QgsLayerTreeView, QgsLayerTreeMapCanvasBridge, QgsMapToolPan, QgsMapToolZoom, QgsMapToolIdentifyFeature
from os.path import basename,join
from tools.CommonTool import show_info_message, show_question_message
from lxml import etree
import sys
import traceback
# XML文件的路径
from menu.ContextMenu import CustomMenuProvider
from ui.MainWinUI import Ui_MainWindow

class mainWin(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(mainWin, self).__init__()
        self.setupUi(self)  # 调用setupUi方法初始化界面
        # 1 最大化窗口
        self.showMaximized()#最大化窗口
        self.title = self.windowTitle()
        # 2 初始化图层树
        self.tocView = QgsLayerTreeView(self)
        self.dockWidgetContents.setContentsMargins(0,0,0,0)
        self.dockWidget.setWidget(self.tocView)
        # 3 初始化地图画布
        self.canvas : QgsMapCanvas = QgsMapCanvas(self)
        self.hl = QHBoxLayout(self.frame)
        self.hl.setContentsMargins(0,0,0,0) #设置周围间距
        self.hl.addWidget(self.canvas)
        # 4 设置图层树风格
        self.project = QgsProject.instance()
        self.model = QgsLayerTreeModel(self.project.layerTreeRoot(),self)
        self.model.setFlag(QgsLayerTreeModel.AllowNodeRename) #允许图层节点重命名
        self.model.setFlag(QgsLayerTreeModel.AllowNodeReorder) #允许图层拖拽排序
        self.model.setFlag(QgsLayerTreeModel.AllowNodeChangeVisibility) #允许改变图层节点可视性
        self.model.setFlag(QgsLayerTreeModel.ShowLegendAsTree) #展示图例
        self.model.setAutoCollapseLegendNodes(10) #当节点数大于等于10时自动折叠
        self.tocView.setModel(self.model)
        # 4 建立图层树与地图画布的桥接
        self.layerTreeBridge = QgsLayerTreeMapCanvasBridge(self.project.layerTreeRoot(),self.canvas,self)
        # 5.0 样本管理栏(右)     
        self.sampleModel = QStandardItemModel() # 创建模型并设置数据
        self.sampleModel.setHorizontalHeaderLabels(["名称", "类别", "误差", "查准", "查全", "IOU", "路径", "编辑"])  # 设置列头标签       
        self.tableView.setModel(self.sampleModel)# 创建表格视图
        self.tableView.resizeColumnsToContents()       
        self.tableView.horizontalHeader().setSectionsClickable(True)# 设置 QTableView 的列头可排序      
        # 5 初始加载影像
        self.firstAddLayer = True
        # 6 允许拖拽文件
        self.setAcceptDrops(True)
        
        # 7 图层树右键菜单创建
        self.rightMenuProv = CustomMenuProvider(self, self.tocView, self.canvas)
        self.tocView.setMenuProvider(self.rightMenuProv)

        # 8.0 提前给予基本CRS
        self.canvas.setDestinationCrs(QgsCoordinateReferenceSystem("EPSG:4326"))

        # 8 状态栏控件
        # 状态栏
        statusBar = self.statusBar()  # 确保状态栏被创建
        statusBar.setSizeGripEnabled(False)  # 禁用大小调整手柄       
        self.progress_bar = QLabel(self)# 创建用于显示处理进度的进度条  
        self.coordinate_label = QLabel('{:<40}'.format(''))# 创建用于显示坐标信息的标签  #x y 坐标状态   
        self.crs_label = QLabel(f"坐标系: {self.canvas.mapSettings().destinationCrs().description()}")
        # 将进度条和标签添加到水平布局中
        layout = QHBoxLayout()
        layout.addWidget(self.progress_bar)
        layout.addStretch(1)  # 添加一个可伸缩的空间，使标签右对齐
        layout.addWidget(self.crs_label)
        layout.addWidget(self.coordinate_label)
        layout.setSpacing(5)  # 设置小部件之间的间距
        layout.setContentsMargins(0, 0, 0, 0)  # 设置布局的边距为0
        # 创建一个容器小部件来包含布局
        container = QWidget()
        container.setLayout(layout)
        # 将容器小部件添加到状态栏中
        statusBar.addWidget(container, 1)  # 1表示伸展因子，使容器占据剩余空间
        # 为容器小部件设置样式表以添加边框
        container.setStyleSheet("""
            QWidget {               
                padding: 5px; /* 设置内边距为5像素 */
            }
        """)
        # 9 error catch
        self.old_hook = sys.excepthook
        sys.excepthook = self.catch_exceptions

        # A 按钮、菜单栏功能
        self.connectFunc()

        # B 初始设置控件
        self.editTempLayer : QgsVectorLayer = None #初始编辑图层为None
        self.pan()# 设置默认功能 
        self.initPrj = True
        self.newProject()# 默认新建工程   
        # 在初始化代码中添加（通常在主窗口初始化时）
        self.project.layersAdded.connect(self.project.setDirty)  # 添加图层时标记为已修改
        self.project.layerWasAdded.connect(self.project.setDirty)
        # 初始化最近文件菜单
        from menu.RecentFilesMenu import RecentFilesMenu
        self.recent_files = RecentFilesMenu(self)

    def connectFunc(self):
       # 菜单绑定事件
        self.actionNewProject.triggered.connect(self.newProject)
        self.actionOpenProject.triggered.connect(self.openProject)
        self.actionCloseProject.triggered.connect(self.closeProject)
        self.actionSaveProject.triggered.connect(self.saveProject)
        self.actionSaveAsProject.triggered.connect(self.saveAsProject)
        self.actionOpenRas.triggered.connect(self.openDialogRas)
        self.actionOpenVec.triggered.connect(self.openDialogVec)

        self.actionZoomIn.triggered.connect(self.zoomIn)
        self.actionZoomOut.triggered.connect(self.zoomOut)
        self.actionPan.triggered.connect(self.pan)
        self.actionFullExtent.triggered.connect(self.fullExtent)
        self.actionSwipe.triggered.connect(self.swipe)
        self.actionLayerView.toggled.connect(self.showLayerView)
        self.actionSamplesView.toggled.connect(self.showSamplesView)
 
        self.actionEditSample.triggered.connect(self.editSample)
        self.actionDrawPolygon.triggered.connect(self.drawPolygon)
        self.actionSelectSample.triggered.connect(self.selectSample)
        self.actionDeleteSample.triggered.connect(self.deleteSample)
        self.actionEvalSample.triggered.connect(self.evalSample)
        self.actionMakeSample.triggered.connect(self.makeSample)
        self.actionSampleStatistic.triggered.connect(self.sampleStatistic)
        self.actionImportSample.triggered.connect(self.importSample)
        self.actionDeleteSamples.triggered.connect(self.deleteSamples)
        self.actionQuerySample.triggered.connect(self.querySample)
        self.actionCloseSamples.triggered.connect(self.closeSamples)

        self.actionModelTrain.triggered.connect(self.modelTrain)
        self.actionStopTrain.triggered.connect(self.stopTrain)
        self.actionWatchTrain.triggered.connect(self.watchTrain)
        self.actionImportModel.triggered.connect(self.ImportModel)
        self.actionDeleteModel.triggered.connect(self.DeleteModel)
        self.actionModelStatistic.triggered.connect(self.modelStatistic)

        self.actionSelectFeature.triggered.connect(self.selectFeature)
        self.actionDrawRect.triggered.connect(self.drawRect)
        self.actionClearDraw.triggered.connect(self.clearDraw)  
        self.actionSegment.triggered.connect(self.segment)
        self.actionPostClump.triggered.connect(self.postClump)
        self.actionRasterToVector.triggered.connect(self.rasterToVector) 

        self.actionSplitDataSet.triggered.connect(self.splitDataSet)
        self.actionUpdateDatabase.triggered.connect(self.updateDatabase)
        self.actionUpdateModelsDB.triggered.connect(self.updateModelsDB)

        self.actionAbout.triggered.connect(self.about) 
        # 控件绑定事件
        self.canvas.xyCoordinates.connect(self.showXY)
        self.canvas.destinationCrsChanged.connect(self.showCrs)
        self.tableView.doubleClicked.connect(self.on_tableView_double_clicked)    
        self.dockWidget.visibilityChanged.connect(self.on_tocViewDock_visibility_changed)       
        self.dockWidget_2.visibilityChanged.connect(self.on_tableViewDock_visibility_changed)
        # 单击、双击图层 触发事件
        self.tocView.clicked.connect(self.layerClicked)
      
    # 新建工程
    def newProject(self):
        if self.project.isDirty():
            print("工程有未保存的修改")
            savePrj = show_question_message(self, '提示', "是否保存对当前工程的更改？")
            if savePrj == QMessageBox.Yes:
                self.saveProject()
        # 创建一个新的项目
        self.new = True # 新建工程标志 
        self.project.clear()  # 清除当前项目中的所有内容（如果有的话）
        
        # 设置项目的CRS（可选）
        # 例如，使用WGS 84坐标系统
        crs = QgsCoordinateReferenceSystem()
        crs.createFromId(4326, QgsCoordinateReferenceSystem.EpsgCrsId)
        self.project.setCrs(crs)
        
        # 保存新项目到文件（例如：new_project.qgs）
        from DeeplearningSystem import base_dir
        project_path = join(base_dir, 'temp', 'new_project.qgs')
        self.project.writeEntry("qgis", "/projectTitle", "New Project")  # 设置项目标题（可选）
        self.project.setFileName(project_path)
        self.project.write()     
        self.setWindowTitle(f"new_project - {self.title.split(' - ')[1] if self.title.find('-')>=0 else self.title}") 
    
    # 打开工程
    def openProject(self):
        self.closeProject()
        path_to_project,_ = QFileDialog.getOpenFileName (self, '打开工程', '', 'Project File (*.qgs);;All Files (*.*)')
        if  path_to_project == "":# 如果用户取消了选择，则返回空字符串
            return
        self.addProject(path_to_project)      
        self.recent_files.manager.add_recent_file(path_to_project)      

        self.new = False

    # 关闭工程
    def closeProject(self):
        if self.project.isDirty():
            print("工程有未保存的修改")
            savePrj = show_question_message(self, '提示', "是否保存对当前工程的更改？")
            if savePrj == QMessageBox.Yes:
                self.saveProject()
            else:
                return           
        else:
            print("工程没有未保存的修改")
            self.newProject()

    # 保存工程
    def saveProject(self):
        # 获取当前项目实例
        self.project.writeEntry("ViewSettings", "LastExtent", self.canvas.extent().toString())
        crs = self.canvas.mapSettings().destinationCrs().authid()
        self.project.writeEntry("ViewSettings", "LastExtentCRS", crs)
        if self.new:
            path_to_project,_ = QFileDialog.getSaveFileName (self, '保存工程', '', 'Project File (*.qgs);;All Files (*.*)')
            if  path_to_project == "":# 如果用户取消了选择，则返回空字符串
                return               
            # 设置要保存的文件路径和文件名
            #project.setFileName(path_to_project)   
            # 保存项目到指定文件
            self.project.write(path_to_project)
            self.setWindowTitle(f"{basename(path_to_project).split('.')[0]} - {self.title.split(' - ')[1] if self.title.find('-')>=0 else self.title}") 
            self.new = False
        else:
            self.project.write()

    # 另存工程
    def saveAsProject(self):
        # 获取当前项目实例
        self.project.writeEntry("ViewSettings", "LastExtent", self.canvas.extent().toString())
        crs = self.canvas.mapSettings().destinationCrs().authid()
        self.project.writeEntry("ViewSettings", "LastExtentCRS", crs)
        path_to_project,_ = QFileDialog.getSaveFileName (self, '保存工程', '', 'Project File (*.qgs);;All Files (*.*)')
        if  path_to_project == "":# 如果用户取消了选择，则返回空字符串
            return               
        # 设置要保存的文件路径和文件名
        #project.setFileName(path_to_project)   
        # 保存项目到指定文件
        self.project.write(path_to_project)
        self.setWindowTitle(f"{basename(path_to_project).split('.')[0]} -{self.title.split(' - ')[1] if self.title.find('-')>=0 else self.title}") 

        self.new = False
        self.initPrj = False 


    # 打开影像
    def openDialogRas(self):
        path_to_tif,_ = QFileDialog.getOpenFileName(self, '打开', '', 'Raster Files (*.tif;*.tiff;*.img;*.dat);;All Files (*.*)')
        if  path_to_tif=="":# 如果用户取消了选择，则返回空字符串
            return
        self.addRaster(path_to_tif)

    # 打开矢量
    def openDialogVec(self):
        path_to_vec, _ = QFileDialog.getOpenFileName(self, '打开', '', 'Vector Files (*.shp);;All Files (*.*)')
        if  path_to_vec=="":
            return
        self.addVector(path_to_vec)

    # 视图放大         
    def zoomIn(self):
        self.toolZoomIn = QgsMapToolZoom(self.canvas, False)  # false = in
        self.toolZoomIn.setAction(self.actionZoomIn)
        self.canvas.setMapTool(self.toolZoomIn)

    # 视图缩小
    def zoomOut(self):
        self.toolZoomOut = QgsMapToolZoom(self.canvas, True)  # true = out
        self.toolZoomOut.setAction(self.actionZoomOut)
        self.canvas.setMapTool(self.toolZoomOut)

    # 视图平移
    def pan(self):
        self.toolPan = QgsMapToolPan(self.canvas)
        self.toolPan.setAction(self.actionPan)
        self.canvas.setMapTool(self.toolPan)

    # 视图全图
    def fullExtent(self):
        self.canvas.zoomToFullExtent()

    # 视图卷帘
    def swipe(self):
        from tools.SwipeTool import SwipeToolController
        swipe_controller = SwipeToolController(self)

    # 图层面板显示
    def showLayerView(self,checked):
        if checked:
            self.dockWidget.setVisible(True)  # 不显示
        else:
            self.dockWidget.setVisible(False)  # 显示
    # 图层面板是否可见事件
    def on_tocViewDock_visibility_changed(self,visible):  
        if not self.isMinimized():
            if not visible: 
                self.actionLayerView.setChecked(False)
            else:
                self.actionLayerView.setChecked(True)

    # 样本库面板显示    
    def showSamplesView(self,checked):
        if checked:
            self.dockWidget_2.setVisible(True)  # 显示
        else:
            self.dockWidget_2.setVisible(False)  # 显示  
    # 样本库面板是否可见事件
    def on_tableViewDock_visibility_changed(self,visible):
            if not self.isMinimized():
                if not visible: 
                    self.actionSamplesView.setChecked(False)
                else:
                    self.actionSamplesView.setChecked(True)
    # 样本库面板双击事件
    def on_tableView_double_clicked(self, index):
        row = index.row()
        name_index = index.sibling(row, 0)
        name = name_index.data()
        path_index = index.sibling(row, 6)  # 获取同一行的其他列索引
        path = path_index.data()  # 获取单元格数据
        image_file = f'{path}/image/{name}.tif'
        from os.path import exists
        if not exists(image_file):
            image_file = f'{path}/image/{name}.tiff'
        shape_file = f'{path}/vector/{name}.shp'
        #print(image_file,shape_file)
        self.addRaster(image_file)
        self.addVector(shape_file)

    # 编辑矢量
    def editSample(self):
        if self.actionEditSample.isChecked():
            self.editTempLayer : QgsVectorLayer = self.tocView.currentLayer()
            self.editTempLayer.startEditing()
        else:
            saveShpEdit = show_question_message(self, '保存编辑', "确定要将编辑内容保存到内存吗？")
            if saveShpEdit == QMessageBox.Yes:
                self.editTempLayer.commitChanges()
            else:
                self.editTempLayer.rollBack()
    
            self.canvas.refresh()
            self.pan()
            self.actionEditSample.setEnabled(False)
            self.editTempLayer = None
    # 激活“编辑矢量”功能
    def layerClicked(self):
        curLayer: QgsMapLayer = self.tocView.currentLayer()
        if curLayer and type(curLayer) == QgsVectorLayer and not curLayer.readOnly():
            self.actionEditSample.setEnabled(True)
        else:
            self.actionEditSample.setEnabled(False)
   
    # 画多边形
    def drawPolygon(self):  
        from tools.PolygonMapTool import PolygonMapTool
        if self.editTempLayer == None:
            show_info_message(self, '警告', '您没有编辑中的矢量！')
            return
        if self.canvas.mapTool():
            self.canvas.mapTool().deactivate()
        self.polygonTool = PolygonMapTool(self.canvas, self.editTempLayer, self)
        self.canvas.setMapTool(self.polygonTool)
    
    # 选择样本
    def selectSample(self):
        current_layer = self.tocView.currentLayer()
        if not current_layer:
            show_info_message(self,'提示','未选中矢量图层！！！\n请在图层树中点击一个矢量图层！')
            self.actionSelectSample.setCheckable(False)
            return
        else:
            self.actionSelectSample.setCheckable(True)

        if self.actionSelectSample.isChecked():
            if self.canvas.mapTool():
                self.canvas.unsetMapTool(self.canvas.mapTool())
            self.toolSelectSample = QgsMapToolIdentifyFeature(self.canvas)
            self.toolSelectSample.setAction(self.actionSelectSample)
            self.toolSelectSample.setCursor(Qt.ArrowCursor)
            self.toolSelectSample.featureIdentified.connect(self.selectToolIdentified)
            layers = self.canvas.layers()
            if layers:
                self.toolSelectSample.setLayer(current_layer)
            self.canvas.setMapTool(self.toolSelectSample)
        else:
            if self.canvas.mapTool():
                self.canvas.unsetMapTool(self.canvas.mapTool())
    
    # 选择要素
    def selectFeature(self):
        current_layer = self.tocView.currentLayer()
        if not current_layer:
            show_info_message(self,'提示','未选中矢量图层！！！\n请在图层树中点击一个矢量图层！')
            self.actionSelectFeature.setCheckable(False)
            return
        else:
            self.actionSelectFeature.setCheckable(True)
        if self.actionSelectFeature.isChecked():
            if self.canvas.mapTool():
                self.canvas.unsetMapTool(self.canvas.mapTool())
            self.toolSelectFeature = QgsMapToolIdentifyFeature(self.canvas)
            self.toolSelectFeature.setAction(self.actionSelectFeature)
            self.toolSelectFeature.setCursor(Qt.ArrowCursor)
            self.toolSelectFeature.featureIdentified.connect(self.selectToolIdentified)
            layers = self.canvas.layers()
            if layers:
                self.toolSelectFeature.setLayer(current_layer)
            self.canvas.setMapTool(self.toolSelectFeature)
        else:
            if self.canvas.mapTool():
                self.canvas.unsetMapTool(self.canvas.mapTool())
    # 选择要素用到的工具
    def selectToolIdentified(self,feature):
        #print(feature.id())
        layerTemp: QgsVectorLayer = self.tocView.currentLayer()
        if layerTemp.type() == QgsMapLayerType.VectorLayer:
            if feature.id() in layerTemp.selectedFeatureIds():
                layerTemp.deselect(feature.id())
            else:
                layerTemp.removeSelection()
                layerTemp.select(feature.id())

    # 删除要素
    def deleteSample(self):
        if self.editTempLayer == None:
            show_info_message(self, '警告', '您没有编辑中矢量')
            return
        if len(self.editTempLayer.selectedFeatureIds()) == 0:
            show_info_message(self, '删除选中矢量', '您没有选择任何矢量')
        else:
            self.editTempLayer.deleteSelectedFeatures()

    # 样本制作
    def makeSample(self):
        from dialog.MakeSamplesDiaolog import MakeSamplesDialog
        self.makeSampleDialog = MakeSamplesDialog()
        # 显示对话框
        result = self.makeSampleDialog.exec_()  # 这会阻塞，直到对话框关闭
 
        if result == QDialog.Accepted:
            from algorithm.MakeSampleThread import MakeSampleThread
            self.thread = MakeSampleThread(self.makeSampleDialog, self.progress_bar)
            self.thread.finished.connect(self.on_makeSample_finished)  # 连接信号到槽
            self.thread.start()
        elif result == QDialog.Rejected:
            print("User clicked Close or pressed Escape")
    # 样本制作后事件    
    def on_makeSample_finished(self, result):
        makeSample = show_question_message(self, '样本制作', f"需要将已制作完成的样本入库吗？")
        if makeSample == QMessageBox.Yes:
            sampleClass, samplePath = result
            result = samplePath.rsplit('/', 6)
            sampleName = result[5]
            print(f'sampleName={sampleName}')

            parser = etree.XMLParser(remove_blank_text=True)  # 移除空白文本节点
            # XML文件的路径
            from DeeplearningSystem import sample_cofing_path
            # 加载现有 XML
            tree = etree.parse(sample_cofing_path, parser)
        
            # 查找特定ID的节点
            nodes = tree.xpath(f'//SamplePath[@Name="{sampleName}"]')
            if not nodes:
                node1 = tree.xpath(f'//SampleClass[@EnglishName="{sampleClass}"]')[0]
                # 创建新节点
                new_node = etree.SubElement(node1, 'SamplePath', 
                                            attrib={'Type': self.ui_importSample.lineEdit_labelType.text(),
                                                    'Size': self.ui_importSample.lineEdit_labelSize.text(),
                                                    'GSD': self.ui_importSample.lineEdit_labelGSD.text(),
                                                    'Acc': self.ui_importSample.lineEdit_labelAcc.text(),
                                                    'Recall': self.ui_importSample.lineEdit_labelRecall.text(),
                                                    'IOU': self.ui_importSample.lineEdit_labelIOU.text(),
                                                    'Name': self.ui_importSample.lineEdit_labelName.text(),
                                                    'ValSetNums': self.ui_importSample.lineEdit_labelValNums.text()
                                                    }).text = self.ui_importSample.lineEdit_SamplesPath.text()+"/"
            else:
                node = nodes[0]
                saveSample = show_question_message(self, '样本导入', "存在相同的样本，确定要导入吗？\n如果导入,将会覆盖！")
                if saveSample == QMessageBox.Yes:
                    node.text = self.ui_importSample.lineEdit_SamplesPath.text()+"/"  # 更新文本内容
                else:
                    return
            # 保存修改
            tree.write(sample_cofing_path, 
                    encoding='utf-8', 
                    xml_declaration=True, 
                    pretty_print=True) 
            show_info_message(self, "信息", "样本导入完成!")

    # 样本评估
    def evalSample(self):
        from dialog.EvalSamplesDialog import EvalSamplesDialog
        self.evalSampleDialog = EvalSamplesDialog()
        # 显示对话框
        result = self.evalSampleDialog.exec_()  # 这会阻塞，直到对话框关闭
 
        if result == QDialog.Accepted:
            from algorithm.EvalSampleThread import EvalSampleThread
            self.thread = EvalSampleThread(self.evalSampleDialog, self.progress_bar)
            self.thread.finished.connect(self.on_evalSample_finished)  # 连接信号到槽
            self.thread.start()
        elif result == QDialog.Rejected:
            print("User clicked Close or pressed Escape")
    # 样本评估后事件
    def on_evalSample_finished(self,result):
        show_info_message(self,"提示","样本评估完成！")

    # 样本统计
    def sampleStatistic(self):
        from dialog.SamplesStatisticDialog import SamplesStatisticDialog
        self.samplesStatisticDialog = SamplesStatisticDialog(self)
        # 显示对话框
        self.samplesStatisticDialog.show()

    # 样本库导入
    def importSample(self):
        from dialog.ImportSamplesDialog import ImportSamplesDialog
        # 创建一个对话框实例，这里我们假设对话框是基于 QDialog 的
        self.importSampleDialog = ImportSamplesDialog()
    
        # 显示对话框
        result = self.importSampleDialog.exec_()

        if result == QDialog.Accepted:
            parser = etree.XMLParser(remove_blank_text=True)  # 移除空白文本节点
            # XML文件的路径
            from DeeplearningSystem import sample_cofing_path
            # 加载现有 XML
            tree = etree.parse(sample_cofing_path, parser)
        
            # 查找特定ID的节点
            nodes = tree.xpath(f'//SamplePath[@Name="{self.importSampleDialog.lineEdit_labelName.text()}"]')
            if not nodes:
                node1 = tree.xpath(f'//SampleClass[@EnglishName="{self.importSampleDialog.lineEdit_Class.text()}"]')[0]
                print(f'self.importSampleDialog.lineEdit_labelValNums.text()={self.importSampleDialog.lineEdit_labelValNums.text()}')
                # 创建新节点
                new_node = etree.SubElement(node1, 'SamplePath', 
                                            attrib={'Type': self.importSampleDialog.lineEdit_labelType.text(),
                                                    'Size': self.importSampleDialog.lineEdit_labelSize.text(),
                                                    'GSD': self.importSampleDialog.lineEdit_labelGSD.text(),
                                                    'Acc': self.importSampleDialog.lineEdit_labelAcc.text(),
                                                    'Recall': self.importSampleDialog.lineEdit_labelRecall.text(),
                                                    'IOU': self.importSampleDialog.lineEdit_labelIOU.text(),
                                                    'Name': self.importSampleDialog.lineEdit_labelName.text(),
                                                    'ValSetNums': self.importSampleDialog.lineEdit_labelValNums.text()
                                                    }).text = self.importSampleDialog.lineEdit_SamplesPath.text()+"/"
            else:
                node = nodes[0]
                saveSample = show_question_message(self, '样本导入', "存在相同的样本，确定要导入吗？\n如果导入，将会覆盖！")
                if saveSample == QMessageBox.Yes:
                    node.text = self.ui_importSample.lineEdit_SamplesPath.text()+"/"  # 更新文本内容
                else:
                    return
            # 保存修改
            tree.write(sample_cofing_path, 
                    encoding='utf-8', 
                    xml_declaration=True, 
                    pretty_print=True)   
            self.updateDatabase()
            show_info_message(self, "信息", "样本导入完成!")   
        elif result == QDialog.Rejected:
            print("User clicked Close or pressed Escape")
    
    # 样本库删除
    def deleteSamples(self):
        from dialog.DeleteSamplesDialog import DeleteSamplesDialog
        self.deleteSamplesDialog = DeleteSamplesDialog()
        # 显示对话框
        result = self.deleteSamplesDialog.exec_()

        if result == QDialog.Accepted:
            # XML文件的路径
            from DeeplearningSystem import sample_cofing_path
            # 加载现有 XML
            tree = etree.parse(sample_cofing_path)

            column_index = 4  # 假设复选框项在第三列（索引为4）
            for row_index in range(self.deleteSamplesDialog.model.rowCount()):                  
                check_state = self.deleteSamplesDialog.model.item(row_index, column_index).checkState()
                if check_state == Qt.Checked:
                    name = self.deleteSamplesDialog.sampleList[row_index]
                    # 查找特定ID的节点
                    try:
                        # 尝试获取节点
                        node = tree.xpath(f'//SamplePath[@Name="{name}"]')[0]
                        if node is not None:
                            deleteSample = show_question_message(self, '删除样本库', f"确定要删除名称为“{name}”的样本库吗？")
                            if deleteSample == QMessageBox.Yes:
                                node.getparent().remove(node)
                            else:
                                return                                
                    except IndexError:
                        print("未找到匹配的节点")
                    except etree.XPathEvalError as e:
                        print(f"XPath表达式错误: {e}")
                    except Exception as e:
                        print(f"发生错误: {e}")
                    # 保存修改
                    tree.write(sample_cofing_path, 
                            encoding='utf-8', 
                            xml_declaration=True, 
                            pretty_print=True)
                    self.updateDatabase()
                    show_info_message(self, "信息", "样本删除完成!")  
    
    # 样本库查询
    def querySample(self):
        from dialog.QuerySampleDialog import QuerySamplesDialog
        self.querySampleDialog = QuerySamplesDialog()
        # 显示对话框
        result = self.querySampleDialog.exec_()

        if result == QDialog.Accepted:
            # 启动子线程
            from algorithm.QuerySampleThread import QuerySampleThread
            self.thread_query = QuerySampleThread(self.querySampleDialog, self.progress_bar)
            self.thread_query.finished.connect(self.on_query_finished)  # 连接信号到槽
            self.thread_query.start()  
            self.actionCloseSamples.setEnabled(True)
        elif result == QDialog.Rejected:
            print("User clicked Close or pressed Escape")
    # 样本库查询完成后响应事件
    def on_query_finished(self,result):
        print(result)
        import time
        from osgeo import ogr
        ogr.UseExceptions()
        time_start=time.time()
        self.progress_bar.setText('开始处理...')
        samplelists = self.thread_query.sampleList
        count = len(samplelists)
        #print(count)
        for index1,sample in enumerate(samplelists):
            rangefile = sample+'SamplesRange.shp'
            driver = ogr.GetDriverByName("ESRI Shapefile")
            data_source:ogr.DataSource = driver.Open(rangefile, 0)  # 0只读模式
            if data_source is None:
                print(f"无法打开文件:{rangefile}")
                return
            else:
                layer = data_source.GetLayer()

            # 获取输入图层的几何类型和字段定义
            feature_count = layer.GetFeatureCount()
            # 遍历每个要素
            for index2,feature in enumerate(layer):
                self.progress_bar.setText(f"开始处理({index1+1}/{count}): {int((index2+1) * 100 / feature_count)}%")
                # 确定输出文件名
                name  = feature.GetField("Name")
                type = feature.GetField("Bz")
                loss = feature.GetField("Loss")
                acc = feature.GetField("Acc")
                recall = feature.GetField("Recall")
                iou = feature.GetField("Iou")
                path = feature.GetField("Path")
                checkbox_item = QStandardItem()
                checkbox_item.setCheckable(True)
                #checkbox_item.setCheckState(Qt.Unchecked)  # 可选：设置初始检查状态                               
                row = [QStandardItem(name), QStandardItem(type), QStandardItem(loss), QStandardItem(acc), QStandardItem(recall), QStandardItem(iou), QStandardItem(path), checkbox_item]
                self.sampleModel.appendRow(row)
        self.tableView.resizeColumnsToContents()
        time_end = time.time()
        self.progress_bar.setText(f"处理完成: 花费时间 {((time_end-time_start)/60.0):.2f} 分钟")

    # 样本库关闭
    def closeSamples(self):
        self.sampleModel.removeRows(0,self.sampleModel.rowCount())
        self.tableView.resizeColumnsToContents()
        self.actionCloseSamples.setEnabled(False)

    # 模型训练
    def modelTrain(self):
        from dialog.TrainDialog import TrainDialog
        self.trainDialog = TrainDialog()
        result = self.trainDialog.exec_()  # 这会阻塞，直到对话框关闭
 
        if result == QDialog.Accepted:
            self.actionStopTrain.setEnabled(True)
            self.actionWatchTrain.setEnabled(True)
            # sample
            lines_train = []
            train_nums = 0
            lines_val = []
            val_nums = 0
            column_index = 4  # 假设复选框项在第三列（索引为4）
            for row_index in range(self.trainDialog.model.rowCount()):                  
                check_state = self.trainDialog.model.item(row_index, column_index).checkState()
                if check_state == Qt.Checked:
                    samplerange_file = self.trainDialog.sampleList[row_index]+'SamplesRange.shp'
                    from osgeo import ogr
                    driver = ogr.GetDriverByName("ESRI Shapefile")
                    data_source:ogr.DataSource = driver.Open(samplerange_file, 0)  # 0只读模式
                    if data_source is None:
                        print("无法打开文件")
                    else:
                        layer = data_source.GetLayer()
                    for feature in layer:
                        bz_vale = feature.GetField("Bz")
                        name_value = feature.GetField("Name")
                        path_value = feature.GetField("Path")
                        sample = f'{path_value}/image/{name_value}.tif'
                        from os.path import exists
                        if not exists(sample):
                            sample = f'{path_value}/image/{name_value}.tiff'
                        sample = sample + '\n'
                        if bz_vale == "train":
                            lines_train.append(sample)
                            train_nums+=1
                        elif bz_vale == "val":
                            lines_val.append(sample)
                            val_nums+=1
                    data_source.Release()
            from DeeplearningSystem import train_set,val_set
            with open(train_set, 'w', encoding='utf-8') as file:
                file.write(f'{train_nums}\n')
                file.writelines(lines_train)
            with open(val_set, 'w', encoding='utf-8') as file:
                file.write(f'{val_nums}\n')
                file.writelines(lines_val)
            # 初始化日志监视对话框
            from dialog.LogDialog import LogDialog     
            self.logDialog = LogDialog(self) 
            # 启动训练子线程
            from algorithm.TrainThread import TrainThread
            self.thread_train = TrainThread(self.trainDialog, self.progress_bar)
            self.thread_train.finished.connect(self.on_train_finished)  # 连接信号到槽
            self.thread_train.msg.connect(self.on_train_msg)  # 连接信号到槽
            self.thread_train.start()                       
        elif result == QDialog.Rejected:
            print("User clicked Close or pressed Escape")
    # 模型训练后事件
    def on_train_finished(self, result):
        show_info_message(self, '提示', f"训练完成！")
    # 模型训练中事件
    def on_train_msg(self, result):
        self.logDialog.textEdit_Log.append(result)

    # 终止训练
    def stopTrain(self):  
        result = show_question_message(self, '信息', "确定要终止训练？")
        if result == QMessageBox.Yes:
            self.thread_train.stop()

    # 监视训练
    def watchTrain(self):                    
        # 显示对话框
        self.logDialog.show()

    # 模型导入
    def ImportModel(self):
        from dialog.ImportModelsDialog import ImportModelsDialog
        # 创建一个对话框实例，这里我们假设对话框是基于 QDialog 的
        self.importModelsDialog = ImportModelsDialog()
    
        # 显示对话框
        result = self.importModelsDialog.exec_()

        if result == QDialog.Accepted:
            parser = etree.XMLParser(remove_blank_text=True)  # 移除空白文本节点
            # XML文件的路径
            from DeeplearningSystem import model_cofing_path
            # 加载现有 XML
            tree = etree.parse(model_cofing_path, parser)
        
            # 查找特定ID的节点
            nodes = tree.xpath(f'//ModelPath[@Name="{self.importModelsDialog.lineEdit_Name.text()}"]')
            if not nodes:
                node1 = tree.xpath(f'//ModelClass[@EnglishName="{self.importModelsDialog.lineEdit_Class.text()}"]')[0]
                # 创建新节点
                new_node = etree.SubElement(node1, 'ModelPath', 
                                            attrib={'Name': self.importModelsDialog.lineEdit_Name.text(),
                                                    'Net': self.importModelsDialog.lineEdit_net.text(),
                                                    'GSD': self.importModelsDialog.comboBox_GSD.currentText()
                                                    }).text = self.importModelsDialog.lineEdit_ModelsPath.text()
            else:
                node = nodes[0]
                save = show_question_message(self.importModelsDialog, '模型导入', "存在相同的模型，确定要导入吗？\n如果导入，将会覆盖！")
                if save == QMessageBox.Yes:
                    node.text = self.importModelsDialog.lineEdit_ModelsPath.text()  # 更新文本内容
                else:
                    return
            # 保存修改
            tree.write(model_cofing_path, 
                    encoding='utf-8', 
                    xml_declaration=True, 
                    pretty_print=True) 
            self.updateModelsDB()
            show_info_message(self.importModelsDialog, "模型导入", "模型导入完成!")   
        elif result == QDialog.Rejected:
            print("User clicked Close or pressed Escape")

    # 模型删除
    def DeleteModel(self):
        from dialog.DeleteModelsDialog import DeleteModelsDialog
        self.deleteModelsDialog = DeleteModelsDialog(self)
        # 显示对话框
        result = self.deleteModelsDialog.exec_()

        if result == QDialog.Accepted:
            # XML文件的路径
            from DeeplearningSystem import model_cofing_path
            # 加载现有 XML
            tree = etree.parse(model_cofing_path)
            column_index = 0  # 假设复选框项在第三列（索引为4）
            for row_index in range(self.deleteModelsDialog.model.rowCount()):                  
                check_state = self.deleteModelsDialog.model.item(row_index, column_index).checkState()
                if check_state == Qt.Checked:
                    name = self.deleteModelsDialog.list[row_index]
                    # 查找特定ID的节点
                    try:
                        # 尝试获取节点
                        node = tree.xpath(f'//ModelPath[@Name="{name}"]')[0]
                        if node is not None:
                            delete = show_question_message(self.deleteModelsDialog, '删除模型', f"确定要删除名称为“{name}”的模型吗？")
                            if delete == QMessageBox.Yes:
                                node.getparent().remove(node)
                            else:
                                return                                
                    except IndexError:
                        print("未找到匹配的节点")
                    except etree.XPathEvalError as e:
                        print(f"XPath表达式错误: {e}")
                    except Exception as e:
                        print(f"发生错误: {e}")
                    # 保存修改
                    tree.write(model_cofing_path, 
                            encoding='utf-8', 
                            xml_declaration=True, 
                            pretty_print=True)
                    self.updateModelsDB()
                    show_info_message(self.deleteModelsDialog, "删除模型", "模型删除完成!")  

    # 模型统计
    def modelStatistic(self):
        from dialog.ModelsStatisticDialog import ModelsStatisticDialog
        self.modelsStatisticDialog = ModelsStatisticDialog(self)
        # 显示对话框
        self.modelsStatisticDialog.show()

    # 画矩形     
    def drawRect(self):  
        from tools.RectangleMapTool import RectangleMapTool
        self.toolDrawRect = RectangleMapTool(self.canvas)
        self.toolDrawRect.setAction(self.actionDrawRect)
        self.canvas.setMapTool(self.toolDrawRect)
        self.actionClearDraw.setEnabled(True)

    # 清绘
    def clearDraw(self):  
        self.toolDrawRect.reset()    
        self.canvas.scene().removeItem(self.toolDrawRect.rubberBand)
        self.pan()
        self.actionClearDraw.setEnabled(False)
    
    # 地物提取
    def segment(self, path):
        from dialog.SegmentDialog import SegmentDialog
        self.segmentDialog = SegmentDialog()
        # 显示对话框
        result = self.segmentDialog.exec_()  # 这会阻塞，直到对话框关闭
 
        if result == QDialog.Accepted:
            from algorithm.PredictThread import PredictThread
            self.thread = PredictThread(self.segmentDialog, self.progress_bar, self.toolDrawRect)
            self.thread.finished.connect(self.on_segment_finished)  # 连接信号到槽
            self.thread.start()    
        elif result == QDialog.Rejected:
            print("User clicked Close or pressed Escape")
    # 地物提取后事件
    def on_segment_finished(self, result):
        print(result)  # 在主线程中处理结果
        self.addRaster(result)

    # 聚类-分类后处理
    def postClump(self):
        from dialog.PostProcessDialog import PostProcessDialog
        self.postprocessDialog = PostProcessDialog()
        # 显示对话框
        result = self.postprocessDialog.exec_()  # 这会阻塞，直到对话框关闭
 
        if result == QDialog.Accepted:
            from algorithm.PostClumpThread import PostClumpThread
            self.thread = PostClumpThread(self.postprocessDialog, self.progress_bar, self.toolDrawRect)
            self.thread.finished.connect(self.on_postclump_finished)  # 连接信号到槽
            self.thread.start()
        elif result == QDialog.Rejected:
            print("User clicked Close or pressed Escape")
    # 聚类后事件
    def on_postclump_finished(self, result):
        #print(result)  # 在主线程中处理结果
        self.addRaster(result)

    # 栅格转矢量
    def rasterToVector(self):
        from dialog.RasterToVectorDialog import RasterToVectorDialog
        self.rasterToVectorDialog = RasterToVectorDialog()
        # 显示对话框
        result = self.rasterToVectorDialog.exec_()  # 这会阻塞，直到对话框关闭
 
        if result == QDialog.Accepted:
            from algorithm.RasterToVectorThread import RasterToVectorThread
            self.thread = RasterToVectorThread(self.rasterToVectorDialog, self.progress_bar)
            self.thread.finished.connect(self.on_rasterToVector_finished)  # 连接信号到槽
            self.thread.start()
        elif result == QDialog.Rejected:
            print("User clicked Close or pressed Escape")
    # 栅格转矢量后事件
    def on_rasterToVector_finished(self, result):
        print(result)  # 在主线程中处理结果
        self.addVector(result)

    # 数据集划分-成训练集和验证集
    def splitDataSet(self):
        from dialog.SplitDatasetDialog import SplitDatasetDialog
        # 创建一个对话框实例，这里我们假设对话框是基于 QDialog 的
        self.splitDataSetDialog = SplitDatasetDialog()
        # 显示对话框
        result = self.splitDataSetDialog.exec_()

        if result == QDialog.Accepted:
            from torch.utils.data import random_split
            from algorithm.tool.dataset_split import BasicDataset
            import torch
            from tqdm import tqdm
            from os.path import dirname
            from os import mkdir
            from os.path import exists
            import time
            import shutil 
            from osgeo import ogr
            time_start=time.time() 
            trainsetNums = int(self.ui_splitDataset.lineEdit_trainset.text())
            valsetNums = int(self.ui_splitDataset.lineEdit_valset.text())
            testsetNums = int(self.ui_splitDataset.lineEdit_testset.text())          
            column_index = 4  # 假设复选框项在第三列（索引为4）
            for row_index in range(self.ui_splitDataset.model.rowCount()):                  
                check_state = self.ui_splitDataset.model.item(row_index, column_index).checkState()
                samplepath = self.ui_splitDataset.sampleList[row_index]
                if check_state == Qt.Checked:
                    samplerange_file = samplepath + 'SamplesRange.shp'                
                    split_path = dirname(dirname(samplepath)) + '/split/'
                    #print(split_path)
                    train_file = split_path + '/train_set.txt'
                    val_file = split_path + '/val_set.txt'
                    test_file = split_path + '/test_set.txt'
                    #make dir
                    if (exists(split_path)!=True):
                        mkdir(split_path)
                    else:
                        shutil.rmtree(split_path)
                        mkdir(split_path)
                    #processing
                    image_path =  samplepath + 'image/'
                    label_path = samplepath + 'label/'    
                    dataset = BasicDataset(image_path, label_path)
                    if len(dataset) != (trainsetNums+valsetNums+testsetNums):
                       show_info_message(self, "错误", f"数据集划分参数错误！\n现有数据集数量（{len(dataset)}）不等于查询到的数据集数量（{(trainsetNums+valsetNums+testsetNums)}）。") 
                    train_set, val_set, test_set = random_split(dataset, [trainsetNums, valsetNums, testsetNums], generator=torch.Generator().manual_seed(0))   

                    f = open(train_file,'w',buffering=1)
                    f.write(str(trainsetNums)+'\n') 
                    strTrainSet = ""
                    for image,label in tqdm(train_set):
                        strTrainSet += image + '\n'
                    f.write(strTrainSet)
                    f.close()
                    f = open(val_file,'w',buffering=1)
                    f.write(str(valsetNums)+'\n')
                    strValSet = ""
                    for image,label in tqdm(val_set):
                        strValSet += image + '\n'
                    f.write(strValSet)
                    f.close()
                    f = open(test_file,'w',buffering=1)
                    f.write(str(testsetNums)+'\n') 
                    strTestSet = ""
                    for image,label in tqdm(test_set):
                        strTestSet += image + '\n'
                    f.write(strTestSet)
                    f.close()
                    #print(strValSet)

                    driver = ogr.GetDriverByName("ESRI Shapefile")
                    data_source:ogr.DataSource = driver.Open(samplerange_file, 1)  # 1表示更新模式
                    if data_source is None:
                        print("无法打开文件")
                    else:
                        layer = data_source.GetLayer()
                    for feature in layer:
                        name_value = feature.GetField("Name")
                        if str(strValSet).find(str(name_value))!=-1:
                            #print(name_value)
                            # 设置bz字段的值，这里假设设为"新属性值"，你可按需替换
                            feature.SetField("Bz", "val")
                        elif str(strTestSet).find(str(name_value))!=-1:
                            feature.SetField("Bz", "test")
                        else:
                            feature.SetField("Bz", "train")
                        layer.SetFeature(feature)
                    data_source.Release()
            time_end=time.time()
            print('time cost','%.2f'%((time_end-time_start)/60.0),'minutes') 
            show_info_message(self, "信息", "数据集划分完成!")   
        elif result == QDialog.Rejected:
            print("User clicked Close or pressed Escape")
    
    def updateDatabase(self):
        self.progress_bar.setText('开始处理...')
        import time
        time_start=time.time() 
        from PyQt5.QtSql import QSqlDatabase, QSqlQuery
        """初始化数据库连接"""
        db_samples = QSqlDatabase.addDatabase("QSQLITE")
        db_samples.setDatabaseName("databae_samples.db")  # SQLite数据库文件
        
        if not db_samples.open():
            show_info_message(self, "错误", "无法连接数据库")
            return False
            
        # 创建数据表（如果不存在）
        query = QSqlQuery(db_samples)
        table_sql = """
            CREATE TABLE IF NOT EXISTS imported_data (
                序号 INTEGER PRIMARY KEY,
                名称 TEXT,
                类别 TEXT,
                地市 TEXT,
                `县区/景` TEXT,
                类型 TEXT,
                时相 INTEGER,
                分辨率 TEXT,
                数量 INTEGER,
                备注 TEXT,
                训练集 INTEGER,
                验证集 INTEGER,
                `训:验` REAL,  
                查准 REAL, 
                查全 REAL, 
                IOU REAL                            
            )
            """
        if not query.exec_(table_sql):
            show_info_message(self, "错误", f"创建表失败: {query.lastError().text()}")
            return
         # 开始事务
        db_samples.transaction()
        # 清空现有数据
        QSqlQuery("DELETE FROM imported_data", db_samples)
        
        # 插入新数据
        query = QSqlQuery(db_samples)
        # 插入数据
        insert_sql = """
        INSERT INTO imported_data 
        (名称, 类别, 地市, `县区/景`, 类型, 时相, 分辨率, 数量, 备注, 训练集, 验证集, `训:验`, 查准, 查全, IOU) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        query.prepare(insert_sql)
        # 加载现有 XML
        from DeeplearningSystem import sample_cofing_path
        tree = etree.parse(sample_cofing_path)
        # 尝试获取节点
        nodes = tree.xpath(f'//SamplePath')
        # "名称", "类别", "地市", "县区/景", "类型", "时相", "分辨率", "数量", "备注", "训练集", "验证集", "训:验", "查准", "查全", "IOU"
        # negative_411726_202102_biyang_unknown
        sum = 0
        for index,node in enumerate(nodes):
            self.progress_bar.setText(f"开始处理: {int((index+1) * 100 / len(nodes))}%")
            Name = node.get('Name')
            s = Name.split('_')
            Class = node.getparent().get('Name')
            Country1 = s[1][:4]
            Country2 = s[3]
            Type = s[0]
            Time = s[2]
            GSD = node.get('GSD')
            samplePath = node.text
            from glob import glob
            count = len(glob(f'{samplePath}image/*.tif')) + len(glob(f'{samplePath}image/*.tiff'))
            sum += count
            BZ = s[4]
            from os.path import exists,dirname
            trainset_file = dirname(dirname(samplePath))+'/split/train_set.txt'
            if exists(trainset_file):
                with open(trainset_file,"r") as f:
                    lines = f.readline()
                    trainset_nums = lines.strip()
            else:
                print(f'{trainset_file}不存在')
            valset_file = dirname(dirname(samplePath))+'/split/val_set.txt'
            if exists(valset_file):
                with open(valset_file,"r") as f:
                    lines = f.readline()
                    valset_nums = lines.strip()
            else:
                print(f'{valset_file}不存在')
                valset_nums = 0
            ratio = None if int(valset_nums)==0 else f'{int(int(trainset_nums)/int(valset_nums)+0.5)}:1'
            Recall = node.get('Recall') if node.get('Recall') else None
            Acc = node.get('Acc') if node.get('Acc') else None
            Iou = node.get('IOU') if node.get('IOU') else None
            query.addBindValue(Name)
            query.addBindValue(Class)
            query.addBindValue(Country1)
            query.addBindValue(Country2)
            query.addBindValue(Type)
            query.addBindValue(Time)
            query.addBindValue(GSD)
            query.addBindValue(count)
            query.addBindValue(BZ)
            query.addBindValue(trainset_nums)
            query.addBindValue(valset_nums)
            query.addBindValue(ratio)
            query.addBindValue(Acc)
            query.addBindValue(Recall)
            query.addBindValue(Iou)
            # 在执行SQL后检查错误
            if not query.exec_():
                print("SQL错误:", query.lastError().text())
        # 提交事务
        if not db_samples.commit():
            print("提交失败:", db_samples.lastError().text()) 
        db_samples.close()
        time_end=time.time() 
        self.progress_bar.setText(f"处理完成: 花费时间 {((time_end-time_start)/60.0):.2f} 分钟") 

    def updateModelsDB(self):
        self.progress_bar.setText('开始处理...')
        import time
        time_start=time.time() 
        """初始化数据库连接"""
        connection_name = "connection_updateModelsDB"  # 自定义连接名称
        db_models = QSqlDatabase.addDatabase("QSQLITE",connection_name)
        db_models.setDatabaseName("databae_models.db")  # SQLite数据库文件
        
        if not db_models.open():
            show_info_message(self, "错误", "无法连接数据库")
            return False
            
        # 创建数据表（如果不存在）
        query = QSqlQuery(db_models)
        table_sql = """
            CREATE TABLE IF NOT EXISTS imported_data (
                序号 INTEGER PRIMARY KEY,
                名称 TEXT,
                类别 TEXT,
                分辨率 TEXT,
                网络 TEXT,
                轮数 INTEGER,
                `损失(train)` REAL,
                `精度(train)` REAL,
                `损失(val)` REAL,
                `查准(val)` REAL,
                `查全(val)` REAL,
                `IOU(val)` REAL                      
            )
            """
        if not query.exec_(table_sql):
            show_info_message(self, "错误", f"创建表失败: {query.lastError().text()}")
            return
         # 开始事务
        db_models.transaction()
        # 清空现有数据
        QSqlQuery("DELETE FROM imported_data", db_models)
        
        # 插入新数据
        query = QSqlQuery(db_models)
        # 插入数据
        insert_sql = """
        INSERT INTO imported_data 
        (名称, 类别, 分辨率, 网络, 轮数, `损失(train)`, `精度(train)`, `损失(val)`, `查准(val)`, `查全(val)`, `IOU(val)`) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        query.prepare(insert_sql)
        # 加载现有 XML
        from DeeplearningSystem import model_cofing_path
        tree = etree.parse(model_cofing_path)
        # 尝试获取节点
        nodes = tree.xpath(f'//ModelPath')
        # 名称, 类别, 分辨率, 网络, 轮数, `损失(train)`, `精度(train)`, `损失(val)`,  `查准(val)`, `查全(val)`, `IOU(val)`
        # desert_AUNet_256_epoch=74_train-loss=0.1796_train-acc=0.8176_val-loss=0.1323_val-acc=0.8651_val-recall=0.9555_val-iou=0.8311
        for index,node in enumerate(nodes):
            self.progress_bar.setText(f"开始处理: {int((index+1) * 100 / len(nodes))}%")
            Name = node.get('Name')
            Class = node.getparent().get('Name')
            GSD = node.get('GSD')
            Net = node.get('Net')          
            modelName = basename(node.text).rsplit('.',1)[0]        
            s = modelName.split('_')
            epoch = s[3].split('=')[1]
            trainloss = s[4].split('=')[1]
            trainacc = s[5].split('=')[1]
            valloss = s[6].split('=')[1]
            valacc = s[7].split('=')[1]
            valrecall = s[8].split('=')[1]
            valiou = s[9].split('=')[1]
            query.addBindValue(Name)
            query.addBindValue(Class)
            query.addBindValue(GSD)
            query.addBindValue(Net)
            query.addBindValue(epoch)
            query.addBindValue(trainloss)
            query.addBindValue(trainacc)
            query.addBindValue(valloss)
            query.addBindValue(valacc)
            query.addBindValue(valrecall)
            query.addBindValue(valiou)
            # 在执行SQL后检查错误
            if not query.exec_():
                print("SQL错误:", query.lastError().text())
        # 提交事务
        if not db_models.commit():
            print("提交失败:", db_models.lastError().text()) 
        db_models.close()
        QSqlDatabase.removeDatabase(connection_name)  # 移除自定义名称的连接
        time_end=time.time() 
        self.progress_bar.setText(f"处理完成: 花费时间 {((time_end-time_start)/60.0):.2f} 分钟") 

    # 关于
    def about(self):
        import json
        from cryptography.fernet import Fernet
        from DeeplearningSystem import key_path,lic_path
        # 从文件加载密钥
        with open(key_path, 'rb') as key_file:
            key = key_file.read()           
        # 创建Fernet对象
        fernet = Fernet(key)
        with open(lic_path, "rb") as f:
            encrypted_license = f.read()         
        license_json = fernet.decrypt(encrypted_license).decode()
        license_data = json.loads(license_json)
        software_version = license_data.get("software_version")
        user_id = license_data.get("user_id")
        expiration_date = license_data.get("expiration_date")
        info = f"软件信息：{self.title.split(' - ')[1] if self.title.find('-')>=0 else self.title}\n构建日期：2024-12-31\n版权所有：河南省地球物理空间信息研究院有限公司\n技术邮箱：malianwei2009@163.com\n许可截至：{expiration_date}"
        show_info_message(self, "提示", info)
    
    
    #############
    # 其它集成函数  
    #############
    
    # 加载栅格数据
    def addRaster(self, path):
        layer = QgsRasterLayer(path,basename(path))
        if not layer.isValid():
            show_info_message(self, '提示', '文件打开失败')
            return
        if self.firstAddLayer:
            self.canvas.setDestinationCrs(layer.crs())
            self.canvas.setExtent(layer.extent())
        #layer.dataProvider().setNoDataValue(1,0)
        while(self.project.mapLayersByName(layer.name())):
            layer.setName(layer.name()+"_1")
        self.project.addMapLayer(layer)
        layers = [layer] + [self.project.mapLayer(i) for i in self.project.mapLayers()]
        self.canvas.setLayers(layers)
        
        self.canvas.refresh()
        self.firstAddLayer = False
    
    # 加载矢量数据
    def addVector(self, path):
        layer = QgsVectorLayer(path,basename(path))
        if not layer.isValid():
            show_info_message(self, '提示', '文件打开失败')
            return   

        # 构造一个嵌入的渲染器
        
        fill_props = {}
        fill_props["color"] = QColor(0, 0, 0, 0)
        fill_props["color_border"] = 'red'
        fill = QgsFillSymbol.createSimple(fill_props)
        embededRenderer = QgsSingleSymbolRenderer(fill)

        # 构造 QgsInvertedPolygonRenderer，并赋给多边形图层
        renderer = QgsInvertedPolygonRenderer(embededRenderer)
        layer.setRenderer(renderer)

        if self.firstAddLayer:
            self.canvas.setDestinationCrs(layer.crs())
            self.canvas.setExtent(layer.extent())
        #layer.dataProvider().setNoDataValue(1,0)
        while(self.project.mapLayersByName(layer.name())):
            layer.setName(layer.name()+"_1")
        self.project.addMapLayer(layer)
        layers = [layer] + [self.project.mapLayer(i) for i in self.project.mapLayers()]
        self.canvas.setLayers(layers)

        self.canvas.refresh()
        self.firstAddLayer = False

    # 加载qgis工程
    def addProject(self, path):         
        # 尝试加载工程文件
        success = self.project.read(path)
        # 检查加载是否成功
        if not success:
            print(f"Failed to load project: {path}")
        else:
            print("Project loaded successfully")
        self.setWindowTitle(f"{basename(path).split('.')[0]} -{self.title.split(' - ')[1] if self.title.find('-')>=0 else self.title}")        
        QgsLayerTreeMapCanvasBridge(self.project.layerTreeRoot(), self.canvas)        
        # 从工程加载保存的范围
        extent_str = self.project.readEntry("ViewSettings", "LastExtent", "")[0]
        #print(extent_str)
        # 分割字符串
        parts = extent_str.split(":")
        min_coord = parts[0].strip().split(",")
        max_coord = parts[1].strip().split(",")     
        # 转换为浮点数并创建QgsRectangle
        xmin = float(min_coord[0])
        ymin = float(min_coord[1])
        xmax = float(max_coord[0])
        ymax = float(max_coord[1])    
        extent = QgsRectangle(xmin, ymin, xmax, ymax)     
        # 检查范围是否有效
        if extent.isFinite():
            self.canvas.setExtent(extent)
            self.canvas.refresh()
        else:
            print("保存的范围值无效")
        return success           
        
    #########
    # 其它事件  
    #########
     
    # 显示地图坐标（在状态栏显示）
    def showXY(self,point):
        if bool(self.project.mapLayers()):
            x = point.x()
            y = point.y()
            self.coordinate_label.setText(f'坐标：{x:.6f}, {y:.6f}')
        else:
            self.coordinate_label.setText('坐标：无数据')
    
    # 显示地图坐标系（在状态栏显示）
    def showCrs(self):
        mapSetting : QgsMapSettings = self.canvas.mapSettings()
        self.crs_label.setText(f"坐标系: {mapSetting.destinationCrs().description()}")
                       
    # 文件拖拽事件(支持文件拖拽到软件中)
    def dragEnterEvent(self, fileData):
        if fileData.mimeData().hasUrls():
            fileData.accept()
        else:
            fileData.ignore()

    # 拖拽文件事件
    def dropEvent(self,fileData):
        mimeData: QMimeData = fileData.mimeData()
        filePathList = [u.path()[1:] for u in mimeData.urls()]
        for filePath in filePathList:
            filePath:str = filePath.replace("/","//")
            if filePath.split(".")[-1] in ["tif","TIF","tiff","TIFF","GTIFF","png","jpg","pdf","img"]:
                self.addRaster(filePath)
            elif filePath.split(".")[-1] in ["shp","SHP","gpkg","geojson","kml"]:
                self.addVector(filePath)
            elif filePath.split(".")[-1] in ["qgs"]:
                self.addProject(filePath)
            elif filePath == "":
                pass
            else:
                show_info_message(self, '警告', f'{filePath}为不支持的文件类型，目前支持栅格影像和shp矢量')

    def catch_exceptions(self, ty, value, trace):
        """
            捕获异常，并弹窗显示
        :param ty: 异常的类型
        :param value: 异常的对象
        :param traceback: 异常的traceback
        """
        traceback_format = traceback.format_exception(ty, value, trace)
        traceback_string = "".join(traceback_format)
        QMessageBox.about(self, 'error', traceback_string)
        self.old_hook(ty, value, trace)
