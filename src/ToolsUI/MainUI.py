#-*- encoding: utf-8 -*-

import sys
import socket
import avenueProtocol.SapMessage
import avenueProtocol.SapConnection
import avenueProtocol.SapConnectManager
import libConfig.AddressConfig
from libConfig.AvenueServiceConfigs import AvenueServiceConfigs
from PyQt5.QtGui import  QPixmap
#from PyQt5.QtCore import SIGNAL
from PyQt5.QtWidgets import QWidget, QApplication, QGroupBox, QPushButton, QLabel, QHBoxLayout,  QVBoxLayout, QGridLayout, QFormLayout, QLineEdit, QTextEdit,\
    QTreeWidget,QTreeWidgetItem,QTreeWidgetItemIterator, QLayoutItem
from libConfig.AddressConfig import CAddressConfig
from tkinter import messagebox

class MainWindow(QWidget):
    def __init__(self):
        self.avenueServiceConfigs = AvenueServiceConfigs()
        #self.addressConfigs = CAddressConfig()
        self.sapConnectManager = avenueProtocol.SapConnectManager.CSapConnectManager()
        self.params_widget_array = []
        self.params_value_dict = {}
        self.service_name = ''
        self.msg_name = ''
        super(MainWindow,self).__init__()
        self.initUi()
        

    def initUi(self):
        self.createGridGroupBox()
        self.creatVboxGroupBox()
        self.creatFormGroupBox()
        mainLayout = QVBoxLayout()
        hboxLayout = QHBoxLayout()
        #hboxLayout.addStretch() 
        hboxLayout.addWidget(self.gridGroupBox)
        hboxLayout.addWidget(self.vboxGroupBox)
        self.save_button = QPushButton('保存')
        self.save_button.resize(self.save_button.sizeHint())
        self.save_button.setMaximumSize(70, 40)
        self.save_button.clicked.connect(self.saveParams)
        
        self.run_button = QPushButton('运行')
        self.run_button.resize(self.run_button.sizeHint())
        self.run_button.setMaximumSize(70, 40)
        self.run_button.clicked.connect(self.sendAvenueRequest)
        
        
        mainLayout.addWidget(self.save_button)
        mainLayout.addWidget(self.run_button)
        mainLayout.addLayout(hboxLayout)
        mainLayout.addWidget(self.formGroupBox)
        self.setLayout(mainLayout)

    def clearLayout(self):
        self.params_widget_array.clear()
        while self.params_layout.count():
                child = self.params_layout.takeAt(0)
                if child.widget() is not None:
                    child.widget().deleteLater()
                elif child.layout() is not None:
                    self.clearLayout(child.layout())

    def saveParams(self):
        self.params_value_dict.clear()
        
        for params_widget in self.params_widget_array:
            self.params_value_dict[params_widget.objectName()] = params_widget.text()
        
        print(self.params_value_dict)

    def sendAvenueRequest(self):
        stConfig = self.avenueServiceConfigs.GetServiceByName(self.service_name)
        if stConfig is None:
            return
        message_type = stConfig.serviceConfig.GetMessageTypeByName(self.msg_name)
        if message_type is None:
            return
        
        serviceId = stConfig.dwId
        messsageId = message_type.dwId
        
        request = avenueProtocol.SapMessage.SapEncoder(avenueProtocol.SapMessage.ESapPacketType.SAP_PACKET_REQUEST.value,serviceId,messsageId,0)
        request.sm_dwSeq += 1
    
        request.m_header.dwSequence = socket.htonl(request.sm_dwSeq)
        
        sConnect = self.sapConnectManager.mapConnectByServiceId.get(serviceId)
        if sConnect is None:
            #messagebox.showinfo('提示', '服务未配置连接地址')
            return
        
        for key in self.params_value_dict.keys():
            fieldValue = self.params_value_dict[key]
            
            fieldName = message_type.oRequestType.mapFieldByName[key].strTypeName
            print(fieldName)
            fieldCode = (stConfig.serviceConfig.GetTypeByName(fieldName)).nCode
            fieldType = (stConfig.serviceConfig.GetTypeByName(fieldName)).eType
            print(fieldCode,fieldType)
            if fieldType == 1:
                request.setIntValue(fieldCode, int(fieldValue), 4)
            if fieldType == 2:
                request.setStringValue(fieldCode, bytes(fieldValue,encoding = "utf8"), len(fieldValue))
                
        request.combineContent()
        sConnect.client.send(request.content)
            

    def freshParamsPage(self,item):
        self.msg_name = item.text(0)
        msg_parent = item.parent()
        if msg_parent is None:
            return
        else:
            self.service_name = msg_parent.text(0)
            stConfig = self.avenueServiceConfigs.GetServiceByName(self.service_name)
            message_type = stConfig.serviceConfig.GetMessageTypeByName(self.msg_name)
            
            #刷新参数页面
            self.clearLayout()
            
            for field_name in message_type.oRequestType.mapFieldByName.keys():
                #nameLabel = QLabel(field_name)
                lineEditor = QLineEdit()
                lineEditor.setObjectName(field_name)
                
                self.params_widget_array.append(lineEditor)
                
                #self.params_layout.addWidget(nameLabel)
                #self.params_layout.addWidget(lineEditor)
                self.params_layout.addRow(field_name,lineEditor)
            
            self.vboxGroupBox.setLayout(self.params_layout)
            #print(self.params_widget_array)
            

    def createGridGroupBox(self):
        self.gridGroupBox = QGroupBox("测试项")
        layout = QVBoxLayout()
        
        self.avenueServiceConfigs.LoadAvenueServiceConfigs()
        snames = self.avenueServiceConfigs.GetServiceNames()
        print(snames)
        
        self.serviceTree = QTreeWidget()
        self.serviceTree.setColumnCount(1)
        self.serviceTree.setHeaderLabels(['服务名.消息名'])
        for sname in snames:
            child1 = QTreeWidgetItem(self.serviceTree)
            child1.setText(0,sname)
            stConfig = self.avenueServiceConfigs.GetServiceByName(sname)
            mnames = stConfig.serviceConfig.GetMessages()
            for mname in mnames:
                child2 = QTreeWidgetItem(child1)
                child2.setText(0,mname)
            
            
        self.serviceTree.setColumnWidth(0,100)
        self.serviceTree.itemClicked.connect(self.freshParamsPage)
    
        
        layout.addWidget(self.serviceTree)
        
        self.gridGroupBox.setLayout(layout)
        self.setWindowTitle('')

    def creatVboxGroupBox(self):
        self.vboxGroupBox = QGroupBox("参数")
        self.params_layout = QFormLayout() 
        
        self.vboxGroupBox.setLayout(self.params_layout)

    def creatFormGroupBox(self):
        self.formGroupBox = QGroupBox("")
        layout = QFormLayout()
        
        planLabel = QLabel("返回结果：")
        planEditor = QTextEdit()
        planEditor.setPlainText("")
        
        layout.addRow(planLabel,planEditor)

        self.formGroupBox.setLayout(layout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())

    
    