from qgis.PyQt.QtCore import QThread, pyqtSignal
from xml.dom import minidom
from lxml import etree

class QuerySampleThread(QThread):
    finished = pyqtSignal(object)  # 用于将数据从子线程发送到主线程的信号
    
    def __init__(self, ui):
        super().__init__()
        self.ui = ui

    def run(self):
        # 在这里执行耗时任务，并使用self.param
        result = self.do_work()
        self.finished.emit(result)  # 发送信号，并将结果作为参数传递

    def do_work(self):
        sampleClass = self.ui.comboBox_Class.currentText()
        sampleSize = self.ui.comboBox_Size.currentText()
        sampleType = self.ui.comboBox_Type.currentText()
        sampleGSD = self.ui.comboBox_GSD.currentText()
        sampleName = self.ui.comboBox_Name.currentText()
        self.sampleList = []
        from DeeplearningSystem import sample_cofing_path
        # 加载现有 XML
        tree = etree.parse(sample_cofing_path)
        if sampleClass == '':
            nodes = tree.xpath(f'//SamplePath')
            for i,node in enumerate(nodes):
                self.sampleList.append(node.text)
            return
        if sampleSize == '':
            nodes = tree.xpath(f'//SampleClass[@EnglishName="{sampleClass}"]/SamplePath')
            for i,node in enumerate(nodes):
                self.sampleList.append(node.text)
            return
        if sampleType == '':
            nodes = tree.xpath(f'//SampleClass[@EnglishName="{sampleClass}"]/SamplePath[@Size="{sampleSize}"]')
            for i,node in enumerate(nodes):
                self.sampleList.append(node.text)
            return
        if sampleGSD == '':
            nodes = tree.xpath(f'//SampleClass[@EnglishName="{sampleClass}"]/SamplePath[@Size="{sampleSize}" and @Type="{sampleType}"]')
            for i,node in enumerate(nodes):
                self.sampleList.append(node.text)
            return
        if sampleName == '':
            nodes = tree.xpath(f'//SampleClass[@EnglishName="{sampleClass}"]/SamplePath[@Size="{sampleSize}" and @Type="{sampleType}" and @GSD="{sampleGSD}"]')
            for i,node in enumerate(nodes):
                self.sampleList.append(node.text)
            return
        nodes = tree.xpath(f'//SampleClass[@EnglishName="{sampleClass}"]/SamplePath[@Size="{sampleSize}" and @Type="{sampleType}" and @GSD="{sampleGSD}" and @Name="{sampleName}"]')
        for i,node in enumerate(nodes):
            self.sampleList.append(node.text)       
        return 'query sucess'