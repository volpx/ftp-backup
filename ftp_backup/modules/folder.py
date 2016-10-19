import xml.etree.ElementTree as ET
from os import makedirs
from os.path import isdir, isfile
##My import
from ftp_backup.settings import DEBUG, home
##Folder
class Folder:
    def __init__(self,name,source,dest,filter_type='e',filter_string='',include_hidden=False,enable=True,recursive=False):
        self.name=name
        self.source=source
        self.dest=dest
        self.include_hidden=include_hidden
        if filter_type not in ['o','e']:
            print('filter_type not valid')
        self.filter_type=filter_type
        self.filter_string=filter_string
        self.enable=enable
        self.recursive=recursive
    @classmethod
    def fromFolderElement(cls,folderE):
        return cls(folderE.get('name'),folderE.get('source'),folderE.get('dest'),folderE.get('filter_type'),folderE.get('filter_string'),(folderE.get('include_hidden') == 'true'),(folderE.get('enable') == 'true'),(folderE.get('recursive') == 'true'))

    def getFolderElement(self):
        folderE=ET.Element('folder')
        folderE.set('name',self.name)
        folderE.set('source',self.source)
        folderE.set('dest',self.dest)
        folderE.set('include_hidden','true' if self.include_hidden else 'false')
        folderE.set('filter_type',self.filter_type)
        folderE.set('filter_string',self.filter_string)
        folderE.set('enable','true' if self.enable else 'false')
        folderE.set('recursive','true' if self.recursive else 'false')
        return folderE
    def printFolder(self):
        print('Folder')
        print('\tName:',self.name,'\n\tSource:',self.source,'\n\tDest:',self.dest)
        if self.include_hidden:
            print('\tHidden included: true')
        if self.filter_type != 'e' or self.filter_string != '':
            print('\tFilter type:','only' if self.filter_type == 'o' else 'exclude','\n\tFilter string:',self.filter_string)
        if self.recursive:
            print('\tRecursive: true')
        print('\tEnable:',self.enable)
    def backup(self,ftps,ignore_downloaded=False):
        def getWordFromFirstIndex(line,index):
            word=''
            while index<len(line):
                word=word+line[index]
                index+=1
            return word
        def excludeAlreadyDownloadedFiles(files,dest):
            files1=[]
            for f in files:
                if not isfile(dest+'/'+f):
                    files1.append(f)
                else:
                    if DEBUG:
                        print('skipping already existing file',f)
            return files1
        def getExtensionFromFileName(filename): #return the extension without the '.'
            p=len(filename)-1#last character
            extension=[]
            while p != 0 and filename[p] != '.':
                extension.insert(0,filename[p])
                p-=1
            if p == 0:#if no extension or hidden file
                return ''
            return ''.join(extension)
        def getFileNames(retrlines,include_hidden=False,filter_type='e',filter_string=''):
            files=[]
            for line in retrlines:
                if line[0] == '-':##that's a file
                    p=0
                    for _ in range(0,8): #skip first eight whitespaces
                        while line[p] != ' ':
                            p+=1
                        p+=1
                    #p = first index of file name
                    if (line[p] != '.') or include_hidden:
                        extension=getExtensionFromFileName(getWordFromFirstIndex(line,p))
                        if ((filter_type == 'e') and ((extension not in filter_string.split(',')) or extension == '')) or ((filter_type == 'o') and (extension in filter_string.split(','))):
                            files.append(getWordFromFirstIndex(line,p))#this file need to be backed up
            return files
        def getFolderNames(retrlines,include_hidden):
            fnames=[]
            for line in retrlines:
                if line[0] == 'd': #thats a directory
                    p=0
                    for _ in range(0,8): #skip first eight whitespaces
                        while line[p] != ' ':
                            p+=1
                        p+=1
                    #p = first index of folder name
                    if (line[p] != '.') or include_hidden:
                        fnames.append(getWordFromFirstIndex(line,p))
            return fnames
        if not self.enable:
            print('Folder',self.name,'disabled')
            return
        current=ftps.pwd()
        try:
            ftps.cwd(self.source)
        except:
            print('Cannot cd into folder')
        lines=[]
        ftps.retrlines('LIST',lines.append)
        ftps.cwd(current)
        if DEBUG:
            print('Folder:',self.name)
        files=getFileNames(lines,self.include_hidden,self.filter_type,self.filter_string)
        #if tilde is used
        if self.dest[0] == '~':
            if DEBUG:
                print('replacing ~ with home directory:',self.dest)
            self.dest=self.dest.replace('~',home,1)
        #create destination folder if needed
        if not isdir(self.dest):
            if DEBUG:
                print('creating destination directory:',self.dest)
            makedirs(self.dest)
        #if a file is present in dest folder, don't download it twice
        if not ignore_downloaded:
            files=excludeAlreadyDownloadedFiles(files,self.dest)
        for name in files:
            print('[remote]',self.source+'/'+name,'>>> [local]',self.dest+'/'+name)
            ftps.retrbinary('RETR %s' % self.source+'/'+name,open(self.dest+'/'+name,'wb').write)
        if self.recursive:
            fnames=getFolderNames(lines,self.include_hidden)
            if len(fnames):
                print('Starting recursion in folder:',self.name,'for folders:',', '.join(fnames))
            for fname in fnames:
                Folder(fname,self.source+'/'+fname,self.dest+'/'+fname,filter_type=self.filter_type,filter_string=self.filter_string,include_hidden=self.include_hidden,enable=True,recursive=True).backup(ftps,ignore_downloaded)
##End Folder
