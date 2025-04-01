from qgis.PyQt.QtCore import QThread, pyqtSignal
 
class EvalSampleThread(QThread):
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
        import numpy as np
        import time
        from osgeo import gdal
        import torch
        import torch.nn as nn
        import argparse
        from glob import glob
        from os.path import basename,dirname,split
        from algorithm.train.tools import one_hot,score_score,score
        import shutil
        import os,sys
        from os import environ
        import geopandas as gpd
        environ['PROJ_LIB'] = dirname(sys.argv[0])+'/proj'
       
        time_start=time.time()
        self.progress_bar.setText('开始处理...')
        # 是否使用cuda
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")    
        # para
        netType = self.ui.comboBox_modelNet.currentText()
        sampleClass = self.ui.comboBox_sampleClass.currentText()
        sampleLists = self.ui.selectSampleList
        modelFile = self.ui.m_modelFile
        if (netType == 'AUNet'):
            from net.AU_Net import AttU_Net
            net = AttU_Net(3, 2)
        if (netType == 'DeepLabV3Plus'):
            from net.DeepLabV3.segmentation_models_pytorch.decoders.deeplabv3.model import DeepLabV3Plus
            net = DeepLabV3Plus(classes=2)
        net = nn.DataParallel(net)
        net.load_state_dict(torch.load(modelFile))
        net = net.cuda()
        net.eval()
        
        colorTable=gdal.ColorTable()
        background = (0,0,0,255)
        label = (255,255,255,255)
        colors = [background ,label ]
        categories = ['background','label']    
        for i in range(len(colors)):
            colorTable.SetColorEntry(i,colors[i])
        count = len(sampleLists)
        for index1,samplePath in enumerate(sampleLists):
            #make dir
            try:
                os.mkdir(samplePath + 'pre/')
            except OSError:
                pass
            #processing
            test_imgs = glob(samplePath + 'image/*.tif')
            img_nums = len(test_imgs)
            
            gdal.AllRegister()
            driver = gdal.GetDriverByName("GTiff")
            driverImg = gdal.GetDriverByName("ENVI")
            acc_average=[]
            recall_average=[]
            iou_average=[]
            i=0
            use_img_nums = 0
            score_file = samplePath + 'loss.csv'
            avg_file = samplePath + 'average_index.csv'
            f = open(score_file,'w',buffering=1)
            f_avg = open(avg_file,'w',buffering=1)
            f.write('ID,'+'Name,'+'loss,'+'acc,'+'recall,'+'iou\n') 
            f_avg.write('acc_average,'+'recall_average,'+'iou_average\n') 
            count2 = len(test_imgs)

            
            range_file = samplePath + 'SamplesRange.shp'
            # 读取矢量文件
            gdf = gpd.read_file(range_file)

            # 检查 'NewField' 是否已经存在
            if 'Loss' not in gdf.columns:
                # 如果不存在，添加新字段并初始化为空字符串
                gdf['Loss'] = ''
            else:
                print("字段 'Loss' 已存在，跳过添加操作。")
            if 'Acc' not in gdf.columns:
                # 如果不存在，添加新字段并初始化为空字符串
                gdf['Acc'] = ''
            else:
                print("字段 'Acc' 已存在，跳过添加操作。")
            if 'Recall' not in gdf.columns:
                # 如果不存在，添加新字段并初始化为空字符串
                gdf['Recall'] = ''
            else:
                print("字段 'Recall' 已存在，跳过添加操作。")
            if 'Iou' not in gdf.columns:
                # 如果不存在，添加新字段并初始化为空字符串
                gdf['Iou'] = ''
            else:
                print("字段 'Iou' 已存在，跳过添加操作。")
            
            # 获取要素个数
            num_features = len(gdf)
            # 遍历 'Name' 字段并将值复制到 'NewField'
            for index2, row in gdf.iterrows():
                self.progress_bar.setText(f"开始处理{index1+1}/{count}: {int((index2+1) * 100 / num_features)}%")
                name = row['Name']                       

                img = f'{samplePath}image/{name}.tif'
                label = f'{samplePath}label/{name}.tif'
                pre = f'{samplePath}pre/{name}.tif'
                
                intervalX = 256
                intervalY = 256
                    
                #inputimage
                y_test = gdal.Open(img)
                projection = y_test.GetProjection()
                geotransform = y_test.GetGeoTransform()
                width = y_test.RasterXSize
                height = y_test.RasterYSize
                
                #outputimage       
                outputimage=driver.Create(pre,width,height,1,gdal.GDT_Byte)
                outputimage.SetProjection(projection)
                outputimage.SetGeoTransform(geotransform)
                #outputimage: index image
                outputimage.GetRasterBand(1).SetRasterColorTable(colorTable)
                outputimage.GetRasterBand(1).SetRasterCategoryNames(categories)
                
                imgdata = y_test.ReadAsArray(0,0,width,height).astype(np.float32)
                pre_img = torch.from_numpy(imgdata/ 255)
                pre_img = pre_img.unsqueeze(0)
                pre_img = pre_img.to(device=device, dtype=torch.float32)
                
                labelImg = gdal.Open(label)
                labeldata = labelImg.ReadAsArray(0,0,width,height)
                labeldata1 = np.expand_dims(labeldata, 0)
                labeldata1 = np.expand_dims(labeldata1, 0)
                onehot_labels = one_hot(labeldata1,2)
                onehot_labels = torch.from_numpy(onehot_labels)
                onehot_labels = onehot_labels.to(device=device, dtype=torch.float32)
                
                with torch.no_grad():               
                    output = net(pre_img)
                    loss = nn.BCEWithLogitsLoss()(output, onehot_labels)
                    pred_max = output.max(1)[1].squeeze().cpu().data.numpy()#(b,w,h) 
                    recall, acc, iou = score(labeldata, pred_max)
                pred_max = pred_max.astype(np.uint8)
                outputimage.GetRasterBand(1).WriteArray(pred_max,0,0)
                outputimage.GetRasterBand(1).FlushCache()
            
                outputimage = None
                y_test = None
                acc_average += [acc]
                recall_average += [recall]
                iou_average += [iou]
                use_img_nums += 1
                
                gdf.at[index2, 'Loss'] = round(loss.item(),3) 
                gdf.at[index2, 'Acc'] = round(acc,3) 
                gdf.at[index2, 'Recall'] = round(recall,3) 
                gdf.at[index2, 'Iou'] = round(iou,3) 

                score_image = str(index2+1)+','+basename(img).split('.')[0]+','+str(round(loss.item(),3))+","+str(round(acc,3))+","+str(round(recall,3))+","+str(round(iou,3))+'\n'      
                f.write(score_image)
                print(index2+1,"/",img_nums,basename(img).split('.')[0],":loss=",round(loss.item(),3),",precision=",round(acc,3),",recall=",round(recall,3),",iou=",round(iou,3))
            f.close()
            print("use_img_nums:",use_img_nums,":acc_average=",round(np.mean(acc_average),3),",recall_average=",round(np.mean(recall_average),3),",iou_average=",round(np.mean(iou_average),3))
            f_avg.write(str(round(np.mean(acc_average),3))+","+str(round(np.mean(recall_average),3))+","+str(round(np.mean(iou_average),3)))
            f_avg.close()
            # 将修改后的 GeoDataFrame 保存回原始文件（覆盖原文件）
            gdf.to_file(range_file)
        time_end=time.time()    
        print('time cost','%.2f'%((time_end-time_start)/60.0),'minutes')     
        self.progress_bar.setText(f"处理完成: 花费时间 {((time_end-time_start)/60.0):.2f} 分钟")           