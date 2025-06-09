from qgis.PyQt.QtCore import QThread, pyqtSignal
 
class PostClumpThread(QThread):

    finished = pyqtSignal(object)  # 用于将数据从子线程发送到主线程的信号
    # 添加信号
    progress_signal = pyqtSignal(str)

    def __init__(self, ui, toolDrawRect):
        super().__init__()
        self.ui = ui
        self.toolDrawRect = toolDrawRect

    def run(self):
        # 在这里执行耗时任务，并使用self.param
        result = self.do_work()
        self.finished.emit(result)  # 发送信号，并将结果作为参数传递

    def do_work(self):

        # 这里是实际工作的函数，接受参数param
        # 模拟耗时任务
        import numpy as np
        import time
        from osgeo import gdal
        from tqdm import tqdm
        import cv2
        from os.path import splitext,basename,isfile
        from os import mkdir
        from glob import glob

        time_start=time.time()
        self.progress_signal.emit('开始处理...') 
        #index color
        colorTable=gdal.ColorTable()
        background = (0,0,0,255)
        label = (0,0,255,255)
        colors = [background ,label ]
        categories = ['background','label']   
        for i in range(len(colors)):
            colorTable.SetColorEntry(i,colors[i])
        #paras
        kernel_size = int(self.ui.lineEdit_kernel.text()) 
        kernel=cv2.getStructuringElement(cv2.MORPH_RECT,(kernel_size,kernel_size))
        test_imgs = []
        test_img_path = self.ui.comboBox_openImage.currentText()
        if(isfile(test_img_path)):
            if(basename(test_img_path)=='file.list'):
                with open(test_img_path,encoding= 'utf-8') as f:
                    for line in f.readlines():              
                        line = line.strip('\n')
                        test_imgs.append(line)
            else:
                test_imgs += [test_img_path]
        else:
            test_imgs += glob(test_img_path+'*.tif')
            test_imgs += glob(test_img_path+'*.img')
        img_nums = len(test_imgs)
        if(img_nums == 0):
            print("No file in this path: "+test_img_path)
        output_img_path = self.ui.lineEdit_saveImage.text()
        intervalX = int(self.ui.lineEdit_labelSize.text())
        intervalY = intervalX
        overlap = 0
        parallelSize = 0
        #write data
        gdal.AllRegister()
        for index,test_img in enumerate(test_imgs):
            print(index+1,'/',img_nums,test_img)
            y_test:gdal.Dataset = gdal.Open(test_img)
            #info
            projection = y_test.GetProjection()
            geotransform = y_test.GetGeoTransform()
            width, height = y_test.RasterXSize, y_test.RasterYSize 
            startX, startY, startX_r, startY_r, width_r, height_r = 0, 0, 0, 0, width, height
            #是否勾画范围
            r = self.toolDrawRect.rectangle()
            if r is not None:
                print("Rectangle（PredictThread）:", r.xMinimum(),
                        r.yMinimum(), r.xMaximum(), r.yMaximum()
                    )
                xmin_r,ymin_r,xmax_r,ymax_r = r.xMinimum(), r.yMinimum(), r.xMaximum(), r.yMaximum()
                startX_r = int((xmin_r-geotransform[0])/geotransform[1])
                startY_r = int((ymax_r-geotransform[3])/geotransform[5])
                endX_r = int((xmax_r-geotransform[0])/geotransform[1])
                endY_r = int((ymin_r-geotransform[3])/geotransform[5])
                width_r = endX_r - startX_r + 1
                height_r = endY_r - startY_r + 1
                startX, startY = startX_r, startY_r
                geotransform = [xmin_r, geotransform[1], geotransform[2], ymax_r, geotransform[4], geotransform[5]]
            print(f"width={width},height={height},width_r={width_r},height_r={height_r},startX_r={startX_r},startY_r={startY_r}")    
            #outputimage 
            if(".img" in output_img_path or ".tif" in output_img_path ):
                output_img = output_img_path
            else:
                output_img = output_img_path + splitext(basename(test_img))[0] +".img"
                try:
                    mkdir(output_img_path)               
                except OSError:
                    pass
            #driver = gdal.GetDriverByName("GTiff")
            driverImg = gdal.GetDriverByName("ENVI")
            outputimage=driverImg.Create(output_img,width_r,height_r,1,gdal.GDT_Byte)
            outputimage.SetProjection(projection)
            outputimage.SetGeoTransform(geotransform)
            #outputimage: index image
            outputimage.GetRasterBand(1).SetRasterColorTable(colorTable)
            outputimage.GetRasterBand(1).SetRasterCategoryNames(categories)
            padding = overlap
            intervalWidthNums = int(width_r/(intervalX-2*padding))+1
            intervalHeightNums = int(height_r/(intervalY-2*padding))+1
            print(f'intervalWidthNums={intervalWidthNums},intervalHeightNums={intervalHeightNums}')
            #processing
            for y in tqdm(range(int(intervalHeightNums)),position=0,ncols=100):           
                #clip big image 
                startY -= 2*padding
                endY = startY + intervalY - 1
                for x in range(int(intervalWidthNums)):
                    print(f'x={x},y={y}')
                    #clip big image        
                    startX -= 2*padding
                    endX = startX + intervalX -1
                    #edge process
                    if startX < startX_r:
                        startX = startX_r
                        endX = startX_r + intervalX - padding -1
                    if endX >= startX_r + width_r:           
                        endX = startX_r + width_r-1
                    if startY < startY_r:
                        startY = startY_r
                        endY = startY_r + intervalY - padding -1
                    if endY >=startY_r + height_r:
                        endY = startY_r + height_r-1       
                    print(f'startX={startX},startY={startY},intervalX={endX-startX+1},intervalY={endY-startY+1}')
                    imgdata = y_test.ReadAsArray(startX,startY,endX-startX+1,endY-startY+1).astype(np.float32)                
                    
                    if np.any(imgdata>0):                                                              
                        #print('imgdata',imgdata.shape,imgdata)#CHW
                        closing=cv2.morphologyEx(imgdata,cv2.MORPH_CLOSE,kernel)
                        opening=cv2.morphologyEx(closing,cv2.MORPH_OPEN,kernel)                       
                        #eroded_image=cv2.erode(imgdata,kernel,iterations=1)#腐蚀
                        #dilated_image=cv2.dilate(opening,kernel_s,iterations=1)#膨胀
                        #cv2.imshow('eroded_image',eroded_image)
                        #print("eroded_image.shape:",eroded_image.shape,eroded_image)
                        endX_n, startX_n, endY_n, startY_n = endX-startX_r, startX-startX_r, endY-startY_r, startY-startY_r
                        outputimage.GetRasterBand(1).WriteArray(opening,startX_n,startY_n)
                        outputimage.GetRasterBand(1).FlushCache() 
                    #clip big image 
                    startX = endX + 1
                #clip big image 
                startX = startX_r
                startY = endY + 1
                # 更新状态栏
                self.progress_signal.emit(f"开始处理: {int((y+1) * 100 / intervalHeightNums)}%")        
            outputimage = None
            y_test = None
        
        time_end=time.time()
        self.progress_signal.emit(f'完成处理：花费时间 {((time_end-time_start)/60.0):.2f} 分钟')
        return output_img_path


        
    