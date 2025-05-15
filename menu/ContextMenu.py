from qgis.PyQt.QtWidgets import QMenu, QAction,QMessageBox
from qgis.core import QgsLayerTreeNode, QgsLayerTree, QgsMapLayerType, QgsProject, QgsLayerTreeGroup,QgsMapLayer
from qgis.gui import QgsLayerTreeViewMenuProvider, QgsLayerTreeView, QgsLayerTreeViewDefaultActions, QgsMapCanvas
from dialog.VectorLayerAttributeDialog import VectorLayerAttributeDialog
from tools.CommonTool import show_info_message, show_question_message

class CustomMenuProvider(QgsLayerTreeViewMenuProvider):
    def __init__(self, mainWindow, layerTreeView: QgsLayerTreeView, mapCanvas: QgsMapCanvas, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layerTreeView = layerTreeView
        self.mapCanvas = mapCanvas
        self.mainWindow = mainWindow

    def createContextMenu(self):
        menu = QMenu()
        actions: QgsLayerTreeViewDefaultActions = self.layerTreeView.defaultActions()
        if not self.layerTreeView.currentIndex().isValid():
            # 不在图层上右键
            # 清除图层 deleteAllLayer
            actionDeleteAllLayer = QAction('清除图层', menu)
            actionDeleteAllLayer.triggered.connect(lambda: self.deleteAllLayer())
            menu.addAction(actionDeleteAllLayer)
            self.actionAddGroup = actions.actionAddGroup(menu)
            menu.addAction(self.actionAddGroup)
            menu.addAction('展开所有图层', self.layerTreeView.expandAll)
            menu.addAction('折叠所有图层', self.layerTreeView.collapseAll)
            return menu

        node: QgsLayerTreeNode = self.layerTreeView.currentNode()
        if QgsLayerTree.isGroup(node):
            # 图组操作
            #print('group')
            group: QgsLayerTreeGroup = self.layerTreeView.currentGroupNode()
            self.actionRenameGroup = actions.actionRenameGroupOrLayer(menu)
            menu.addAction(self.actionRenameGroup)
            actionDeleteGroup = QAction('删除选中组', menu)
            actionDeleteGroup.triggered.connect(lambda: self.deleteGroup(group))
            menu.addAction(actionDeleteGroup)
        elif QgsLayerTree.isLayer(node):
            #print('layer')
            #ZoomToLayer
            self.actionZoomToLayer = actions.actionZoomToLayer(self.mapCanvas, menu)
            menu.addAction(self.actionZoomToLayer)
            #MoveToTop
            self.actionMoveToTop = actions.actionMoveToTop(menu)
            menu.addAction(self.actionMoveToTop)      
            # 图层属性
            layer: QgsMapLayer = self.layerTreeView.currentLayer()
            actionOpenLayerProp = QAction('图层属性', menu)
            actionOpenLayerProp.triggered.connect(lambda : self.openLayerPropTriggered(layer))
            menu.addAction(actionOpenLayerProp)

            if layer.type() == QgsMapLayerType.VectorLayer:
                # 矢量图层
                openAttributeDialog = QAction('打开属性表', menu)
                openAttributeDialog.triggered.connect(lambda: self.openAttributeDialog(layer))
                menu.addAction(openAttributeDialog)
            else:
                # 栅格图层
                pass
            if len(self.layerTreeView.selectedLayers()) >= 1:
                # 添加组
                #print('selectedLayers')
                self.actionGroupSelected = actions.actionGroupSelected()
                menu.addAction(self.actionGroupSelected)
            
                actionDeleteSelectedLayers = QAction('删除选中图层',menu)
                actionDeleteSelectedLayers.triggered.connect(self.deleteSelectedLayer)
                menu.addAction(actionDeleteSelectedLayers)   
                    
        else:
            print('node type is none')       
        return menu

    def openAttributeDialog(self,layer):
            self.mainWindow.ad = VectorLayerAttributeDialog(self.mainWindow, layer)
            self.mainWindow.ad.show()

    def deleteSelectedLayer(self):
        deleteRes = show_question_message(self.mainWindow, '信息', "确定要删除所选图层？")
        if deleteRes == QMessageBox.Yes:
            layers = self.layerTreeView.selectedLayers()
            for layer in layers:
                self.deleteLayer(layer)

    def deleteLayer(self,layer):
        QgsProject.instance().removeMapLayer(layer)
        self.mapCanvas.refresh()
        return 0
    
    def deleteAllLayer(self):
        if len(QgsProject.instance().mapLayers().values()) == 0:
            show_info_message(self.mainWindow, '信息', '您的图层为空')
        else:
            deleteRes = show_question_message(self.mainWindow, '信息', "确定要删除所有图层？")
            if deleteRes == QMessageBox.Yes:
                for layer in QgsProject.instance().mapLayers().values():
                        self.deleteLayer(layer)
                self.mainWindow.firstAddLayer = True
    
    def deleteGroup(self,group:QgsLayerTreeGroup):
        deleteRes = show_info_message(self.mainWindow, '信息', "确定要删除选中组？")
        if deleteRes == QMessageBox.Yes:
            layerTreeLayers  = group.findLayers()
            for layer in layerTreeLayers:
                self.deleteLayer(layer.layer())
        QgsProject.instance().layerTreeRoot().removeChildNode(group)

    def openLayerPropTriggered(self,layer):
        try:
            from dialog.LayerAttributeDialog import LayerAttributeDialog
            self.lp = LayerAttributeDialog(layer,self.mainWindow)
            #print(type(self.lp))
            self.lp.show()
        except:
            import traceback
            print(traceback.format_exc())