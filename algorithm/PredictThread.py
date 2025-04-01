from qgis.PyQt.QtCore import QThread, pyqtSignal
 
class PredictThread(QThread):
    finished = pyqtSignal(object)  # 用于将数据从子线程发送到主线程的信号

    def __init__(self, ui, progress_bar, toolDrawRect):
        super().__init__()
        self.ui = ui
        self.progress_bar = progress_bar
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
        import torch
        import torch.nn as nn
        from glob import glob
        from os.path import splitext,basename,isfile
        from os import mkdir
        from os import environ
        environ['PROJ_LIB'] = '.settings/proj/'
        time_start=time.time()
        self.progress_bar.setText('开始处理...')
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        if (self.ui.comboBox_modelNet.currentText() == 'AUNet'):
            from net.AU_Net import AttU_Net
            if(self.ui.comboBox_modelType.currentText() == 'bareland'):
                net = AttU_Net(4, 2)
            else:
                net = AttU_Net(3, 2)
        if (self.ui.comboBox_modelNet.currentText() == 'DeepLabV3Plus'):
            from net.DeepLabV3.segmentation_models_pytorch.decoders.deeplabv3.model import DeepLabV3Plus
            net = DeepLabV3Plus(classes=2)
        net.to(device)
        net = nn.DataParallel(net)
        net.load_state_dict(torch.load(self.ui.m_modelFile))   
        net.eval()
        #index color
        colorTable=gdal.ColorTable()
        background = (0,0,0,255)
        label = (255,0,0,255)
        colors = [background ,label ]
        categories = ['background','label']   
        for i in range(len(colors)):
            colorTable.SetColorEntry(i,colors[i])
        #paras
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
        overlap = int(self.ui.lineEdit_overlap.text())
        parallelSize = int(self.ui.lineEdit_parallelSize.text())
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
                #print(f"width={width},height={height},width_r={width_r},height_r={height_r},startX_r={startX_r},startY_r={startY_r}")
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
            #print(f'intervalWidthNums={intervalWidthNums},intervalHeightNums={intervalHeightNums}')
            #processing                 
            new_imgdatas = None
            position_list = []        
            for y in tqdm(range(int(intervalHeightNums)),position=0,ncols=100):           
                #clip big image 
                startY -= 2*padding
                endY = startY + intervalY - 1
                for x in range(int(intervalWidthNums)):
                    #print(f'x={x},y={y}')
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
                    #print(f'startX={startX},startY={startY},intervalX={endX-startX+1},intervalY={endY-startY+1}')
                    imgdata = y_test.ReadAsArray(startX,startY,endX-startX+1,endY-startY+1).astype(np.float32)                
                    
                    if np.any(imgdata>0):
                        xmin = geotransform[0]+startX*geotransform[1]+startY*geotransform[2]
                        ymax = geotransform[3]+startX*geotransform[4]+startY*geotransform[5]
                        if endX-startX+1 < intervalX:
                            if startX == startX_r:
                                imgdata = np.pad(imgdata,((0,0),(0,0),(padding,0)),'edge')
                                xmin -= padding*geotransform[1]
                            if endX == startX_r + width_r-1:
                                imgdata = np.pad(imgdata,((0,0),(0,0),(0,intervalX-(endX-startX+1))),'edge')
                        if endY-startY+1 < intervalY:
                            if startY == startY_r:
                                imgdata = np.pad(imgdata,((0,0),(padding,0),(0,0)),'edge')
                                ymax -= padding*geotransform[5]
                            if endY == startY_r + height_r-1:
                                imgdata = np.pad(imgdata,((0,0),(0,intervalY-(endY-startY+1)),(0,0)),'edge')
                        if(self.ui.comboBox_modelType.currentText() == 'bareland'):
                            imgdata = imgdata/10000   
                        else:
                             imgdata = imgdata/255                 
                        imgdata = np.expand_dims(imgdata, 0)
                        if new_imgdatas is None:
                            new_imgdatas = imgdata
                        else:
                            new_imgdatas = np.concatenate((new_imgdatas, imgdata), axis=0)
                        position_list.append([endX-startX_r, startX-startX_r, endY-startY_r, startY-startY_r])
                        if new_imgdatas.shape[0] >= parallelSize:
                            pre_img = torch.from_numpy(new_imgdatas)# numpy中的ndarray转化成pytorch中的tensor
                            pre_img = pre_img.to(device=device, dtype=torch.float32)
                            # 将图片数据传给GPU计算
                            with torch.no_grad():
                                output = net(pre_img)
                                #print("output:",output.shape,output)
                                preds = output.max(1)[1].cpu().data.numpy()
                                #print("preds:",preds.shape,preds)
                            preds = preds.astype(np.uint8)
                            for i in range(preds.shape[0]):
                                pred = np.squeeze(preds[i])
                                endX_n, startX_n, endY_n, startY_n = position_list[i]
                                outputimage = self.write_array(endX_n, startX_n, endY_n, startY_n, intervalX, intervalY, width_r, height_r, pred,
                                                        padding, outputimage)
                            new_imgdatas=None
                            position_list=[]
                            outputimage.GetRasterBand(1).FlushCache()
                    #clip big image 
                    startX = endX + 1
                #clip big image 
                startX = startX_r
                startY = endY + 1
                # 更新状态栏
                #将进度信息设置到状态栏
                #wx.CallAfter(self.UpdateStatusBar, y, intervalHeightNums)
                self.progress_bar.setText(f"开始处理: {int((y+1) * 100 / intervalHeightNums)}%")
            if new_imgdatas is not None:
                pre_img = torch.from_numpy(new_imgdatas)# numpy中的ndarray转化成pytorch中的tensor
                pre_img = pre_img.to(device=device, dtype=torch.float32)
                # 将图片数据传给GPU计算
                with torch.no_grad():
                    output = net(pre_img)
                    preds = output.max(1)[1].cpu().data.numpy()
                preds = preds.astype(np.uint8)
                for i in range(preds.shape[0]):
                    pred = np.squeeze(preds[i])
                    endX_n, startX_n, endY_n, startY_n = position_list[i]
                    outputimage = self.write_array(endX_n, startX_n, endY_n, startY_n, intervalX, intervalY, width_r, height_r, pred,
                                            padding, outputimage)
                new_imgdatas=None
                position_list=[]
            outputimage = None
            y_test = None
        
        time_end=time.time()
        self.progress_bar.setText(f'完成处理：花费时间 {((time_end-time_start)/60.0):.2f} 分钟')
        return output_img
    
    def write_array(self,endX, startX, endY, startY, intervalX, intervalY, width, height, pred, padding, outputimage):
        #print(f'(write_arrary):startX={startX},startY={startY},endX={endX},endY={endY}')
        if endX-startX+1 == intervalX and endY-startY+1 == intervalY:
            data = pred[padding:pred.shape[0]-padding,padding:pred.shape[1]-padding] 
            #print(f'(write_arrary):startX={startX},startY={startY},endX={endX},endY={endY}') 
            #print(f'data.shape:{data.shape}')
            #print(f'(write_arrary):startX={startX+ padding},startY={startY+ padding}')        
            outputimage.GetRasterBand(1).WriteArray(data,startX + padding,startY + padding)
        #overwrite edge data(only inlude left and top edge of image)            
        if endX-startX+1 < intervalX:#左右
            if startX == 0:#左                    
                if startY == 0:#左上
                    data = pred[padding:pred.shape[0]-padding,padding:pred.shape[1]-padding]
                    outputimage.GetRasterBand(1).WriteArray(data,startX,startY)
                elif endY+1!=height:#左中
                    data = pred[padding:pred.shape[0]-padding,padding:pred.shape[1]-padding]
                    outputimage.GetRasterBand(1).WriteArray(data,startX,startY+padding)
                else:#左下
                    data = pred[padding:pred.shape[0]-(intervalY-(endY-startY+1)),padding:pred.shape[1]-padding]
                    outputimage.GetRasterBand(1).WriteArray(data,startX,startY+padding)
            if endX+1 == width:#右                   
                if startY == 0:#右上
                    data = pred[padding:pred.shape[0]-padding,padding:pred.shape[1]-(intervalX-(endX-startX+1))]
                    outputimage.GetRasterBand(1).WriteArray(data,startX+padding,startY)
                elif endY +1 != height:#右中
                    data = pred[padding:pred.shape[0]-padding,padding:pred.shape[1]-(intervalX-(endX-startX+1))]
                    outputimage.GetRasterBand(1).WriteArray(data,startX+padding,startY+padding)
                else:#右下
                    data = pred[padding:pred.shape[0]-(intervalY-(endY-startY+1)),padding:pred.shape[1]-(intervalX-(endX-startX+1))]
                    outputimage.GetRasterBand(1).WriteArray(data,startX+padding,startY+padding)
        if endY-startY+1 < intervalY:#上下
            if startY == 0:#上                  
                if startX == 0:#上左
                    data = pred[padding:pred.shape[0]-padding,padding:pred.shape[1]-padding]
                    outputimage.GetRasterBand(1).WriteArray(data,startX,startY)
                elif endX+1!=width:#上中                     
                    data = pred[padding:pred.shape[0]-padding,padding:pred.shape[1]-padding]
                    outputimage.GetRasterBand(1).WriteArray(data,startX + padding,startY)
                else:#上右                       
                    data = pred[padding:pred.shape[0]-padding,padding:pred.shape[1]-(intervalX-(endX-startX+1))]
                    outputimage.GetRasterBand(1).WriteArray(data,startX + padding,startY)
            if endY+1 == height:#下                   
                if startX == 0:#下左
                    data = pred[padding:pred.shape[0]-(intervalY-(endY-startY+1)),padding:pred.shape[1]-padding]
                    outputimage.GetRasterBand(1).WriteArray(data,startX,startY+ padding)
                elif endX+1!=width:#下中
                    data = pred[padding:pred.shape[0]-(intervalY-(endY-startY+1)),padding:pred.shape[1]-padding]
                    outputimage.GetRasterBand(1).WriteArray(data,startX + padding,startY+ padding)
                else:#下右
                    data = pred[padding:pred.shape[0]-(intervalY-(endY-startY+1)),padding:pred.shape[1]-(intervalX-(endX-startX+1))]
                    outputimage.GetRasterBand(1).WriteArray(data,startX + padding,startY+ padding)
        return outputimage