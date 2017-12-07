import xml.dom.minidom
import os

class CAddressConfig:
    
    def __init__(self):
        self.mapAddrByServiceId = {}
        self.LoadAddressConfig()
        
    def LoadAddressConfig(self):
        ConfigTree = xml.dom.minidom.parse(os.path.split(os.path.realpath(__file__))[0] + "\\config.xml")
        rootConfig = ConfigTree.documentElement
        
        sosLists = rootConfig.getElementsByTagName("SosList")
        for sosList in sosLists:
            serviceIDs = sosList.getElementsByTagName("ServiceId")[0]
            serviceIDsContent = serviceIDs.childNodes[0].nodeValue
            serviceAddr = sosList.getElementsByTagName("ServerAddr")[0]
            serviceAddrContent = serviceAddr.childNodes[0].nodeValue
            
            sIDArray = serviceIDsContent.split(',')
            for sID in sIDArray:
                self.mapAddrByServiceId[sID] = serviceAddrContent
        

'''
if __name__=="__main__":
    test = CAddressConfig()
    print(test.mapAddrByServiceId)
''' 
