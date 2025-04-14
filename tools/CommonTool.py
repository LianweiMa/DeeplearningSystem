# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QMessageBox, QLabel, QHBoxLayout
from PyQt5.QtCore import Qt


def show_info_message(self, title, info):
        msg = QMessageBox(self)
        layout = msg.layout()
        #print(f"行数: {layout.rowCount()}, 列数: {layout.columnCount()}")  # 通常为 3 行 2 列
        #msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle(title)

        # 移除默认的文本和 icon
        msg.setText("")
        msg.setIcon(QMessageBox.NoIcon)  # 禁用默认 icon

        # 创建自定义的 QLabel 用于文本（居中）
        label = QLabel(info)
        #label.setAlignment(Qt.AlignLeft)

        # 创建自定义的 QLabel 用于 icon（居中）
        icon_label = QLabel()       
        icon = QMessageBox().standardIcon(QMessageBox.Information)  # ✅ 正确
        icon_label.setPixmap(icon)  # ✅ 正确
        #icon_label.setAlignment(Qt.AlignCenter)
        # 创建一个垂直布局，并添加 icon 和文本
        layout = QHBoxLayout()
        layout.addWidget(icon_label)
        layout.addStretch(1) 
        layout.addWidget(label)
        #layout.setAlignment(icon_label, Qt.AlignLeft)  # 整体居中

        # 替换 QMessageBox 的布局
        msg.layout().addLayout(layout, 0, 0)  # 添加到 QMessageBox 的布局

        #msg.setText(info)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.button(QMessageBox.Ok).setText("确定")  # 关键修改点
            
        msg.exec_()

def show_question_message(self, title, info):
        msg = QMessageBox(self)
        layout = msg.layout()
        #print(f"行数: {layout.rowCount()}, 列数: {layout.columnCount()}")  # 通常为 3 行 2 列
        #msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle(title)

        # 移除默认的文本和 icon
        msg.setText("")
        msg.setIcon(QMessageBox.NoIcon)  # 禁用默认 icon

        # 创建自定义的 QLabel 用于文本（居中）
        label = QLabel(info)
        #label.setAlignment(Qt.AlignLeft)

        # 创建自定义的 QLabel 用于 icon（居中）
        icon_label = QLabel()       
        icon = QMessageBox().standardIcon(QMessageBox.Question)  # ✅ 正确
        icon_label.setPixmap(icon)  # ✅ 正确
        #icon_label.setAlignment(Qt.AlignCenter)
        # 创建一个垂直布局，并添加 icon 和文本
        layout = QHBoxLayout()
        layout.addWidget(icon_label)
        layout.addStretch(1) 
        layout.addWidget(label)
        #layout.setAlignment(icon_label, Qt.AlignLeft)  # 整体居中

        # 替换 QMessageBox 的布局
        msg.layout().addLayout(layout, 0, 0)  # 添加到 QMessageBox 的布局

        #msg.setText(info)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.button(QMessageBox.Yes).setText("确定")  # 关键修改点
        msg.button(QMessageBox.No).setText("取消")  # 关键修改点
                
        return msg.exec_()