# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QDialog, QFileDialog
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt
import geopandas as gpd
from tools.CommonTool import show_info_message
from ui.MakeSamplesUI import Ui_Dialog


class MakeSamplesDialog(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)  # 调用setupUi方法初始化界面
        
        # 在这里添加你的逻辑代码
        from os.path import join
        from DeeplearningSystem import base_dir
        png = join(base_dir, 'settings/icon', 'label_create.png') 
        icon = QIcon()
        icon.addPixmap(QPixmap(png), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)
        self.setWindowFlags(self.windowFlags() & ~(Qt.WindowContextHelpButtonHint))

        self.pushButton_OpenImageFile.clicked.connect(self.openImageFile_clicked)
        self.pushButton_OpenLabelFile.clicked.connect(self.openLabelFile_clicked)
        self.pushButton_OpenBoundaryFile.clicked.connect(self.openBoundaryFile_clicked)          
        self.pushButton_OpenSamplePath.clicked.connect(self.saveSamplePath_clicked)  
        self.comboBox_sampleClass.addItems(["building", "road", "mine", "water", "forest", "pv", "greenhouse", "desert"])     
        self.comboBox_sampleClass.setCurrentIndex(-1)

    def openImageFile_clicked(self,Dialog):
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

    def openLabelFile_clicked(self,Dialog):
        path,_ = QFileDialog.getOpenFileName(None, '打开', '', 'Shape Files (*.shp);;All Files (*.*)')
        if  path=="":
            return
        
        # 读取矢量文件
        gdf = gpd.read_file(path)
        # 检查 'NewField' 是否已经存在
        if 'ClassID' not in gdf.columns:
            show_info_message(self,"样本制作","标签矢量文件需要ClassID字段，但该矢量不存在该字段！")
            return
        self.lineEdit_label.setText(path)

    def openBoundaryFile_clicked(self,Dialog):
        path,_ = QFileDialog.getOpenFileName(None, '打开', '', 'Shape Files (*.shp);;All Files (*.*)')
        if  path=="":
            return
        
         # 读取矢量文件
        gdf = gpd.read_file(path)
        # 检查 'NewField' 是否已经存在
        if 'Name' not in gdf.columns:
            show_info_message(self,"样本制作","标签矢量文件需要Name字段，但该矢量不存在该字段！")
            return
        self.lineEdit_boundary.setText(path)

    def saveSamplePath_clicked(self,Dialog):
        folder_selected = QFileDialog.getExistingDirectory(None, "Select Folder to Save")
        if  folder_selected:
            self.lineEdit_saveSamplePath.setText(folder_selected)