from os.path import dirname,basename
import os
import numpy as np
from glob import glob
from torch.utils.data import Dataset
import logging
from PIL import Image
from torchvision.transforms import functional as F
from torchvision import transforms as tfs

# 随机裁剪
def rand_crop(image, label, height=128, width=128 , u=0.5):
    transformers=tfs.Compose([tfs.Resize((256,256),interpolation=2)])
    if np.random.random() < u:
        crop_params = tfs.RandomCrop.get_params(image, (height, width))
        image = transformers(F.crop(image, *crop_params))
        label = transformers(F.crop(label, *crop_params))
    return image, label

# ColorJitter变换
def color_jitter(image, label, u=0.5):
    transform = tfs.ColorJitter(brightness = 0.2, contrast = 0.2, saturation = 0.2, hue = 0.1)
    if np.random.random() < u:
        image = transform(image)
    return image, label

# 灰度化变换
def gray_scale(image, label, u=0.5):
    transform = tfs.Grayscale(num_output_channels = 1)
    if np.random.random() < u:
        image = transform(image)
    return image, label

# 高斯模糊变换
def blur(image, label, u=0.5):
    transform = tfs.GaussianBlur(kernel_size = 3)
    if np.random.random() < u:
        image = transform(image)
    return image, label

class BasicDataset(Dataset):
    def __init__(self, input):
        f = open(input,"r",encoding="utf-8")
        count = f.readline() 
        self.ids = f.readlines()#读取全部内容
        logging.info(f'Creating dataset with {len(self.ids)} examples')
        f.close()

    def __len__(self):
        return len(self.ids)
    
    def __getitem__(self, i):
        img_file = self.ids[i].rstrip()
        id = basename(img_file)      
        mask_file = dirname(dirname(img_file)) + '/label/' + id  
        img = Image.open(img_file)
        mask = Image.open(mask_file)  
        img, mask = rand_crop(img, mask)
        img, mask = color_jitter(img, mask)
        #img, mask = gray_scale(img, mask)
        img, mask = blur(img, mask)
        img = np.array(img).transpose((2, 0, 1)) / 255
        mask = np.expand_dims(mask, axis=0)
        return img, mask

class ValDataset(Dataset):
    def __init__(self, input):
        f = open(input,"r",encoding="utf-8") 
        count = f.readline()
        self.ids = f.readlines()#读取全部内容
        logging.info(f'Creating dataset with {len(self.ids)} examples')
        f.close()

    def __len__(self):
        return len(self.ids)
    
    def __getitem__(self, i):
        img_file = self.ids[i].rstrip()
        id = basename(img_file)      
        mask_file = dirname(dirname(img_file)) + '/label/' + id  
        img = Image.open(img_file)
        mask = Image.open(mask_file)  
        img = np.array(img).transpose((2, 0, 1)) / 255
        mask = np.expand_dims(mask, axis=0)
        return img, mask