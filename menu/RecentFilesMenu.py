from qgis.PyQt.QtWidgets import QMenu, QAction, QMessageBox
from tools.CommonTool import show_info_message,show_question_message
from qgis.PyQt.QtCore import QSettings, QObject, pyqtSignal
import os

class RecentFilesMenu:
    def __init__(self, main_window):
        self.main_window = main_window
        self.manager = RecentFilesManager(max_files=10)
              
        # 获取菜单栏
        menubar = self.main_window.menuBar()
        # 查找File菜单（可能有不同名称）
        file_menu = None
        for action in menubar.actions():
            if action.text().lower().replace("&", "") == "文件":  # 处理"&File"情况
                file_menu = action.menu()
                break

        if file_menu:
             # 创建菜单
            self.recent_menu = QMenu("最近打开", self.main_window)           
            #print("找到文件菜单")
            file_menu.insertMenu(
                file_menu.actions()[2], 
                self.recent_menu
            )
        
        # 添加清除动作
        clear_action = QAction("清除列表", self.main_window)
        clear_action.triggered.connect(self.manager.clear_recent_files)
        self.recent_menu.addAction(clear_action)
        self.recent_menu.addSeparator()
        
        # 初始更新
        self.update_menu()
        self.manager.files_changed.connect(self.update_menu)
    
    def update_menu(self):
        """更新最近文件菜单"""
        # 清除现有动作
        for action in self.recent_menu.actions()[2:]:  # 保留前两个动作(标题和分隔线)
            self.recent_menu.removeAction(action)
        
        # 添加新动作
        for i, file_path in enumerate(self.manager.recent_files, 1):
            action = QAction(f"{i}. {file_path}", self.main_window)
            action.triggered.connect(lambda _, path=file_path: self.open_project(path))
            self.recent_menu.addAction(action)
    
    def open_project(self, path):
        """打开QGIS工程文件"""
        if not path:
            return
        # 检查工程是否要保存
        if self.main_window.project.isDirty():
            print("工程有未保存的修改")
            savePrj = show_question_message(self.main_window, '打开工程', "是否保存对当前工程的更改？")
            if savePrj == QMessageBox.Yes:
                self.main_window.saveProject()
        
        # 加载新工程
        if self.main_window.addProject(path):
            self.main_window.new = False
            self.manager.add_recent_file(path)
            title = self.main_window.title
            self.main_window.setWindowTitle(f"{os.path.basename(path).split('.')[0]} - {title.split(' - ')[1] if title.find('-')>=0 else title}")
        else:
            show_info_message(self.main_window, "打开工程", f"无法加载工程: {path}")


class RecentFilesManager(QObject):
    """管理最近打开的文件列表"""
    files_changed = pyqtSignal(list)  # 当列表变化时发出信号

    def __init__(self, max_files=5):
        super().__init__()
        self.max_files = max_files
        self.settings = QSettings()
        self.recent_files = self.load_recent_files()

    def load_recent_files(self):
        """从QSettings加载最近文件列表"""
        files = self.settings.value("recent_files", [])
        return files if isinstance(files, list) else []

    def save_recent_files(self):
        """保存最近文件列表到QSettings"""
        self.settings.setValue("recent_files", self.recent_files)

    def add_recent_file(self, file_path):
        """添加一个新文件到列表"""
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        
        self.recent_files.insert(0, file_path)
        
        # 限制最大数量
        if len(self.recent_files) > self.max_files:
            self.recent_files = self.recent_files[:self.max_files]
        
        self.save_recent_files()
        self.files_changed.emit(self.recent_files)

    def clear_recent_files(self):
        """清空最近文件列表"""
        self.recent_files = []
        self.save_recent_files()
        self.files_changed.emit(self.recent_files)