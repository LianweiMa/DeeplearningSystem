
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QDialog, QHBoxLayout, QDesktopWidget
from qgis.core import QgsVectorLayerCache,QgsVectorLayer
from qgis.gui import QgsAttributeTableView, QgsAttributeTableModel, QgsAttributeTableFilterModel,QgsGui
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt
from tools.CommonTool import show_info_message


class VectorLayerAttributeDialog(QDialog):
    def __init__(self, mainWindows, layer):
        #mainWindows : MainWindow
        super(VectorLayerAttributeDialog, self).__init__(mainWindows)
        self.mainWindows = mainWindows
        self.mapCanvas = self.mainWindows.canvas
        self.layer : QgsVectorLayer = layer
        self.setObjectName("attrWidget"+self.layer.id())
        self.setWindowTitle("属性表 - "+self.layer.name())
        vl = QHBoxLayout(self)
        self.tableView = QgsAttributeTableView(self)   
        self.tableView.doubleClicked.connect(self.double_click)# 连接双击信号到槽函数  
        self.resize(800, 600)
        vl.addWidget(self.tableView)
        self.center()
        self.openAttributeDialog()
        QgsGui.editorWidgetRegistry().initEditors(self.mapCanvas)

        # 在这里添加你的逻辑代码
        from os.path import join
        from DeeplearningSystem import base_dir
        png = join(base_dir, 'settings/icon', 'VectorEditor_BatchAttributeEdit.png') 
        icon = QIcon()
        icon.addPixmap(QPixmap(png), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)
        self.setWindowFlags(self.windowFlags() & ~(Qt.WindowContextHelpButtonHint))

    def center(self):
        # 获取屏幕的尺寸信息
        screen = QDesktopWidget().screenGeometry()
        # 获取窗口的尺寸信息
        size = self.geometry()
        # 将窗口移动到指定位置
        self.move(int((screen.width() - size.width()) / 2), int((screen.height() - size.height()) / 2))

    def openAttributeDialog(self):
        #iface
        self.layerCache = QgsVectorLayerCache(self.layer, 10000)
        self.tableModel = QgsAttributeTableModel(self.layerCache)
        self.tableView.selectionModel().selectionChanged.connect(self.selection_changed)
        self.tableModel.loadLayer()

        self.tableFilterModel = QgsAttributeTableFilterModel(self.mapCanvas, self.tableModel, parent=self.tableModel)
        self.tableFilterModel.setFilterMode(QgsAttributeTableFilterModel.ShowAll)  #显示问题
        self.tableView.setModel(self.tableFilterModel)
        #self.tableView.edit()
        #print(self.tableView.currentIndex())

    def double_click(self,index):
        # 获取当前选中的行
        #row = index.row()
        # 获取当前行的属性值
        #layer = self.tableView.layer()
        #feature = layer.getFeature(row)
        if not self.layer.isEditable():
            show_info_message(self.tableView, "信息", "如要编辑属性，请打开图层编辑状态！")

    def selection_changed(self,selected, deselected):
        self.mainWindows.actionClearSelection.setEnabled(False)
