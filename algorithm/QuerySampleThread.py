from qgis.PyQt.QtCore import QThread, pyqtSignal
from xml.dom import minidom

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
        dom = minidom.parse(sample_cofing_path)#Samples
        root = dom.documentElement
        for child in root.childNodes:#SampleClass
            if child.nodeType == child.ELEMENT_NODE:
                for __, attr_value in child.attributes.items():                       
                    if attr_value == sampleClass:                                   
                        for child2 in child.childNodes:#SamplePath
                            if child2.nodeType == child2.ELEMENT_NODE:                              
                                samplePath = child2.firstChild.data.strip()
                                data_dict = {}
                                for key, value in child2.attributes.items():
                                    data_dict[key] = value
                                size = data_dict['Size']
                                type = data_dict['Type']
                                gsd = data_dict['GSD']
                                name = data_dict['Name']
                                if (sampleSize==size or sampleSize=='') and (sampleType==type or sampleType=='') and (sampleGSD==gsd or sampleGSD=='') and (sampleName==name or sampleName==''):
                                    self.sampleList.append(samplePath)
        return 'query sucess'