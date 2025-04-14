# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt
from ui.LogUI import Ui_Dialog


class LogDialog(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)  # 调用setupUi方法初始化界面
        
        # 在这里添加你的逻辑代码
        from os.path import join
        from DeeplearningSystem import base_dir
        icon_Segment = join(base_dir, 'settings/icon', 'Train_Watch.png') 
        icon = QIcon()
        icon.addPixmap(QPixmap(icon_Segment), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)
        self.setWindowFlags(self.windowFlags() & ~(Qt.WindowContextHelpButtonHint))
