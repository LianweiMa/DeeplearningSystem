# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt
from ui.MakeSamplesUI import Ui_Dialog


class MakeSamplesDialog(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)  # 调用setupUi方法初始化界面
        
        # 在这里添加你的逻辑代码
        from os.path import join
        from DeeplearningSystem import base_dir
        png = join(base_dir, 'settings/icon', 'MakeSample.png') 
        icon = QIcon()
        icon.addPixmap(QPixmap(png), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)
        self.setWindowFlags(self.windowFlags() & ~(Qt.WindowContextHelpButtonHint))

        self.pushButton_OpenImageFile.clicked.connect(self.on_openImageFile_clicked)
        self.pushButton_OpenLabelFile.clicked.connect(self.on_openLabelFile_clicked)
        self.pushButton_OpenBoundaryFile.clicked.connect(self.on_openBoundaryFile_clicked)          
        self.pushButton_OpenSamplePath.clicked.connect(self.on_saveSamplePath_clicked)  
        self.comboBox_sampleClass.addItems(["building", "road", "mine", "water", "forest", "pv", "greenhouse", "desert"])     
        self.comboBox_sampleClass.setCurrentIndex(-1)

    def on_openImageFile_clicked(self,Dialog):
        from qgis.PyQt.QtWidgets import QFileDialog
        path_to_tif,_ = QFileDialog.getOpenFileName(None, '打开', '', 'Raster Files (*.tif;*.tiff;*.img;*.dat);;All Files (*.*)')
        if  path_to_tif=="":
            return
        self.lineEdit_image.setText(path_to_tif)
        from osgeo import gdal
        gdal.UseExceptions()
        dataset = gdal.Open(path_to_tif)
        if dataset is None:
            raise Exception("无法打开栅格文件")

        # 获取地理变换参数
        geotransform = dataset.GetGeoTransform()
        if geotransform is None:
            raise Exception("无法获取地理变换参数")
        # 提取分辨率
        pixel_size = abs(geotransform[1])  # X 方向分辨率
        self.lineEdit_sampleGSD.setText(str(pixel_size))
        dataset = None

    def on_openLabelFile_clicked(self,Dialog):
        from qgis.PyQt.QtWidgets import QFileDialog
        path_to_vec,_ = QFileDialog.getOpenFileName(None, '打开', '', 'Shape Files (*.shp);;All Files (*.*)')
        if  path_to_vec=="":
            return
        self.lineEdit_label.setText(path_to_vec)

    def on_openBoundaryFile_clicked(self,Dialog):
        from qgis.PyQt.QtWidgets import QFileDialog
        path_to_vec,_ = QFileDialog.getOpenFileName(None, '打开', '', 'Shape Files (*.shp);;All Files (*.*)')
        if  path_to_vec=="":
            return
        self.lineEdit_boundary.setText(path_to_vec)

    def on_saveSamplePath_clicked(self,Dialog):
        from qgis.PyQt.QtWidgets import QFileDialog
        folder_selected = QFileDialog.getExistingDirectory(None, "Select Folder to Save")
        if  folder_selected:
            self.lineEdit_saveSamplePath.setText(folder_selected)