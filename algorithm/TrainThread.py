from qgis.PyQt.QtCore import QThread, pyqtSignal

class TrainThread(QThread):
    finished = pyqtSignal(object)  # 用于将数据从子线程发送到主线程的信号
    msg = pyqtSignal(object)

    def __init__(self, ui, progress_bar):
        super().__init__()
        self.ui = ui
        self.progress_bar = progress_bar
        self.running = True

    def run(self):
        # 在这里执行耗时任务，并使用self.param
        result = self.do_work()
        self.finished.emit(result)  # 发送信号，并将结果作为参数传递

    def stop(self):
        self.running = False

    def do_work(self):
        # 这里是实际工作的函数，接受参数param
        import logging
        import os
        import sys
        import time
        import datetime
        import numpy as np
        from tqdm import tqdm
        import torch
        import torch.nn as nn
        from torch import optim
        from torch.utils.data import DataLoader
        from algorithm.train.dataset import BasicDataset,ValDataset
        from torch.utils.tensorboard import SummaryWriter
        from algorithm.train.tools import one_hot, score

        time_start = time.time()
        self.progress_bar.setText('训练初始化...')
        logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
        info = f'Star time: {datetime.datetime.now()}'
        logging.info(info)
        self.msg.emit(info)
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        # para
        netType = self.ui.comboBox_modelNet.currentText()
        learn_rate = float(self.ui.lineEdit_learningRate.text())
        save_fold = self.ui.lineEdit_saveModelPath.text()+'/'
        batch_size = int(self.ui.lineEdit_batch.text())
        labelType = self.ui.comboBox_sampleClass.currentText()
        epochs = int(self.ui.lineEdit_epoch.text())

        if (netType == 'AUNet'):
            from net.AU_Net import AttU_Net
            net = AttU_Net(3, 2)
        if (netType == 'DeepLabV3Plus'):
            from net.DeepLabV3.segmentation_models_pytorch.decoders.deeplabv3.model import DeepLabV3Plus
            net = DeepLabV3Plus(classes=2)
        net = nn.DataParallel(net)
        net.to(device=device)
        try:
            
            optimizer = optim.Adam(net.parameters(), lr=learn_rate, weight_decay=0)
            criterion = nn.BCEWithLogitsLoss()         
            writer = SummaryWriter(log_dir=save_fold)
            # train data   
            from DeeplearningSystem import train_set,val_set  
            dataset = BasicDataset(train_set)
            n_train = len(dataset)
            train_loader = DataLoader(dataset, batch_size=batch_size, shuffle=True, pin_memory=True, drop_last=True)
            # val data    
            val_dataset = ValDataset(val_set)
            n_val = len(val_dataset)
            val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, pin_memory=True, drop_last=True)
            # info 
            info = f'''Start training:
            Network:       {netType}
            Device:        {device.type}
            Epochs:        {epochs}
            Learn Rate:     {learn_rate}
            Batch Size:     {batch_size}
            Training Size:  {n_train}
            Validation Size: {n_val}
            Label Type:    {labelType}
            '''
            logging.info(info)
            self.msg.emit(info)
            log_file = save_fold + f'{labelType}_{netType}_epoch={epochs}_bz={batch_size}_lr={learn_rate}.csv'
            f = open(log_file, 'w', buffering=1)
            f.write('epoch,' + 'accuracy,' + 'loss,' + 'val_accuracy,' + 'val_loss,' + 'val_recall,' + 'val_iou\n')
            # iter
            best_iou = 0.0
            global_step = 0
            epoch = 0
            for epoch in range(epochs):
                if self.running==False:
                    break
                self.progress_bar.setText(f"开始训练: {int((epoch + 1) * 100 / epochs)}%")
                net.train()
                train_loss = []
                train_acc = []
                with tqdm(total=n_train, desc=f'Epoch {epoch + 1}/{epochs}', unit='img') as pbar:
                    for batch_index, batch in enumerate(train_loader):
                        global_step += 1
                        imgs, labels = batch
                        lr = optimizer.param_groups[0]['lr']
                        optimizer.zero_grad()

                        imgs = imgs.to(device=device, dtype=torch.float32)
                        onehot_labels = one_hot(labels, 2)
                        onehot_labels = torch.from_numpy(onehot_labels)
                        onehot_labels = onehot_labels.to(device=device, dtype=torch.float32)
                        pred = net(imgs)  # (b,2,w,h)
                        loss = criterion(pred, onehot_labels)
                        loss.backward()
                        optimizer.step()
                        pre = pred.max(1)[1].squeeze().cpu().data.numpy()  # (b,w,h)
                        gt = labels.squeeze().cpu().data.numpy()
                        recall, precision, iou = score(gt, pre)
                        train_loss += [loss.item()]
                        train_acc += [precision]
                        pbar.set_postfix({'loss': np.mean(train_loss), 'acc': np.mean(train_acc), 'lr': lr})
                        pbar.update(imgs.shape[0])

                writer.add_scalar('learning_rate', lr, epoch + 1)
                writer.add_scalar('Train/loss', np.mean(train_loss), epoch + 1)
                writer.add_scalar('Train/acc', np.mean(train_acc), epoch + 1)
                # valid
                net.eval()
                val_loss = []
                val_acc = []
                val_recall = []
                val_iou = []
                with tqdm(total=n_val, desc='Validation round', unit='img') as pbar:
                    for batch_index, batch in enumerate(val_loader):
                        imgs, labels = batch
                        imgs = imgs.to(device=device, dtype=torch.float32)
                        onehot_labels = one_hot(labels, 2)
                        onehot_labels = torch.from_numpy(onehot_labels)
                        onehot_labels = onehot_labels.to(device=device, dtype=torch.float32)
                        with torch.no_grad():
                            pred = net(imgs)
                            loss = criterion(pred, onehot_labels)
                            pre = pred.max(1)[1].squeeze().cpu().data.numpy()
                        gt = labels.squeeze().cpu().data.numpy()
                        recall, precision, iou = score(gt, pre)
                        val_loss += [loss.item()]
                        val_acc += [precision]
                        val_recall += [recall]
                        val_iou += [iou]
                        pbar.set_postfix(
                            {'val_loss': np.mean(val_loss), 'val_acc': np.mean(val_acc), 'val_iou': np.mean(val_iou)})
                        pbar.update(imgs.shape[0])
                writer.add_scalar('Val/loss', np.mean(val_loss), epoch + 1)
                writer.add_scalar('Val/acc', np.mean(val_acc), epoch + 1)

                # save model
                log_info = str(epoch + 1) + ',' + str(round(np.mean(train_acc), 4)) + "," + str(
                    round(np.mean(train_loss), 4)) + "," + str(round(np.mean(val_acc), 4)) + "," + str(
                    round(np.mean(val_loss), 4)) + "," + str(round(np.mean(val_recall), 4)) + "," + str(
                    round(np.mean(val_iou), 4)) + '\n'
                f.write(log_info)
                self.msg.emit(f'epoch={epoch + 1},train-loss={(np.mean(train_loss)):.4f},train-acc={(np.mean(train_acc)):.4f},val-loss={(np.mean(val_loss)):.4f},val-acc={(np.mean(val_acc)):.4f},val-recall={(np.mean(val_recall)):.4f},val-iou={(np.mean(val_iou)):.4f}')
                torch.save(net.state_dict(),
                    save_fold + f'{labelType}_{netType}_epoch={epoch + 1}_train-loss={(np.mean(train_loss)):.4f}_train-acc={(np.mean(train_acc)):.4f}_val-loss={(np.mean(val_loss)):.4f}_val-acc={(np.mean(val_acc)):.4f}_val-recall={(np.mean(val_recall)):.4f}_val-iou={(np.mean(val_iou)):.4f}.pth')
            f.close()
            writer.close()

            time_end = time.time()
            info = f'完成训练：花费时间 {((time_end-time_start)/60.0):.2f} 分钟'
            logging.info(info)
            self.msg.emit(info)
            self.progress_bar.setText(info)
            info = f'End time: {datetime.datetime.now()}'
            logging.info(info)
            self.msg.emit(info)
        except KeyboardInterrupt:
            torch.save(net.state_dict(), 'INTERRUPTED.pth')
            logging.info('Saved interrupt')
            time_end = time.time()
            logging.info(f'End time: {datetime.datetime.now()}')
            logging.info(f'time cost {"{:.2f}".format((time_end - time_start) / 60.0)}'+f' 分钟')
            try:
                sys.exit(0)
            except SystemExit:
                os._exit(0)
        