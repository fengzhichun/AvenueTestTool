#-*- encoding: utf-8 -*-

from enum import Enum
from pickle import FALSE
from collections import defaultdict
import string
import socket
from ctypes import *
from _testcapi import pyobject_malloc_without_gil
from test.test_buffer import struct
from _socket import htonl
from test.test_typechecks import Integer


SAP_BUFFER_INIT_CAPACITY = 8192

def sapAlign(size):
    return (size + 2047) & ~2047

#四字节对齐
def sap4bytesAlign(len):
    if (len & 0x03) != 0:
        return ((len>>2)+1)<<2
    else:
        return len

#type
class ESapPacketType(Enum):
    SAP_PACKET_REQUEST=0xA1
    SAP_PACKET_RESPONSE=0xA2
    

class SapMsgHeader(Structure):
    _pack_ = 1
    _fields_ = [
        ("byIdentifer",c_ubyte),
        ("byHeadLen",c_ubyte),
        ("byVersion",c_ubyte),
        ("byM",c_ubyte),
        ("dwPacketLen",c_uint32),
        ("dwServiceId",c_uint32),
        ("dwMsgId",c_uint32),
        ("dwSequence",c_uint32),
        ("byContext",c_ubyte),
        ("byPrio",c_ubyte),
        ("byBodyType",c_ubyte),
        ("byCharset",c_ubyte),
        ("dwCode",c_uint32),
        ("bySignature",c_ubyte * 16)
    ]
    
class SapMsgAttribute(Structure):
    _fields_ = [
        ("wType",c_ushort),
        ("wLength",c_ushort),
        ("acValue",c_ubyte * 0)
    ]    
    
'''    
class CSapBuffer:
    def __init__(self,capacity):
        self.capacity_ = capacity
        self.loc_ = 0
        self.base_ = (c_char_p)pyobject_malloc_without_gil
'''        
    
class SapEncoder:
    sm_dwSeq = 0
    
    def __init__(self,byIdentifer,dwServiceId,dwMsgId,dwCode):
        
        self.m_buffer = bytearray(SAP_BUFFER_INIT_CAPACITY)
        self.m_header = SapMsgHeader()
        
        self.m_header.byIdentifer = byIdentifer
        #self.m_header.byHeadLen = struct.pack('=B',hsize)
        self.m_header.byHeadLen = sizeof(SapMsgHeader) & 0xFF
        #print("%x" % self.m_header.byHeadLen)
        self.m_header.byVersion = 0x01
        self.m_header.byM = 0xFF
        
        self.m_header.dwPacketLen = socket.htonl(sizeof(SapMsgHeader))
        self.m_header.dwServiceId = socket.htonl(dwServiceId)
        self.m_header.dwMsgId = socket.htonl(dwMsgId)
        self.m_header.dwSequence = 0    
        
        self.m_header.byContext = 0
        self.m_header.byPrio = 0
        self.m_header.byBodyType = 0
        self.m_header.byCharset = 1
        
        self.m_header.dwCode = socket.htonl(dwCode)
        
        #self.content = string_at(addressof(self.m_header), sizeof(self.m_header))
        self.content = b''
        self.body = b''
        
        print(string_at(addressof(self.m_header), sizeof(self.m_header)))
        
        
        
        #print(self.m_header.dwPacketLen.__class__,self.m_header.dwServiceId.__class__)
        #memmove(addressof(self.m_buffer),addressof(self.m_header),sizeof(self.m_header))
        #self.m_buffer[0:sizeof(SapMsgHeader)] = self.m_header
        
        #print(self.m_buffer[0:44])
        #print(self.m_buffer[8:11])
        
    def setIntValue(self,key,value,value_len):
        intMsgAttribute = SapMsgAttribute()
        intMsgAttribute.wType = socket.htons(key)
        intMsgAttribute.wLength = socket.htons(sizeof(SapMsgAttribute)+value_len)
        
        nFactLen = sap4bytesAlign(value_len)
        
        hValue = socket.htonl(value)
        
        packetLen = socket.ntohl(self.m_header.dwPacketLen) + nFactLen + sizeof(intMsgAttribute)
        self.m_header.dwPacketLen = socket.htonl(packetLen)
        
        
        
        self.body += string_at(addressof(intMsgAttribute), sizeof(intMsgAttribute))
        
        self.body += struct.pack('>l',value)
        
        
    def setStringValue(self,key,value,value_len):
        strMsgAttribute = SapMsgAttribute()
        strMsgAttribute.wType = socket.htons(key)
        strMsgAttribute.wLength = socket.htons(sizeof(SapMsgAttribute)+value_len)
        
        nFactLen = sap4bytesAlign(value_len)
        packetLen = socket.ntohl(self.m_header.dwPacketLen) + nFactLen + sizeof(strMsgAttribute)
        self.m_header.dwPacketLen = socket.htonl(packetLen)
        
        
        
        self.body += string_at(addressof(strMsgAttribute), sizeof(strMsgAttribute))
        self.body += struct.pack(str(value_len) + 's', value)
        
        
        for i in range(nFactLen-value_len):
            self.body += b'\0'
        
    def combineContent(self):
        self.content = string_at(addressof(self.m_header), sizeof(self.m_header))
        self.content += self.body
        print(self.content)
        
        
    
'''
if __name__=="__main__":
    temp = SapEncoder(ESapPacketType.SAP_PACKET_REQUEST.value,31,1,2)
    temp.sm_dwSeq += 1
    
    temp.m_header.dwSequence = socket.htonl(temp.sm_dwSeq)
    
    temp.setIntValue(28, 28, 4)
    
    temp.setStringValue(29, b'abc', 3)
''' 
        
    
    
    #print(sConfig.m_mapTypePairByFieldName)    