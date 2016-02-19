# -*- coding: utf-8 -*-
"""
    schtob.pyontapi.na_http
    ~~~~~~~~~~~~~~~~~~~~~~~

    HTTP(S) Connections.

    :copyright: 2010-2015 Schaefer & Tobies SuC GmbH.
    :author: Markus Grimm <mgr@schaefer-tobies.de>;
             Uwe W. Schaefer <uws@schaefer-tobies.de>
    :license: LGPL, see LICENSE for details.
"""

import ssl
import socket
import sys


if sys.version_info < (3, 0):
    from httplib import HTTPConnection, HTTPSConnection
else:
    from http.client import HTTPConnection, HTTPSConnection


class HTTPSCaConnection(HTTPSConnection):
    """HTTPS Connection using client certificates."""

    def __init__(self, host, port, key_file, cert_file, ca_file,
                 cert_required=False, timeout=1.0):
        if sys.version_info < (2, 6):
            HTTPSConnection.__init__(self, host, port, key_file, cert_file)
        else:
            HTTPSConnection.__init__(self, host, port, key_file, cert_file,
                                     timeout=timeout)
        self._ca_file = ca_file
        self._cert_required = cert_required

    def connect(self):
        """Connect to the host and port specified in __init__."""
        sock = socket.create_connection((self.host, self.port), self.timeout)

        if self._cert_required:
            self.sock = ssl.wrap_socket(sock, self.key_file, self.cert_file,
                                        ca_certs=self._ca_file,
                                        cert_reqs=ssl.CERT_REQUIRED)
        else:
            self.sock = ssl.wrap_socket(sock, self.key_file, self.cert_file,
                                        ca_certs=self._ca_file)

    def peer_common_name(self):
        """Get the certificate common name."""
        for val in self.sock.getpeercert()['subject']:
            if val[0][0].lower() == 'commonname':
                return val[0][1]
        return ''

    def verify_certificate(self):
        """Verify server certificate."""
        return self.peer_common_name().lower() == self.host.lower()


RESPONSES = {
    100: 'Continue',
    101: 'Switching Protocols',
    102: 'Processing',
    118: 'Connection timed out',
    200: 'OK',
    201: 'Created',
    202: 'Accepted',
    203: 'Non-Authoritative Information',
    204: 'No Content',
    205: 'Reset Content',
    206: 'Partial Content',
    207: 'Multi-Status',
    300: 'Multiple Choices',
    301: 'Moved Permanently',
    302: 'Found',
    303: 'See Other',
    304: 'Not Modified',
    305: 'Use Proxy',
    306: '(Unused)',
    307: 'Temporary Redirect',
    400: 'Bad Request',
    401: 'Unauthorized',
    402: 'Payment Required',
    403: 'Forbidden',
    404: 'Not Found',
    405: 'Method Not Allowed',
    406: 'Not Acceptable',
    407: 'Proxy Authentication Required',
    408: 'Request Timeout',
    409: 'Conflict',
    410: 'Gone',
    411: 'Length Required',
    412: 'Precondition Failed',
    413: 'Request Entity Too Large',
    414: 'Request-URI Too Long',
    415: 'Unsupported Media Type',
    416: 'Requested Range Not Satisfiable',
    417: 'Expectation Failed',
    421: 'There are too many connections from your internet address',
    422: 'Unprocessable Entity',
    423: 'Locked',
    424: 'Failed Dependency',
    425: 'Unordered Collection',
    426: 'Upgrade Required',
    500: 'Internal Server Error',
    501: 'Not Implemented',
    502: 'Bad Gateway',
    503: 'Service Unavailable',
    504: 'Gateway Timeout',
    505: 'HTTP Version Not Supported',
    506: 'Variant Also Negotiates',
    507: 'Insufficient Storage',
    509: 'Bandwidth Limit Exceeded',
    510: 'Not Extended',
}
