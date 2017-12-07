import avenueProtocol.SapConnection
import libConfig.AddressConfig

class CSapConnectManager:
    def __init__(self):
        self.mapConnectByServiceId = {}
        
        self.addressConfigs = libConfig.AddressConfig.CAddressConfig()
        
        for serviceID in self.addressConfigs.mapAddrByServiceId.keys():
            sConnect = avenueProtocol.SapConnection.SapConnection()
            sConnectInfo = self.addressConfigs.mapAddrByServiceId[serviceID].split(':')
            sConnect.setHostPort(sConnectInfo[0], int(sConnectInfo[1]))
            
            sConnect.connectToSapServer()
            
            self.mapConnectByServiceId[int(serviceID)] = sConnect
        
        print(self.mapConnectByServiceId)
        
if __name__=="__main__":
    test = CSapConnectManager()