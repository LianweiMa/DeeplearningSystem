import numpy as np
import torch
from osgeo import gdal
from os.path import basename,dirname,abspath,splitext
from tqdm import tqdm

eps = 1e-15

'''compute recall, precision, iou'''
def score(gt,pre):
    
    pre_acc = ((pre==1) & (gt==1)).sum()

    gt_total = gt.sum()
    pre_total = pre.sum()

    recall = (pre_acc.astype(np.float32) ) / (gt_total.astype(np.float32) + eps)
    precision = (pre_acc.astype(np.float32) ) / (pre_total.astype(np.float32) + eps)
    iou = (pre_acc.astype(np.float32) ) / ((gt_total+pre_total-pre_acc).astype(np.float32) + eps)
    
    return recall,precision,iou

def compute_iou(gt,pre):
    
    pre_acc = ((pre==1) & (gt==1)).sum()

    gt_total = gt.sum()
    pre_total = pre.sum()

    iou = (pre_acc.astype(np.float32) ) / ((gt_total+pre_total-pre_acc).astype(np.float32) + eps)
    
    return iou

def score_score(gt,pre):
    
    pre_acc = (pre==gt).sum()

    gt_total = gt.shape[0]*gt.shape[1]
    #print(gt.shape)
    

    #recall = (pre_acc.astype(np.float32) ) / (gt_total.astype(np.float32) + eps)
    acc = (pre_acc ) / (gt_total + eps)
    #iou = (pre_acc.astype(np.float32) ) / ((gt_total+pre_total-pre_acc).astype(np.float32) + eps)
    
    return acc

def score_cuda(gt,pre):
    
    pre_acc = torch.dot(gt.view(-1),pre.view(-1))

    gt_total = torch.sum(gt)
    pre_total = torch.sum(pre)

    recall = (pre_acc.float()) / (gt_total.float() + eps)
    precision = (pre_acc.float()) / (pre_total.float() + eps)
    iou = (pre_acc.float()) / ((gt_total+pre_total-pre_acc).float() + eps)
    
    return recall,precision,iou

'''one hot vector'''
def one_hot(labels,num_class):
    
    batch_size = labels.shape[0]
    sample_size_x = labels.shape[2]
    sample_size_y = labels.shape[3]
    
    onehot_labels = np.zeros((batch_size, num_class, sample_size_x, sample_size_y))               
    for i in range(labels.shape[0]):
        for j in range(num_class):
            onehot_labels[i][j][:][:] = (labels[i,0,:,:] == j)                  

    return onehot_labels

def check_data(input_fold):

    train_file = input_fold + 'train_set.txt'
    f = open(train_file,"r",encoding="utf-8") 
    count = f.readline()
    files = f.readlines()#读取全部内容
    f.close()
    val_file = input_fold + 'val_set.txt'
    f = open(val_file,"r",encoding="utf-8") 
    count = f.readline()
    files += f.readlines()#读取全部内容
    f.close()

    #print(f'files={count}')
    #print(files)
    gdal.AllRegister()
    for file in tqdm(files):
        file = file.rstrip()
        y_test:gdal.Dataset = gdal.Open(file)
        width = y_test.RasterXSize
        height = y_test.RasterYSize
        bands = y_test.RasterCount
        if(width!=256 or height!=256 or bands!=4):
            print(f'{basename(file)},{width},{height},{bands}')
        del y_test
        id = splitext(basename(file))[0]
        mask_file =dirname(dirname(abspath(file))) + '/label/' + id + '.tif'
        y_test:gdal.Dataset = gdal.Open(mask_file)
        width = y_test.RasterXSize
        height = y_test.RasterYSize
        bands = y_test.RasterCount
        if(width!=256 or height!=256 or bands!=1):
            print(f'{basename(mask_file)},{width},{height},{bands}')
        del y_test