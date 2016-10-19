import xml.etree.ElementTree as ET
from os.path import isfile
import pkgutil
##My import
from ftp_backup.settings import DEBUG
from ftp_backup.modules import Device
##Configuration
class Configuration:
    """Configuration containing the devices"""
    #Class parameters:
    #devices[]
    #tree
    #root
    def __init__(self,configuration_file_path):
        self.default_configuration_file_path='data/default_configuration_file.cfg'
        self.devices=[]
        if not isfile(configuration_file_path): #create file
            self.createConfigurationFile(configuration_file_path)
        self.tree=ET.parse(configuration_file_path)
        self.root=self.tree.getroot()
        for deviceE in self.root.iter('device'):
            self.devices.append(Device.fromDeviceElement(deviceE))
    def write(self,configuration_file_path):
        #deleting all devices
        for deviceE in self.root.findall('device'):
            self.root.remove(deviceE)
        #re-adding devices
        for device in self.devices:
            self.root.append(device.getDeviceElement())
        #writing new file
        self.tree.write(configuration_file_path)
        if DEBUG:
            ET.dump(self.root)
    def createConfigurationFile(self,configuration_file_path):
        print('Writing default configuration file...')
        configuration_file=open(configuration_file_path,'wb')
        configuration_file.write(pkgutil.get_data(__name__,self.default_configuration_file_path))
        configuration_file.close()
        print('Configuration file created in ',configuration_file_path,'\nYou can modify it manually at your own risk')
    def addDevice(self,device):
        if not self.checkAvaibleDeviceName(device.name):
            print('Name already used!')
            exit(-1)
        self.devices.append(device)
    def checkAvaibleDeviceName(self,name):
        for device in self.devices:
            if device.name == name:
                if DEBUG:
                    print('Name not avaible')
                return False
        if DEBUG:
            print('Name avaible')
        return True
    def addFolderToDevice(self,device,folder):
        #Search the name
        i=0
        try:
            while self.devices[i].name != device:
                i+=1
        except IndexError:
            print('Device name not found!')
            exit(-1)
        self.devices[i].addFolder(folder)
    def removeFolderFromDevice(self,device_name,folder_name):
        for device in self.devices:
            if device.name == device_name:
                device.removeFolder(folder_name)
                return
        print('Device not found')
    def removeDevice(self,device_name):
        for device in self.devices:
            if device.name == device_name:
                self.devices.remove(device)
                return
        print('Device not found')
    def printConfiguration(self,allf=False,device_name=None):
        for device in self.devices:
            if (not device_name) or (device_name == device.name):
                device.printDevice(allf)
                if device_name:
                    return
    def backup(self,device_name=None,folder=None,ignore_downloaded=False):
        for device in self.devices:
            if (not device_name) or (device_name == device.name):
                device.backup(folder,ignore_downloaded)
                if device_name:
                    break
##End Configuration
