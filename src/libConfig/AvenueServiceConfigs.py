import sys,os;
from libConfig.ServiceConfig import CServiceConfig
from test.test_heapq import SideEffectLT


File_Format = [".xml"]

class stServiceConfig:
    def __init__(self):
        self.dwId=0
        self.strName=''
        self.serviceConfig=CServiceConfig()

class AvenueServiceConfigs:
    def __init__(self):
        self.m_mapSConfigBySname={}
        self.m_mapSConfigBySid={}
       
    def curPathDir(self):
        #path = sys.path[0]
        path = os.path.split(os.path.realpath(__file__))[0]
        '''
        if os.path.isdir(path):
            return path
        elif os.path.isfile(path):
            return os.path.dirname(path)    
        '''
        return path
        
    def LoadAvenueServiceConfigs(self):
        global File_Format
        curPath = self.curPathDir()
        curAvenuePath = curPath + "\\avenue_conf"
        for filename in os.listdir(curAvenuePath):
            avenueXMLPath = os.path.join(curAvenuePath,filename)
            if os.path.isfile(avenueXMLPath):
                if os.path.splitext(avenueXMLPath)[1] in File_Format:
                    stSConfig = stServiceConfig()
                    stSConfig.serviceConfig.LoadServiceConfig(avenueXMLPath)
                    stSConfig.dwId = stSConfig.serviceConfig.m_strServiceId
                    stSConfig.strName = stSConfig.serviceConfig.m_strServiceName
                    
                    self.m_mapSConfigBySname[stSConfig.strName] = stSConfig
                    self.m_mapSConfigBySid[stSConfig.dwId] = stSConfig
        
        
    def GetServiceById(self,sId):
        return self.m_mapSConfigBySid.get(sId)
    
    def GetServiceByName(self,sName):
        return self.m_mapSConfigBySname.get(sName)
    
    def GetServiceIdByName(self,strServiceName):
        strNames = strServiceName.split('.',1)
        serviceName = strNames[0]
        msgName = strNames[1]
        stServiceConfig = self.m_mapSConfigBySname.get(serviceName)
        serviceId = stServiceConfig.dwId
        msgId = stServiceConfig.serviceConfig.m_mapMessageByName.get(msgName).dwId
        return serviceId,msgId
    
    def GetServiceIdByName2(self,strServiceName):
        stServiceConfig = self.m_mapSConfigBySname.get(strServiceName)
        return stServiceConfig.dwId
    
    def GetServiceNameById(self,dwServiceId,dwMsgId):
        stServiceConfig = self.m_mapSConfigBySid.get(dwServiceId)
        msgName = stServiceConfig.serviceConfig.m_mapMessageById.get(dwMsgId).strName
        return stServiceConfig.strName + '.' + msgName
    
    def GetServiceNames(self):
        serviceNames = []
        for sName in self.m_mapSConfigBySname.keys():
            serviceNames.append(self.m_mapSConfigBySname[sName].strName)
        return serviceNames
        

if __name__=="__main__":
    print("AvenueTestTools.")
    avenueServiceConfigs = AvenueServiceConfigs()
    avenueServiceConfigs.LoadAvenueServiceConfigs()
    
    test = avenueServiceConfigs.GetServiceIdByName('SAS.addInnerAccount')
    print(test)
    test = avenueServiceConfigs.GetServiceNameById(23, 2348)
    print(test)
    print(avenueServiceConfigs.m_mapSConfigBySname)
        
    