# -*- coding: utf-8 -*-
"""
    schtob.pyontapi.constants
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Pyontapi constants.

    :copyright: 2010-2015 Schaefer & Tobies SuC GmbH.
    :author: Markus Grimm <mgr@schaefer-tobies.de>;
             Uwe W. Schaefer <uws@schaefer-tobies.de>
    :license: LGPL, see LICENSE for details.
"""

HTTP = 'HTTP'
HTTPS = 'HTTPS'

LOGIN = 'LOGIN'
HOSTS = 'HOSTS'
CERTIFICATE = 'CERTIFICATE'

STYLES = (LOGIN, HOSTS, CERTIFICATE)
SERVER_TYPES = ('Filer', 'NetCache', 'Agent', 'DFM')
TRANSPORT_TYPES = (HTTP, HTTPS)

URLS = {
    'Filer': '/servlets/netapp.servlets.admin.XMLrequest_filer',
    'NetCache': '/servlets/netapp.servlets.admin.XMLrequest',
    'Agent': '/apis/XMLrequest',
    'DFM': '/apis/XMLrequest',
}

PORTS = {
    'Filer': 80,
    'NetCache': 80,
    'Agent': 4092,
    'DFM': 8081,
}
