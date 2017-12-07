from enum import Enum;
from pickle import FALSE
from collections import defaultdict
import string
import xml.dom.minidom

#type
class EValueType(Enum):
    MSG_FIELD_INT=1
    MSG_FIELD_STRING=2
    MSG_FIELD_ARRAY=3
    MSG_FIELD_TLV=4
    MSG_FIELD_STRUCT=5
    MSG_FIELD_ALL=6

#configField
class stConfigField:
    def __init__(self):
        self.strName=''
        self.strTypeName=''
        self.bRequested=False
        self.bAutoSet=False
        self.strConfigField=''
        self.nMaxLen=0
        self.nMinLen=0
        self.strRegex=''
        
        #for struct
        self.bStruct=False;
        self.eStructFieldType=EValueType;
        self.nLen=-1

        #default value
        self.bHasDefault=False
        self.nDefaultValue=0
        self.strDefaultValue=''
    
#configType
class stConfigType:
    def __init__(self):
        self.strName=''
        self.eType=EValueType
        self.nCode=0
        self.strItemType=''
        self.vecField=[]
        self.mapFieldByName={}
        self.mapFieldByType={}
        self.vecConfigField=[]
        
        #for array
        self.bArrayField=False
        self.strArraryName=''

        #for int or string default value
        self.bHasDefault=False
        self.nDefaultValue=0
        self.strDefaultValue=''

#configMsg
class stConfigMsg:
    def __init__(self):
        self.strName=''
        self.dwId=0
        self.bAckMsg=False
        self.oRequestType=stConfigType()
        self.oResponseType=stConfigType()
        self.mapArraryTypeNameByCode={}

class stConfigTypePair:
    def __init__(self):
        self.strPreviousTypeName=''
        self.strCurrentTypeName=''        

class CServiceConfig:
    
    def __init__(self):
        self.m_strServiceName=''
        self.m_strServiceId=0
        self.m_bIsTreeStruct=False
        self.m_mapETypeByName={}
        self.m_mapTypeByName={}
        self.m_mapTypeByCode={}
        #self.m_mapTypePairByFieldName={}
        self.m_mapTypePairByFieldName=defaultdict(list)
        self.m_mapMessageByName={}
        self.m_mapMessageById={}
        self.m_mapETypeByName["int"] = EValueType.MSG_FIELD_INT.value
        self.m_mapETypeByName["string"] = EValueType.MSG_FIELD_STRING.value
        self.m_mapETypeByName["systemstring"] = EValueType.MSG_FIELD_STRING.value
        self.m_mapETypeByName["array"] = EValueType.MSG_FIELD_ARRAY.value
        self.m_mapETypeByName["tlv"] = EValueType.MSG_FIELD_TLV.value
        self.m_mapETypeByName["struct"] = EValueType.MSG_FIELD_STRUCT.value
        
        return
    
    def GetFieldAttr_(self,pConfigField,bStruct):
        oConfigField = stConfigField()
        if pConfigField.hasAttribute("name"):
            oConfigField.strName = pConfigField.getAttribute("name")
        if pConfigField.hasAttribute("type"):
            fieldType = pConfigField.getAttribute("type")
        oConfigField.bStruct = bStruct
        if bStruct:
            oConfigField.eStructFieldType = self.m_mapETypeByName[fieldType]
            if pConfigField.hasAttribute("len"):
                oConfigField.nLen = (int)(pConfigField.getAttribute("len"))
            if pConfigField.hasAttribute("default"):
                oConfigField.bHasDefault = True
                if oConfigField.eStructFieldType == EValueType.MSG_FIELD_INT.value:
                    oConfigField.nDefaultValue = (int)(pConfigField.getAttribute("default"))
                else:
                    oConfigField.strDefaultValue = pConfigField.getAttribute("default")
        else:
            oConfigField.strTypeName = fieldType
        if pConfigField.hasAttribute("required"):
            bRequired = pConfigField.getAttribute("required")
            oConfigField.bRequested = True if (bRequired == "true") else False
        if pConfigField.hasAttribute("autoset"):
            bAutoSet = pConfigField.getAttribute("autoset")
            oConfigField.bAutoSet = True if (bAutoSet == "true") else False
        if pConfigField.hasAttribute("validatorregex"):
            oConfigField.strRegex = pConfigField.getAttribute("validatorregex")
        
        return oConfigField
        
        
    def LoadConfigTypeConfig(self,avenueType):
        oConfigType = stConfigType()
        if avenueType.hasAttribute("name"):
            oConfigType.strName = avenueType.getAttribute("name")
        if avenueType.hasAttribute("class"):
            oConfigType.eType = self.m_mapETypeByName[avenueType.getAttribute("class")]
        if avenueType.hasAttribute("code"):
            oConfigType.nCode = (int)(avenueType.getAttribute("code"))
        if avenueType.hasAttribute("itemType"):
            oConfigType.strItemType = avenueType.getAttribute("itemType")
        if avenueType.hasAttribute("default"):
            oConfigType.bHasDefault = True
            if oConfigType.eType == EValueType.MSG_FIELD_INT.value:
                oConfigType.nDefaultValue = (int)(avenueType.getAttribute("default"))
            if oConfigType.eType == EValueType.MSG_FIELD_STRING.value:
                oConfigType.strDefaultValue = avenueType.getAttribute("default")
        #print(oConfigType.strName,oConfigType.eType,oConfigType.nCode,oConfigType.bHasDefault,oConfigType.nDefaultValue,oConfigType.strDefaultValue)
        if oConfigType.eType == EValueType.MSG_FIELD_TLV.value or oConfigType.eType == EValueType.MSG_FIELD_STRUCT.value:
            pConfigFields = avenueType.getElementsByTagName("field")
            for pConfigField in pConfigFields:
                oConfigField = self.GetFieldAttr_(pConfigField,True)
                oConfigType.vecField.append(oConfigField)
                oConfigType.mapFieldByName[oConfigField.strName] = oConfigField
                oConfigType.mapFieldByType[oConfigField.strTypeName] = oConfigField
                if oConfigType.eType == EValueType.MSG_FIELD_STRUCT.value:
                    oConfigType.vecConfigField.append(oConfigField)
                    
        self.m_mapTypeByName[oConfigType.strName] = oConfigType
        if oConfigType.eType != EValueType.MSG_FIELD_ARRAY.value:
            self.m_mapTypeByCode[oConfigType.nCode] = oConfigType
                
        return oConfigType
    
    def LoadMsgField_(self,oConfigMsg,pReqFields,bRequest):
        pMsgFields = pReqFields.getElementsByTagName("field")
        for pMsgField in pMsgFields:
            oConfigField = self.GetFieldAttr_(pMsgField, False)
            oConfigTypePair = stConfigTypePair()
            oConfigTypePair.strCurrentTypeName = oConfigField.strTypeName
            if bRequest == True:
                oConfigMsg.oRequestType.vecField.append(oConfigField)
                (oConfigMsg.oRequestType.mapFieldByName)[oConfigField.strName] = oConfigField
                (oConfigMsg.oRequestType.mapFieldByType)[oConfigField.strTypeName] = oConfigField
                oConfigTypePair.strPreviousTypeName = oConfigMsg.oRequestType.strName
            else:
                oConfigMsg.oResponseType.vecField.append(oConfigField)
                (oConfigMsg.oResponseType.mapFieldByName)[oConfigField.strName] = oConfigField
                (oConfigMsg.oResponseType.mapFieldByType)[oConfigField.strTypeName] = oConfigField
                oConfigTypePair.strPreviousTypeName = oConfigMsg.oResponseType.strName
            itrTypeName = self.m_mapTypeByName[oConfigField.strTypeName]
            if itrTypeName.eType == EValueType.MSG_FIELD_ARRAY.value:
                itrItemTypeName = self.m_mapTypeByName[itrTypeName.strItemType]
                oConfigMsg.mapArraryTypeNameByCode[itrItemTypeName.nCode] = itrTypeName.strName
            #self.m_mapTypePairByFieldName[oConfigField.strName] = oConfigTypePair
            self.m_mapTypePairByFieldName[oConfigField.strName].append(oConfigTypePair)
            
    def LoadConfigMsgConfig(self,avenueMsg):
        oConfigMsg = stConfigMsg()
        if avenueMsg.hasAttribute("name"):
            oConfigMsg.strName = avenueMsg.getAttribute("name")
        if avenueMsg.hasAttribute("id"):
            oConfigMsg.dwId = (int)(avenueMsg.getAttribute("id"))
        if avenueMsg.hasAttribute("isack"):
            bAck = avenueMsg.getAttribute("isack")
            oConfigMsg.bAckMsg = True if (bAck == "true") else False
            
        oConfigMsg.oRequestType.strName = oConfigMsg.strName + "_Req"
        oConfigMsg.oRequestType.nCode = oConfigMsg.dwId
        oConfigMsg.oRequestType.eType = EValueType.MSG_FIELD_TLV.value
        pConfigFields = avenueMsg.getElementsByTagName("requestParameter")[0]
        self.LoadMsgField_(oConfigMsg, pConfigFields, True)
        self.m_mapTypeByName[oConfigMsg.oRequestType.strName] = oConfigMsg.oRequestType
        
        oConfigMsg.oResponseType.strName = oConfigMsg.strName + "_Res"
        oConfigMsg.oResponseType.nCode = oConfigMsg.dwId
        oConfigMsg.oResponseType.eType = EValueType.MSG_FIELD_TLV.value
        pConfigFields = avenueMsg.getElementsByTagName("responseParameter")[0]
        self.LoadMsgField_(oConfigMsg, pConfigFields, False)
        self.m_mapTypeByName[oConfigMsg.oResponseType.strName] = oConfigMsg.oResponseType
        
        self.m_mapMessageByName[oConfigMsg.strName] = oConfigMsg
        self.m_mapMessageById[oConfigMsg.dwId] = oConfigMsg
        
        return oConfigMsg
        
    def LoadServiceConfig(self,strConfigFile):
        try:
            ConfigTree = xml.dom.minidom.parse(strConfigFile)
            pService = ConfigTree.documentElement
            if pService.hasAttribute("name"):
                self.m_strServiceName = pService.getAttribute("name")
            if pService.hasAttribute("id"):
                self.m_strServiceId = (int)(pService.getAttribute("id"))
            if pService.hasAttribute("istreestruct"):
                if pService.getAttribute("istreestruct")=="true":
                    self.m_bIsTreeStruct=True
                else:
                    self.m_bIsTreeStruct=False
            
            types = pService.getElementsByTagName("type")
            for avenuetype in types:
                oConfigType = self.LoadConfigTypeConfig(avenuetype)
            messages = pService.getElementsByTagName("message")
            for avenueMsg in messages:
                oMessage = self.LoadConfigMsgConfig(avenueMsg)
                
            
        except BaseException as e:
            print('LoadServiceConfig error.')
            print(e)
            
        finally:
            return
        
    def GetMessages(self):
        messages = []
        for msgName in self.m_mapMessageByName.keys():
            messages.append(self.m_mapMessageByName[msgName].strName)
        return messages
    
    def GetTypeByName(self,strName):
        return self.m_mapTypeByName.get(strName)
    
    def GetTypeByCode(self,nCode):
        return self.m_mapTypeByCode.get(nCode)
    
    def GetMessageTypeByName(self,strName):
        return self.m_mapMessageByName.get(strName)
    
    def GetMessageTypeById(self,dwMsgId):
        return self.m_mapMessageById.get(dwMsgId)
    
    
'''
if __name__=="__main__":
    print("AvenueTestTools.")    
    sConfig=CServiceConfig()
    sConfig.LoadServiceConfig('C:\\Users\\Administrator\\eclipse-workspace\\AvenueTestTools\\src\\libConfig\\avenue_conf\\AccountCenter.xml')
    
    print(sConfig.m_mapTypePairByFieldName)
'''    
    
    
    
    
    
    
    