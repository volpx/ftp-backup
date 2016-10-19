import xml.etree.ElementTree as ET
from ftplib import FTP
##My import
from ftp_backup.modules import Folder
from ftp_backup.settings import DEBUG
##Device
class Device:
    """Device class represent a device with all its configuration"""
    def __init__(self,name,address,port=0,user='',passwd='',enable=True,folders=None):
        self.name=name
        self.address=address
        self.enable=enable
        self.folders=[] if not folders else folders
        if port:
            self.port=port
        if user:
            self.user=user
            self.passwd=passwd
    @classmethod
    def fromDeviceElement(cls,deviceE):
        port=int(deviceE.get('port')) if deviceE.get('port') else 0
        user=deviceE.get('user') if deviceE.get('user') else ''
        passwd=deviceE.get('passwd') if deviceE.get('passwd') else ''
        enable=deviceE.get('enable')== 'true'
        folders=[]
        for folderE in deviceE.iter('folder'):
            folders.append(Folder.fromFolderElement(folderE))
        return cls(deviceE.get('name'),deviceE.get('address'),port,user,passwd,enable,folders)

    def getDeviceElement(self):
        deviceE=ET.Element('device')
        deviceE.set('name',self.name)
        deviceE.set('address',self.address)
        deviceE.set('enable',('true' if self.enable else 'false'))
        if hasattr(self,'port'):
            deviceE.set('port',str(self.port))
        if hasattr(self,'user'):
            deviceE.set('user',self.user)
            deviceE.set('passwd',self.passwd)
        for folder in self.folders:
            deviceE.append(folder.getFolderElement())
        return deviceE
    def addFolder(self,folder):
        if not self.checkAvaibleFolderName(folder.name):
            print('Folder name already used!')
            exit(-1)
        self.folders.append(folder)
    def removeFolder(self,folder_name):
        for folder in self.folders:
            if folder.name == folder_name:
                self.folders.remove(folder)
                return
        print('Folder not found')
    def printDevice(self,if_folders=False):
        print('Device')
        print('\tName:',self.name,'\n\tAddress:',self.address)
        if hasattr(self,'port'):
            print('\tPort:',self.port)
        if hasattr(self,'user'):
            print('\tUser:',self.user,'\n\tPasswd:',self.passwd)
        print('\tEnable:',self.enable)
        if if_folders:
            for folder in self.folders:
                folder.printFolder()
    def checkAvaibleFolderName(self,name):
        for folder in self.folders:
            if folder.name == name:
                if DEBUG:
                    print('Name not avaible')
                return False
        if DEBUG:
            print('Name avaible')
        return True
    def backup(self,folder_name=None,ignore_downloaded=False):
        if not self.enable:
            print('Device',self.name,'disabled')
            return
        ftps=FTP()
        print('Connecting to device',self.name,'at',self.address)
        try:
            ftps.connect(self.address,getattr(self,'port',0)) ##connected
        except:
            print('Cannot connect to device')
            return
        if hasattr(self,'user'):
            print('Logging in to',self.name)
            try:
                ftps.login(self.user,self.passwd)
            except:
                print('Wrong user or password')
                return
        print('Connected to',self.name)
        for folder in self.folders:
            if (not folder_name) or (folder_name == folder.name):
                folder.backup(ftps,ignore_downloaded)
                if folder_name:
                    break
        ftps.close()
##End Device
