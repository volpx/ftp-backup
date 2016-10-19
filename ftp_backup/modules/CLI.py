import argparse
from ftplib import FTP
from shlex import split as shlex_split
from os.path import basename,isdir
##My import
from ftp_backup.settings import DEBUG,home
from ftp_backup.modules import Folder

def cli():
    cli_parser=argparse.ArgumentParser(add_help=False)
    cli_sub=cli_parser.add_subparsers(description='CLI commands',dest='cli_subprog')
    #
    cli_sub.add_parser('help',help='print help')
    #
    cli_connect=cli_sub.add_parser('connect',help='connect to a server')
    cli_connect.add_argument('address',metavar='ADDR')
    cli_connect.add_argument('-p','--port',metavar='PORT')
    #
    cli_login=cli_sub.add_parser('login',help='login to server')
    cli_login.add_argument('user',metavar='USER')
    cli_login.add_argument('passwd',metavar='PASSWD')
    #
    cli_sub.add_parser('disconnect',help='disconnect to a server')
    #
    cli_cd=cli_sub.add_parser('cd',help='change working directory')
    cli_cd.add_argument('folder',metavar='FOLD')
    #
    cli_download=cli_sub.add_parser('download',help='download from server')
    cli_download.add_argument('source',metavar='SOUR')
    cli_download.add_argument('destination',metavar='DEST')
    cli_download.add_argument('-a',action='store_true')
    cli_download.add_argument('-R',action='store_true')
    cli_download.add_argument('-i',action='store_true')
    #
    cli_ls=cli_sub.add_parser('ls',help='list directory')
    cli_ls.add_argument('-l',action='store_true')
    #
    cli_sub.add_parser('exit',help='exit from cli')
    #
    while True:
        while True:
            try:
                cli_args=cli_parser.parse_args(shlex_split(input('> ')))
                break
            except:
                print('\nInvalid stuff')
        if DEBUG:
            print(cli_args)
        cli_subprog=getattr(cli_args,'cli_subprog','')
        if cli_subprog == 'exit':
            if 'ftps' in locals():
                del ftps
            break
        elif cli_subprog == 'help':
            cli_parser.print_help()
        elif cli_subprog == 'connect':
            ftps=FTP()
            try:
                ftps.connect(cli_args.address,int(getattr(cli_args,'port',0)))
            except:
                print('Cannot connect to device')
                del ftps
                continue
            print('Connected')
        elif cli_subprog == 'login':
            if 'ftps' not in locals():
                print('connect first')
                continue
            try:
                ftps.login(cli_args.user,cli_args.passwd)
            except:
                print('Wrong user or password')
                continue
            print('Logged')
        elif cli_subprog == 'disconnect':
            if 'ftps' in locals():
                del ftps
            print('Disconnected')
        elif cli_subprog == 'cd':
            if 'ftps' not in locals():
                print('connect first')
                continue
            try:
                ftps.cwd(cli_args.folder)
            except:
                print('Cannot cd into folder')
                continue
            print(ftps.pwd())
            print('Folder changed')
        elif cli_subprog == 'ls':
            if 'ftps' not in locals():
                print('connect first')
                continue
            lines=[]
            try:
                ftps.retrlines('LIST',lines.append)
            except:
                print('Cannot ls, check connection or login')
            if cli_args.l:
                print('\n'.join(lines))
            else :
                files=[]
                folders=[]
                for line in lines:
                    p=0
                    #skip first seven whitespaces
                    for _ in range(0,8):
                        while line[p] is not ' ':
                            p+=1
                        p+=1
                    #p = first index of file name
                    word=''
                    while p<len(line):
                        word=word+line[p]
                        p+=1
                    if line[0] == '-':
                        files.append(word)
                    elif line[0] == 'd':
                        folders.append(word)
                print('Files:\n\t','\n\t'.join(files),'\nFolders:\n\t','\n\t'.join(folders),sep='')
        elif cli_subprog == 'download':
            def isFolder(ftps,path):
                current=ftps.pwd()
                try:
                    ftps.cwd(path)
                except:
                    ftps.cwd(current)
                    return False
                ftps.cwd(current)
                return True
            if 'ftps' not in locals():
                print('connect first')
                continue
            if isFolder(ftps,cli_args.source):
                #download all the inside
                Folder(cli_args.source,cli_args.source,cli_args.destination,recursive=cli_args.R,include_hidden=cli_args.a).backup(ftps,cli_args.i)
            else:
                #is a file
                dest=cli_args.destination
                if dest[0] == '~':
                    dest=dest.replace('~',home,1)
                if isdir(dest):
                    dest=dest+'/'+basename(cli_args.source)
                print('[remote]',ftps.pwd()+cli_args.source,'>>> [local]',dest)
                ftps.retrbinary('RETR %s' % cli_args.source,open(dest,'wb').write)
