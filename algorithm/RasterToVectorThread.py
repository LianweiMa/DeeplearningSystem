from qgis.PyQt.QtCore import QThread, pyqtSignal
 
class RasterToVectorThread(QThread):
    finished = pyqtSignal(object)  # 用于将数据从子线程发送到主线程的信号
    # 添加信号
    progress_signal = pyqtSignal(str)
    def __init__(self, ui):
        super().__init__()
        self.ui = ui      

    def run(self):
        # 在这里执行耗时任务，并使用self.param
        result = self.do_work()
        self.finished.emit(result)  # 发送信号，并将结果作为参数传递

    def do_work(self):
        import time
        from osgeo import gdal,ogr,osr
        gdal.UseExceptions()
        time_start=time.time()
        self.progress_signal.emit('开始处理...')
        inputfile = self.ui.comboBox_openImage.currentText()
        ds = gdal.Open(inputfile, gdal.GA_ReadOnly)
        srcband=ds.GetRasterBand(1)
        srcband.SetNoDataValue(0)
        maskband=srcband.GetMaskBand()
        dst_filename=self.ui.lineEdit_saveVector.text()
        drv = ogr.GetDriverByName('ESRI Shapefile')
        dst_ds = drv.CreateDataSource(dst_filename)
        srs = osr.SpatialReference(wkt=ds.GetProjection())
        dst_layername = 'out'
        dst_layer = dst_ds.CreateLayer(dst_layername, srs=srs)
        dst_fieldname = 'DN'
        fd = ogr.FieldDefn(dst_fieldname, ogr.OFTInteger)
        dst_layer.CreateField(fd)
        dst_field = 0
        #prog_func = self.test
        options=[]
        # 参数  输入栅格图像波段\掩码图像波段、矢量化后的矢量图层、需要将DN值写入矢量字段的索引、算法选项、进度条回调函数、进度条参数
        gdal.Polygonize(srcband, maskband, dst_layer,dst_field, options, progress_callback,self)
        ds.Close()
        dst_ds = None
        time_end=time.time()
        self.progress_signal.emit(f'完成处理：花费时间 {((time_end-time_start)/60.0):.2f} 分钟')
        return dst_filename
    
def progress_callback(pct, message, v3):
    """进度条回调函数"""        
    progress = int(pct * 100)
    print(f"\rProgress: {progress}%: {message}", end="")
    v3.progress_signal.emit(f"开始处理: {int(pct * 100)}%")