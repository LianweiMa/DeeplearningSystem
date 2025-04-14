# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt
from ui.PostProcessUI import Ui_Dialog


class PostProcessDialog(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)  # 调用setupUi方法初始化界面
        
        # 在这里添加你的逻辑代码
        from os.path import join
        from DeeplearningSystem import base_dir
        png = join(base_dir, 'settings/icon', 'ImgClass_Post_Clump.png') 
        icon = QIcon()
        icon.addPixmap(QPixmap(png), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)
        self.setWindowFlags(self.windowFlags() & ~(Qt.WindowContextHelpButtonHint))


        self.pushButton_openImage.clicked.connect(self.on_openImage_clicked)####################
        self.pushButton_saveImage.clicked.connect(self.on_saveImage_clicked)###################

        self.__initial__()

    def __initial__(self):
        from qgis.core import QgsProject, QgsRasterLayer, QgsVectorLayer
        #清空
        self.comboBox_openImage.clear()
        self.comboBox_openImage.currentIndex = -1
        for _, layer in QgsProject.instance().mapLayers().items():
            if isinstance(layer, QgsRasterLayer):
                filepath = layer.dataProvider().dataSourceUri()
                self.comboBox_openImage.addItem(filepath)

    def on_openImage_clicked(self,Dialog):
        from qgis.PyQt.QtWidgets import QFileDialog
        path_to_tif,_ = QFileDialog.getOpenFileName(None, '打开', '', 'Raster Files (*.img);;All Files (*.*)')
        if  path_to_tif=="":
            return
        self.comboBox_openImage.setCurrentText(path_to_tif)

    def on_saveImage_clicked(self,Dialog):
        from qgis.PyQt.QtWidgets import QFileDialog
        path_to_tif,_ = QFileDialog.getSaveFileName(None, '保存', '', 'Raster Files (*.img);;All Files (*.*)')
        if  path_to_tif=="":
            return
        self.lineEdit_saveImage.setText(path_to_tif)
