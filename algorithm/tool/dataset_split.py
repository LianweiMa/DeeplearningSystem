from os.path import splitext,basename
from glob import glob
from torch.utils.data import Dataset

class BasicDataset(Dataset):
    def __init__(self, imgs_dir, masks_dir):
        self.imgs_dir = imgs_dir
        self.masks_dir = masks_dir
        self.ids = glob(imgs_dir+'*.tif')
    def __len__(self):
        return len(self.ids)
    def __getitem__(self, i):
        id = splitext(basename(self.ids[i]))[0]       
        img_file = self.ids[i]
        mask_file = self.masks_dir + id + '.tif'
        return img_file,mask_file
