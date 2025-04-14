from qgis.PyQt.QtCore import QThread, pyqtSignal
 
class MakeSampleThread(QThread):
    finished = pyqtSignal(object)  # 用于将数据从子线程发送到主线程的信号

    def __init__(self, ui, progress_bar):
        super().__init__()
        self.ui = ui
        self.progress_bar = progress_bar

    def run(self):
        # 在这里执行耗时任务，并使用self.param
        result = self.do_work()
        self.finished.emit(result)  # 发送信号，并将结果作为参数传递

    def do_work(self):
        import time
        from osgeo import gdal,ogr,osr
        import shutil
        from os.path import dirname,basename
        from os import mkdir
        from os.path import exists
        time_start=time.time()

        self.progress_bar.setText('开始处理...')
        image_file = self.ui.lineEdit_image.text()
        label_file = self.ui.lineEdit_label.text()
        boundaryfile = self.ui.lineEdit_boundary.text()
        samplePath = self.ui.lineEdit_saveSamplePath.text()
        sampleClass = self.ui.comboBox_sampleClass.currentText()

        dataset = gdal.Open(image_file)
        if dataset is None:
            raise Exception("无法打开栅格文件")

        # 获取地理变换参数
        geotransform = dataset.GetGeoTransform()
        if geotransform is None:
            raise Exception("无法获取地理变换参数")
        # 提取分辨率
        pixel_size = abs(geotransform[1])  # X 方向分辨率
        dataset = None

        name = basename(boundaryfile).split('.')[0]
        dbf = dirname(boundaryfile)+'/'+name+'.dbf'
        shutil.copy(dbf,f'{samplePath}/SamplesRange.dbf')
        prj = dirname(boundaryfile)+'/'+name+'.prj'
        shutil.copy(prj,f'{samplePath}/SamplesRange.prj')
        shutil.copy(boundaryfile,f'{samplePath}/SamplesRange.shp')
        shx = dirname(boundaryfile)+'/'+name+'.shx'
        shutil.copy(shx,f'{samplePath}/SamplesRange.shx')

        if (exists(samplePath+'/image/')!=True):
            mkdir(samplePath+'/image/')
        if (exists(samplePath+'/label/')!=True):
            mkdir(samplePath+'/label/')
        if (exists(samplePath+'/vector/')!=True):
            mkdir(samplePath+'/vector/')

        driver = ogr.GetDriverByName("ESRI Shapefile")
        data_source:ogr.DataSource = driver.Open(boundaryfile, 0)  # 0只读模式
        if data_source is None:
            print("无法打开文件")
        else:
            layer = data_source.GetLayer()

        # 获取输入图层的几何类型和字段定义
        geom_type = layer.GetGeomType()
        spatial_ref = layer.GetSpatialRef()
        layer_defn = layer.GetLayerDefn()
        feature_count = layer.GetFeatureCount()

        # 遍历每个要素
        for index,feature in enumerate(layer):
            self.progress_bar.setText(f"开始处理: {int((index+1) * 100 / feature_count)}%")
            # 确定输出文件名
            feature_name  = feature.GetField("Name")
            range_file = f'{samplePath}/vector/{feature_name}_range.shp'
            # 创建输出Shapefile  
            driver = ogr.GetDriverByName("ESRI Shapefile")         
            if exists(range_file):
                driver.DeleteDataSource(range_file)
            out_ds = driver.CreateDataSource(range_file)
            out_layer = out_ds.CreateLayer("feature", srs=spatial_ref, geom_type=geom_type)

            # 复制字段定义
            for i in range(layer_defn.GetFieldCount()):
                field_defn = layer_defn.GetFieldDefn(i)
                out_layer.CreateField(field_defn)

            # 创建新要素并复制几何和属性
            out_feature = ogr.Feature(out_layer.GetLayerDefn())
            out_feature.SetGeometry(feature.GetGeometryRef().Clone())
            for i in range(feature.GetFieldCount()):
                out_feature.SetField(i, feature.GetField(i))
            out_layer.CreateFeature(out_feature)

            # 清理资源
            out_feature = None
            out_ds = None
            #print("要素提取完成！")

            rasterclip_file = f'{samplePath}/image/{feature_name }.tif'
            # 打开矢量数据
            vector_ds = ogr.Open(range_file)
            vector_layer = vector_ds.GetLayer()

            # 设置裁剪选项
            options = gdal.WarpOptions(
                cutlineDSName=range_file,  # 裁剪范围
                cropToCutline=True,  # 裁剪到范围边界
                dstNodata=0  # NoData 值
            )

            # 裁剪栅格影像
            gdal.Warp(
                rasterclip_file,
                image_file,
                options=options
            )

            # 清理资源
            vector_ds = None

            #print("栅格影像裁剪完成！")

            intersect_file = f'{samplePath}/vector/{feature_name }.shp'
            import geopandas as gpd

            # 读取两个矢量文件
            gdf1 = gpd.read_file(range_file)
            gdf2 = gpd.read_file(label_file)

            # 确保坐标系一致
            gdf2 = gdf2.to_crs(gdf1.crs)

            # 计算相交
            intersection = gpd.overlay(gdf1, gdf2, how="intersection",keep_geom_type=False)

            # 保存结果
            intersection.to_file(intersect_file)

            #print("相交操作完成！")

            union_file = f'{samplePath}/vector/{feature_name }_union.shp'

            # 读取两个矢量数据
            gdf3 = gpd.read_file(intersect_file)  

            # 确保坐标系一致
            if gdf1.crs != gdf3.crs:
                gdf3 = gdf3.to_crs(gdf1.crs)

            # 计算并集
            union_gdf = gpd.overlay(gdf1, gdf3, how="union")

            # 保存并集结果
            union_gdf.to_file(union_file)

            #print("并集操作完成！")


            # 输出栅格文件路径
            raster_file = f'{samplePath}/label/{feature_name }.tif'
            # 输出栅格的分辨率（单位：与矢量坐标系一致）
            # 输出栅格的 NoData 值
            no_data_value = -9999
            # 输出栅格的字段名（用于栅格化时的值）
            attribute_field = "ClassID"  # 矢量文件中的字段名

            # 打开矢量文件
            vector_ds = ogr.Open(union_file)
            vector_layer = vector_ds.GetLayer()

            # 获取矢量图层的范围
            x_min, x_max, y_min, y_max = vector_layer.GetExtent()

            # 计算输出栅格的行列数
            x_res = int((x_max - x_min) / pixel_size + 0.5)
            y_res = int((y_max - y_min) / pixel_size + 0.5)

            # 创建输出栅格文件
            driver = gdal.GetDriverByName("GTiff")
            raster_ds = driver.Create(raster_file, x_res, y_res, 1, gdal.GDT_Byte)  # 1 表示单波段
            raster_ds.SetGeoTransform((x_min, pixel_size, 0, y_max, 0, -pixel_size))  # 设置地理变换

            # 设置投影
            srs = osr.SpatialReference()
            srs.ImportFromWkt(vector_layer.GetSpatialRef().ExportToWkt())
            raster_ds.SetProjection(srs.ExportToWkt())

            # 获取栅格波段
            band = raster_ds.GetRasterBand(1)
            band.SetNoDataValue(no_data_value)  # 设置 NoData 值
            band.FlushCache()

            # 栅格化矢量图层
            gdal.RasterizeLayer(
                raster_ds,  # 输出栅格数据集
                [1],  # 波段列表
                vector_layer,  # 矢量图层
                burn_values=[1],  # 栅格化时的值（如果使用字段值，则设置为 None）
                options=[f"ATTRIBUTE={attribute_field}"]  # 使用矢量字段值作为栅格值
            )

            # 清理资源
            raster_ds = None
            vector_ds = None

            #print("矢量转栅格完成！")

        # 关闭输入文件
        data_source = None

        #print(f"处理完成！")
        time_end = time.time()
        self.progress_bar.setText(f"处理完成: 花费时间 {((time_end-time_start)/60.0):.2f} 分钟") 
        return sampleClass,samplePath              