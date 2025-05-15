# -*- coding: utf-8 -*-

from qgis.core import QgsVectorLayer,QgsRasterLayer,QgsStyle,QgsRasterDataProvider,QgsVectorDataProvider,QgsRectangle,QgsCoordinateReferenceSystem,QgsWkbTypes
from qgis.gui import QgsRendererRasterPropertiesWidget,QgsSingleSymbolRendererWidget,QgsCategorizedSymbolRendererWidget
from PyQt5.QtWidgets import QDialog, QListWidgetItem, QTabBar
import os.path as osp
from PyQt5.QtCore import Qt
from qgis.core import QgsFeature
from ui.LayerAttributeUI import Ui_Dialog


class LayerAttributeDialog(QDialog, Ui_Dialog):
    def __init__(self,layer,parent=None):
        """
        # tab 信息含义：
        0 栅格信息 1 矢量信息 2 栅格图层渲染 3 矢量图层渲染
        :param layer:
        :param parent:
        """
        super(LayerAttributeDialog,self).__init__(parent)
        self.layer = layer
        self.parentWindow = parent
        self.setupUi(self)
        self.initUI()
        self.connectFunc()

        # 在这里添加你的逻辑代码
        self.setWindowFlags(self.windowFlags() & ~(Qt.WindowContextHelpButtonHint))

    def initUI(self):
        layerbar = self.tabWidget.findChild(QTabBar)
        layerbar.hide()
        renderBar = self.comboTabWidget.findChild(QTabBar)
        renderBar.hide()
        self.listWidget.setCurrentRow(0)
        self.initInfomationTab()
        self.decideRasterNVector(0)

    def connectFunc(self):
        self.listWidget.itemClicked.connect(self.listWidgetItemClicked)
        self.okPb.clicked.connect(lambda : self.renderApplyPbClicked(needClose=True))
        self.cancelPb.clicked.connect( self.close )
        self.applyPb.clicked.connect(lambda : self.renderApplyPbClicked(needClose=False))
        self.vecterRenderCB.currentIndexChanged.connect(self.vecterRenderCBChanged)

    # 切换矢量渲染方式
    def vecterRenderCBChanged(self):
        self.comboTabWidget.setCurrentIndex(self.vecterRenderCB.currentIndex())

    def initInfomationTab(self):
        if type(self.layer) == QgsRasterLayer:
            rasterLayerDict = getRasterLayerAttrs(self.layer)
            self.rasterNameLabel.setText(rasterLayerDict['name'])
            self.rasterSourceLabel.setText(rasterLayerDict['source'])
            self.rasterMemoryLabel.setText(rasterLayerDict['memory'])
            self.rasterExtentLabel.setText(rasterLayerDict['extent'])
            self.rasterWHLabel.setText(f"{rasterLayerDict['width']},{rasterLayerDict['height']}")
            self.rasterGSDLabel.setText(f"{rasterLayerDict['gsdX']},{rasterLayerDict['gsdY']}")
            self.rasterDataTypeLabel.setText(rasterLayerDict['dataType'])
            self.rasterBandNumLabel.setText(rasterLayerDict['bands'])
            self.rasterCrsLabel.setText(rasterLayerDict['crs'])
            self.rasterRenderWidget = QgsRendererRasterPropertiesWidget(self.layer, self.parentWindow.canvas,parent=self) 

            from qgis.PyQt.QtWidgets import QScrollArea
            # 创建滚动区域
            self.scroll_area = QScrollArea()
            # 将rasterWidget放入滚动区域
            self.scroll_area.setWidget(self.rasterRenderWidget)
            # 根据内容大小自动调整滚动区域大小
            self.scroll_area.setWidgetResizable(True)
            # 显示滚动区域
            self.scroll_area.show()

            self.layerRenderLayout.addWidget(self.scroll_area)           

        elif type(self.layer) == QgsVectorLayer:
            self.layer : QgsVectorLayer
            vectorLayerDict = getVectorLayerAttrs(self.layer)
            self.vectorNameLabel.setText(vectorLayerDict['name'])
            self.vectorSourceLabel.setText(vectorLayerDict['source'])
            self.vectorMemoryLabel.setText(vectorLayerDict['memory'])
            self.vectorExtentLabel.setText(vectorLayerDict['extent'])
            self.vectorGeoTypeLabel.setText(vectorLayerDict['geoType'])
            self.vectorFeatureNumLabel.setText(vectorLayerDict['featureNum'])
            self.vectorEncodingLabel.setText(vectorLayerDict['encoding'])
            self.vectorCrsLabel.setText(vectorLayerDict['crs'])
            self.vectorDpLabel.setText(vectorLayerDict['dpSource'])

            # single Render
            self.vectorSingleRenderWidget = QgsSingleSymbolRendererWidget(self.layer,QgsStyle.defaultStyle(),self.layer.renderer())
            self.singleRenderLayout.addWidget(self.vectorSingleRenderWidget)

            # category Render
            self.vectorCateGoryRenderWidget = QgsCategorizedSymbolRendererWidget(self.layer,QgsStyle.defaultStyle(),self.layer.renderer())
            self.cateRenderLayout.addWidget(self.vectorCateGoryRenderWidget)

    def decideRasterNVector(self,index):
        if index == 0:
            if type(self.layer) == QgsRasterLayer:
                self.tabWidget.setCurrentIndex(0)
            elif type(self.layer) == QgsVectorLayer:
                self.tabWidget.setCurrentIndex(1)
        elif index == 1:
            if type(self.layer) == QgsRasterLayer:
                self.tabWidget.setCurrentIndex(2)
            elif type(self.layer) == QgsVectorLayer:
                self.tabWidget.setCurrentIndex(3)


    def listWidgetItemClicked(self,item:QListWidgetItem):
        tempIndex = self.listWidget.indexFromItem(item).row()
        self.decideRasterNVector(tempIndex)


    def renderApplyPbClicked(self,needClose=False):
        if self.tabWidget.currentIndex() <= 1:
            print("没有在视图里，啥也不干")
        elif type(self.layer) == QgsRasterLayer:
            self.rasterRenderWidget : QgsRendererRasterPropertiesWidget
            self.rasterRenderWidget.apply()
        elif type(self.layer) == QgsVectorLayer:
            print("矢量渲染")
            #self.vectorRenderWidget : QgsSingleSymbolRendererWidget
            self.layer : QgsVectorLayer
            if self.comboTabWidget.currentIndex() == 0:
                renderer = self.vectorSingleRenderWidget.renderer()
            else:
                renderer = self.vectorCateGoryRenderWidget.renderer()
            self.layer.setRenderer(renderer)
            self.layer.triggerRepaint()
        self.parentWindow.canvas.refresh()
        if needClose:
            self.close()

qgisDataTypeDict = {
    0 : "UnknownDataType",
    1 : "Uint8",
    2 : "UInt16",
    3 : "Int16",
    4 : "UInt32",
    5 : "Int32",
    6 : "Float32",
    7 : "Float64",
    8 : "CInt16",
    9 : "CInt32",
    10 : "CFloat32",
    11 : "CFloat64",
    12 : "ARGB32",
    13 : "ARGB32_Premultiplied"
}

def getFileSize(filePath):
    fsize = osp.getsize(filePath)  # 返回的是字节大小

    if fsize < 1024:
        return f"{round(fsize, 2)}Byte"
    else:
        KBX = fsize / 1024
        if KBX < 1024:
            return f"{round(KBX, 2)}Kb"
        else:
            MBX = KBX / 1024
            if MBX < 1024:
                return f"{round(MBX, 2)}Mb"
            else:
                return f"{round(MBX/1024,2)}Gb"
            
def getRasterLayerAttrs(rasterLayer:QgsRasterLayer):

    rdp : QgsRasterDataProvider = rasterLayer.dataProvider()
    crs : QgsCoordinateReferenceSystem = rasterLayer.crs()
    extent: QgsRectangle = rasterLayer.extent()
    resDict = {
        "name" : rasterLayer.name(),
        "source" : osp.dirname(rasterLayer.source()),
        "memory" : getFileSize(rasterLayer.source()),
        "extent" : f"min:[{extent.xMinimum():.6f},{extent.yMinimum():.6f}]; max:[{extent.xMaximum():.6f},{extent.yMaximum():.6f}]",
        "width" : f"{rasterLayer.width()}",
        "height" : f"{rasterLayer.height()}",
        "dataType" : qgisDataTypeDict[rdp.dataType(1)],
        "bands" : f"{rasterLayer.bandCount()}",
        "crs" : crs.description(),
        "gsdX" : f"{rasterLayer.rasterUnitsPerPixelX()}",
        "gsdY" : f"{rasterLayer.rasterUnitsPerPixelY()}"
    }
    return resDict

def getVectorLayerAttrs(vectorLayer:QgsVectorLayer):
    vdp : QgsVectorDataProvider = vectorLayer.dataProvider()
    crs: QgsCoordinateReferenceSystem = vectorLayer.crs()
    extent: QgsRectangle = vectorLayer.extent()
    resDict = {
        "name" : vectorLayer.name(),
        "source" : osp.dirname(vectorLayer.source()),
        "memory": getFileSize(vectorLayer.source()),
        "extent" : f"min:[{extent.xMinimum():.6f},{extent.yMinimum():.6f}]; max:[{extent.xMaximum():.6f},{extent.yMaximum():.6f}]",
        "geoType" : QgsWkbTypes.geometryDisplayString(vectorLayer.geometryType()),
        "featureNum" : f"{vectorLayer.featureCount()}",
        "encoding" : vdp.encoding(),
        "crs" : crs.description(),
        "dpSource" : vdp.description()
    }
    return resDict



