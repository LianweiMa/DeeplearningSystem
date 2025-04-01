
from qgis.PyQt import QtCore, QtGui, QtWidgets
from qgis.PyQt.QtWidgets import QDialog, QHBoxLayout,QDockWidget,QVBoxLayout,QDesktopWidget,QMessageBox
from qgis.core import QgsVectorLayerCache,QgsVectorLayer
from qgis.gui import QgsAttributeTableView, QgsAttributeTableModel, QgsAttributeTableFilterModel,QgsGui

class VectorLayerAttributeDialog(QDialog):
    def __init__(self, mainWindows, layer):
        #mainWindows : MainWindow
        super(VectorLayerAttributeDialog, self).__init__(mainWindows)
        self.mainWindows = mainWindows
        self.mapCanvas = self.mainWindows.canvas
        self.layer : QgsVectorLayer = layer
        self.setObjectName("attrWidget"+self.layer.id())
        self.setWindowTitle("属性表:"+self.layer.name())
        vl = QHBoxLayout(self)
        self.tableView = QgsAttributeTableView(self)   
        self.tableView.doubleClicked.connect(self.on_double_click)# 连接双击信号到槽函数
        self.resize(800, 600)
        vl.addWidget(self.tableView)
        self.center()
        self.openAttributeDialog()
        QgsGui.editorWidgetRegistry().initEditors(self.mapCanvas)

        self.setWindowFlags(self.windowFlags() & ~(QtCore.Qt.WindowContextHelpButtonHint)) # 隐藏对话框标题栏默认的问号按钮

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
        self.tableModel.loadLayer()

        self.tableFilterModel = QgsAttributeTableFilterModel(self.mapCanvas, self.tableModel, parent=self.tableModel)
        self.tableFilterModel.setFilterMode(QgsAttributeTableFilterModel.ShowAll)  #显示问题
        self.tableView.setModel(self.tableFilterModel)
        #self.tableView.edit()
        #print(self.tableView.currentIndex())

    def on_double_click(self,index):
        # 获取当前选中的行
        #row = index.row()
        # 获取当前行的属性值
        #layer = self.tableView.layer()
        #feature = layer.getFeature(row)
        if not self.layer.isEditable():
            QMessageBox.information(self.tableView, "信息", "如要编辑属性，请打开图层编辑状态！", QMessageBox.Ok)
