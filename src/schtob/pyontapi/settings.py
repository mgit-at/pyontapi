# -*- coding: utf-8 -*-
"""
    schtob.pyontapi.settings
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Settings for the :class:`Filers` class. You may want to define
    authentication settings for all your storage systems here.

    See :ref:`configuration` for more details.

    :copyright: 2010-2015 Schaefer & Tobies SuC GmbH.
    :author: Markus Grimm <mgr@schaefer-tobies.de>;
             Uwe W. Schaefer <uws@schaefer-tobies.de>
    :license: LGPL, see LICENSE for details.
"""

from schtob.pyontapi import constants

# Define your NA_CONFIG here
NA_CONFIG = {
    'roles': {
        'default': {
            'user': 'root',
            'password': '',
            'style': constants.LOGIN,
        },
        'my-fancy-default-role': {
            'user': 'fancy-user',
            'cmd_list': ['file-get-file-info',
                         'file-inode-info',
                         'file-list-directory-iter-end',
                         'file-list-directory-iter-next',
                         'file-list-directory-iter-start',
                         'file-read-file',
                         'file-read-symlink',
                         ]
        },
    },

    'filer-roles': {

        'my-fancy-filer': {
            'default': {
                'password': 'fancy-password',
            },
            'yet-another-fancy-role-only-for-this-filer': {
                'user': 'yet-another-fancy-user',
            },
        },

        'yet-anoter-fancy-filer': {
            'fancy-role': {
                'server_type': 'DFM',
            },
        },

    }
    # 'vfiler': '',
    # 'server_type': 'Filer',
    # 'transport_type' : constants.HTTP,
    # 'port': None,
    # 'url': None,
}


def __import_local_settings():
    """Tries to import ``NA_CONFIG`` from `local_settings.py`."""
    try:
        return __import__('schtob.pyontapi.local_settings', {}, {},
                          ['NA_CONFIG']).NA_CONFIG
    except ImportError:
        return None
    except AttributeError:
        return None

if __import_local_settings():
    NA_CONFIG = __import_local_settings()
