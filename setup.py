#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    setup
    ~~~~~

    Pyontapi setup script.

    :copyright: 2010-2015 Schaefer & Tobies SuC GmbH.
    :author: Markus Grimm <mgr@schaefer-tobies.de>;
             Uwe W. Schaefer <uws@schaefer-tobies.de>
    :license: LGPL, see LICENSE for details.
"""

import distutils.core
import os
import shutil
import sys
import tempfile


def main():
    """ run distutils.setup """

    # Exclude local_settings.py from being added to package/installation
    local_settings_py = os.path.join('src', 'schtob', 'pyontapi',
                                     'local_settings.py')
    temp_file_path = None
    if os.path.exists(local_settings_py):
        temp_file_path = os.path.join(tempfile.gettempdir(),
                                      'pyontapi_local_settings.py')
        shutil.move(local_settings_py, temp_file_path)

    handle = open(local_settings_py, 'w')
    handle.write('')
    handle.close()

    sys.path.append('src')
    from schtob.pyontapi import VERSION

    distutils.core.setup(
        name='Pyontapi',
        version=VERSION,
        description='Python NetApp ONTAPI Implementation',
        long_description=('Pyontapi is a Python implementation '
                          'for the NetApp ONTAP API. It automatically '
                          'generates Python methods according to the ONTAPI '
                          'version of your NetApp filer using the system-api-*'
                          ' API commands.'),
        author='Markus Grimm, Uwe W. Schäfer',
        author_email='mgr@schaefer-tobies.de',
        url='http://pyontapi.schaefer-tobies.de',
        download_url='http://pyontapi.schaefer-tobies.de/dist/%s/'
                     'Pyontapi-%s.tar.gz' % (VERSION, VERSION),
        license='LGPL',
        platforms=['POSIX', 'Windows'],
        packages=['schtob', 'schtob.pyontapi'],
        package_dir = {'': 'src'},
        scripts=[os.path.join('bin', 'pyontapi_list_commands.py')],
        classifiers=[
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.4',
            'Programming Language :: Python :: 2.5',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.0',
            'Programming Language :: Python :: 3.1',
            'Programming Language :: Python :: 3.2',
            'Operating System :: POSIX',
            'Operating System :: Microsoft',
            'Operating System :: MacOS',
        ]
    )

    # restore local_settings.py
    if temp_file_path:
        shutil.move(temp_file_path, local_settings_py)


if __name__ == '__main__':
    main()