#!/usr/bin/env python3

#ftp-backup setup.py
from setuptools import setup,find_packages
from ftp_backup.settings import version,author,email
setup(
    name='ftp-backup',
    packages = find_packages(),
    version=version,
    description='Backup utility for smartphones through ftp',
    author=author,
    author_email=email,
    license='GNU General Public License v3(GPLv3)',
    url='https://github.com/volpx/ftp-backup',
    keywords=['ftp','backup','utility','smartphone'],
    package_data={
        'ftp_backup.modules':['data/default_configuration_file.cfg']
    },
    entry_points={
        'console_scripts':[
            'ftp-backup = ftp_backup.ftp_backup_main:main'
        ]
    },
    extras_require={
        'Dialog':['pythondialog']
    }
)
