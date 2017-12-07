#-*- encoding: utf-8 -*-

from socket import *
from avenueProtocol.SapMessage import *

class SapConnection:
    def __init__(self):
        self.host = ''
        self.port = 80
        self.serviceID = []
        self.addr = (self.host, self.port)
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
    def setHostPort(self,host,port):
        self.host = host
        self.port = port
        self.addr = (self.host, self.port)
        
    def connectToSapServer(self):
        try:
            self.client.connect(self.addr)
        except BaseException as e:
            print("连接服务端失败：%s",e)
    


if __name__=="__main__":
    testsocket = SapConnection()
    testsocket.setHostPort('10.152.21.136', 8540)
    
    testsocket.connectToSapServer()
    
    temp = SapEncoder(ESapPacketType.SAP_PACKET_REQUEST.value,59403,11,0)
    temp.sm_dwSeq += 1
    
    temp.m_header.dwSequence = socket.htonl(temp.sm_dwSeq)
    
    #temp.setIntValue(28, 28, 4)
    
    #temp.setStringValue(29, b'abc', 3)
    
    value = '1111111'
    
    temp.setIntValue(1, 8, 4)
    temp.setStringValue(881, bytes(value, encoding = "utf8"), len(value))
    temp.combineContent()
    
    
    num = testsocket.client.send(temp.content)
    print(num)
    


    