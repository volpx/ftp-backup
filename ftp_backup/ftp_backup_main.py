
#TODO: check access through modules
#TODO: add test\check subprogram
import argparse
#my modules
from ftp_backup.modules import Folder,Device,Configuration,cli
from ftp_backup.settings import version,DEBUG,author,email,configuration_file_path
#
def main():
    parser=argparse.ArgumentParser(description='Backup your smartphone wirelessly through ftp',epilog='Created by '+author+' ('+email+').')
    parser.add_argument('-v','--version',action='version',version='ftp-backup v'+version)
    parser.add_argument('--gui',action='store_true',help='use the GUI')
    parser.add_argument('--cli',action='store_true',help='use the CLI')
    #subparsers
    subparsers=parser.add_subparsers(title='subparts',dest='sub')
    subparsers.add_parser('cli',help='use command line interface')
    subparsers.add_parser('gui',help='use graphic user interface')
    #parser_init
    parser_init=subparsers.add_parser('init',help='init a configuration')
    parser_init.add_argument('device_name',help='name of new device',metavar='DEV')
    parser_init.add_argument('address',help='address of ftp server',metavar='ADDR')
    parser_init.add_argument('-p','--port',help='set special port of ftp server',metavar='PORT')
    parser_init.add_argument('-u','--user',help='username to access ftp server',metavar='USER')
    parser_init.add_argument('-k','--passwd',help='password to access ftp server',metavar='PASS')
    parser_init.add_argument('-e','--enable',action='store_true',help='enable immediately the device')
    parser_init.set_defaults(func=initf)
    #parser_modconf
    parser_modconf=subparsers.add_parser('modconf',help='modify the configuration')
    parser_modconf.add_argument('device',help='name of device to modify',metavar='DEV')
    parser_modconf.add_argument('-f','--remove-folder',help='remove a folder from configuration',metavar='FOLD')
    parser_modconf.add_argument('-d','--remove-device',action='store_true',help='delete device')
    parser_modconf.set_defaults(func=modconf)
    #parser_addfolder
    parser_addfolder=subparsers.add_parser('addfolder',help='add a folder')
    parser_addfolder.add_argument('device',help='name of device to modify',metavar='DEV')
    parser_addfolder.add_argument('name',help='name of folder',metavar='NAME')
    parser_addfolder.add_argument('source',help='source folder',metavar='SOUR')
    parser_addfolder.add_argument('destination',help='destination folder',metavar='DEST')
    parser_addfolder.add_argument('-f','--filter-type',choices=['e','o'],help='filter type',metavar='FT',default='e')
    parser_addfolder.add_argument('-s','--filter-string',help='filter string',metavar='FS',default='')#the filter string is like 'png,pdf,doc'
    parser_addfolder.add_argument('-i','--include-hidden',action='store_true',help='include hidden files')
    parser_addfolder.add_argument('-e','--enable',action='store_true',help='enable immediately the folder')
    parser_addfolder.add_argument('-R','--recursive',action='store_true',help='recursion through folders')
    parser_addfolder.set_defaults(func=addfolderf)
    #parser_list
    parser_list=subparsers.add_parser('list',help='list all devices')
    parser_list.add_argument('-a','--all',action='store_true',help='all devices with all folders')
    parser_list.add_argument('-d','--device',help='list folders of this device')
    parser_list.set_defaults(func=listf)
    #parser_backup
    parser_backup=subparsers.add_parser('backup',help='start backup')
    parser_backup.add_argument('-d','--device',help='start to backup selected device',metavar='DEV')
    parser_backup.add_argument('-f','--folder',help='backup only selected folder of device',metavar='FOLD')
    parser_backup.add_argument('-i','--ignore-downloaded',action='store_true',help='ignore already downloaded files and overwrite')
    parser_backup.set_defaults(func=backupf)
    ##parsing
    args=parser.parse_args()
    #handle the stuff
    if DEBUG:
        print(args)
    if args.sub == 'cli':
        cli()
        return
    if args.sub == 'gui':
        print('Sorry WIP')
        return
        from ftp_backup.modules import gui
        gui()
        return
    #if subprogram is called, call the proper function
    if hasattr(args,'func'):
        args.func(args)
        return
    #if nothing interrupt it will print the help
    parser.print_help()
def initf(args):
    conf=Configuration(configuration_file_path)
    if DEBUG:
        print('Adding device:',args.device_name)
    conf.addDevice(Device(args.device_name,args.address,args.port,args.user,args.passwd,args.enable))
    conf.write(configuration_file_path)
def addfolderf(args):
    conf=Configuration(configuration_file_path)
    if DEBUG:
        print('Adding folder:',args.device)
    conf.addFolderToDevice(args.device,Folder(args.name,args.source,args.destination,args.filter_type,args.filter_string,args.include_hidden,args.enable,args.recursive))
    conf.write(configuration_file_path)
def listf(args):
    conf=Configuration(configuration_file_path)
    conf.printConfiguration(args.all,args.device)
def modconf(args):
    conf=Configuration(configuration_file_path)
    if args.remove_device:
        conf.removeDevice(args.device)
    elif args.remove_folder:
        conf.removeFolderFromDevice(args.device,args.remove_folder)
    conf.write(configuration_file_path)
def backupf(args):
    conf=Configuration(configuration_file_path)
    conf.backup(args.device,args.folder,args.ignore_downloaded)

##Calling the main
if __name__ == '__main__':
    main()
