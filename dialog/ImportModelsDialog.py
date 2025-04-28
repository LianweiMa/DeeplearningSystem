# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QDialog, QFileDialog
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt
from os.path import basename
import uuid
from ui.ImportModelsUI import Ui_Dialog


class ImportModelsDialog(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)  # 调用setupUi方法初始化界面
        self.parent = parent
        
        # 在这里添加你的逻辑代码
        from os.path import join
        from DeeplearningSystem import base_dir
        icon_Segment = join(base_dir, 'settings/icon', 'net_import.png') 
        icon = QIcon()
        icon.addPixmap(QPixmap(icon_Segment), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)
        self.setWindowFlags(self.windowFlags() & ~(Qt.WindowContextHelpButtonHint))
        self.comboBox_GSD.addItems([ "meter", "submeter", "meter_submeter" ])
        self.comboBox_GSD.setCurrentIndex(-1)

        self.pushButton_Browser.clicked.connect(self.open_clicked)
        self.lineEdit_ModelsPath.textChanged.connect(self.text_changed)

    def open_clicked(self,Dialog):
        path,_ = QFileDialog.getOpenFileName(self.parent, '打开', '', 'Model Files (*.pth);;All Files (*.*)')
        if  path=="":
            return
        self.lineEdit_ModelsPath.setText(path)

    def text_changed(self,text):        
        # desert_AUNet_256_epoch=74_train-loss=0.1796_train-acc=0.8176_val-loss=0.1323_val-acc=0.8651_val-recall=0.9555_val-iou=0.8311     
        modelName = basename(self.lineEdit_ModelsPath.text()).rsplit('.',1)[0]
        s = modelName.split('_')
        Class = s[0]
        Net = s[1]  
        epoch = s[3].split('=')[1]
        trainloss = s[4].split('=')[1]
        trainacc = s[5].split('=')[1]
        valloss = s[6].split('=')[1]
        valacc = s[7].split('=')[1]
        valrecall = s[8].split('=')[1]
        valiou = s[9].split('=')[1]
        self.lineEdit_Class.setText(Class)
        self.lineEdit_net.setText(Net)
        self.lineEdit_Epoch.setText(epoch)
        self.lineEdit_trainLoss.setText(trainloss)
        self.lineEdit_trainAcc.setText(trainacc)
        self.lineEdit_valLoss.setText(valloss)
        self.lineEdit_valAcc.setText(valacc)
        self.lineEdit_valRecall.setText(valrecall)
        self.lineEdit_valIOU.setText(valiou)
        # 生成完整UUID并截取前N位
        full_uuid = uuid.uuid4().hex  # 32字符的十六进制字符串
        short_id = full_uuid[:8]      # 取前8位
        self.lineEdit_Name.setText(f'{Class}_{short_id}')
