# -*- coding: utf-8 -*-
"""
    schtob.pyontapi.na_filer
    ~~~~~~~~~~~~~~~~~~~~~~~~

    This module is used to invoke ONTAPI commands on a NetApp Filer, NetCache,
    Agent or DFM.

    :copyright: 2010-2015 Schaefer & Tobies SuC GmbH.
    :author: Markus Grimm <mgr@schaefer-tobies.de>;
             Uwe W. Schaefer <uws@schaefer-tobies.de>
    :license: LGPL, see LICENSE for details.
"""

import base64
import logging
import socket
import ssl
import sys
import xml.dom.minidom

from schtob.pyontapi import api, constants, errors, na_http, py_gen, system


# Custom log level for pyontap logger. set to logging.DEBUG for debugging
# if set to logging.NOTSET, the default logger settings are used
# visit http://docs.python.org/library/logging.html for more details.
LOG_LEVEL = logging.NOTSET


class NaFiler(object):
    """Create a new connection to filer `filer` using `settings` dict.

    `settings` may consist of the following entries:

        ================== ========= ===================================
        Key                Default   Possible values
        ================== ========= ===================================
        **user**           "root"    `str`
        **password**       ""        `str`
        **style**          `LOGIN`   `LOGIN`, `HOSTS`, `CERTIFICATE`
        **vfiler**         ""        `str`
        **server_type**    "Filer"   "Filer", "NetCache", "DFM", "Agent"
        **transport_type** `HTTP`    `HTTP`, `HTTPS`
        **port**           `None`    `int`
        **url**            `None`    `str`
        **cert_file**      ""        Path to Cert file
        **key_file**       ""        Path to Key file
        **ca_file**        ""        Path to Key file
        **cert_required**  False     `bool`
        **verify_cn**      False     `bool`
        **cmd_list**       'None'    'list of api_commands'
        ================== ========= ===================================

    """

    def __init__(self, filer, settings=None):
        self._filer = filer
        self._log = logging.getLogger('pyontapi')
        self._api_modules = {}

        self._log.setLevel(LOG_LEVEL)

        self._settings = {
            'cert_file': '',
            'cert_required': False,
            'key_file': '',
            'ca_file': '',
            'ontapi_version': '1.0',
            'password': '',
            'port': None,
            'server_type': 'Filer',
            'style': constants.LOGIN,
            'transport_type': constants.HTTP,
            'url': None,
            'user': 'root',
            'verify_cn': False,
            'vfiler': '',
        }

        if settings and isinstance(settings, dict):
            self.__test_settings(settings)
            self._settings.update(settings)

        if settings and isinstance(settings, dict):
            if 'transport_type' not in settings or \
               settings['transport_type'] == constants.HTTPS:
                # automatically try to use HTTPS if argument not specified or
                # if transport_type is set to HTTPS
                self.__test_https()
        self.__handle_servertype()
        self.__set_api_classes()

    def __set_api_classes(self):
        """Add all api classes as class attributes."""

        try:
            result = self.__get_ontapi_version()
        except errors.APIFailure:
            exc = sys.exc_info()[1]
            self._log.error("Cant't get ontapi version. error was: %s",
                            exc.get_error())
            raise errors.UnknownOntapiVersionError(
                exc.errno, "Cant't get ontapi version. error was:\n%s" %
                exc.reason)

        self._settings['ontapi_version'] = \
            '%(major-version)s.%(minor-version)s' % result

        api_modules = py_gen.generate(self)
        for key, value in api_modules.items():
            self._api_modules[key] = api.BaseAPI(self, value)
            setattr(self, key, self._api_modules[key])

    @property
    def settings(self):
        return self._settings

    def get_api_modules(self):
        """Get all API classes as a dictionary of `package_name`: `api_class`.
        """
        return self._api_modules

    def get_api_module(self, package_name):
        """Get API class for `package_name`."""
        return self._api_modules.get(package_name, None)

    def call(self, api_command_name, **kwargs):
        """Invoke `api_command_name` using `kwargs` as arguments.

        .. versionadded:: 0.2.5
        """
        bits = api_command_name.split('-')
        package_name = bits[0]
        command_name = '-'.join(bits[1:])
        try:
            api_module = self._api_modules[package_name]
        except KeyError:
            raise errors.UnknownCommandError(-1, 'No such api command %s' %
                                             api_command_name)
        return api_module.invoke_command(command_name, **kwargs)

    def do_api_call(self, api_command_name, arguments, fields):
        """Create new API call for `api_command_name` using `arguments` and
        return the result as a dictionary using `fields` to parse the
        response.
        """
        xmlcontent = self.__get_xml_content(api_command_name, arguments)
        self._log.debug('XML request: %s', xmlcontent.toprettyxml())

        content = xmlcontent.toxml(encoding='utf-8')

        def prepare_connection():
            """Prepare connection to the filer."""
            con = self.__get_connection()
            con.putrequest('POST', self._settings['url'])
            con.putheader('Content-Length', len(content))
            con.putheader('Content-type', 'text/xml; charset="UTF-8"')

            if self._settings['style'] == constants.LOGIN:
                login = '%(user)s:%(password)s' % self._settings
                if sys.version_info >= (3, 0):
                    encoded = base64.encodestring(login.encode())
                    encoded = encoded.decode().strip()
                else:
                    encoded = base64.encodestring(login)[:-1]
                con.putheader('Authorization', 'Basic %s' % encoded)
            elif self._settings['style'] == constants.CERTIFICATE and \
                    self._settings['verify_cn']:
                if not con.verify_certificate():
                    raise errors.CertificateError()

            return con

        connection = prepare_connection()

        try:
            connection.endheaders()
        except ssl.SSLError:
            self._settings['transport_type'] = constants.HTTP
            connection = prepare_connection()
            connection.endheaders()

        connection.send(content)

        try:
            response = connection.getresponse()
        except Exception:
            exc = sys.exc_info()[1]
            raise errors.APIFailure(-1, str(exc))

        if response.status != 200:
            if response.status in na_http.RESPONSES:
                raise errors.APIFailure(13002, 'HTTP result status %s' %
                                        response.status)
            else:
                raise errors.APIFailure(13002, 'HTTP result status %s "%s"' %
                                        (response.status,
                                         na_http.RESPONSES[response.status]))

        dom = xml.dom.minidom.parseString(
            response.read().decode('latin1').encode('utf-8')
        )

        connection.close()

        self._log.debug('XML response: %s', dom.toprettyxml())

        return self.__parse_dom(dom, fields)

    def __get_xml_content(self, api_command_name, arguments):
        """Create a XML query document for `api_command_name` and pass
        `arguments`.

        :param arguments: A list of :class:`schtob.pyontapi.NaArgument`
                          instances. Each instance contains the argument value
                          and the information how to generate the corresponding
                          XML structure.
        """
        doc = xml.dom.minidom.Document()
        netapp = doc.createElement('netapp')

        if self._settings['vfiler']:
            netapp.setAttribute('vfiler', self._settings['vfiler'])
        netapp.setAttribute('version', self._settings['ontapi_version'])
        doc.appendChild(netapp)

        api_element = doc.createElement(api_command_name)
        netapp.appendChild(api_element)

        for arg in arguments:
            arg.append_to_doc(doc, api_element)
        return doc

    def __parse_dom(self, dom, fields):
        """Parse XML response `dom` using `fields`.

        :param fields: list of :class:`schtob.pyontap.api.NaField` instances.
        """
        results = dom.getElementsByTagName("results")[0]

        status = results.getAttribute('status')

        if status != 'passed':
            errno = results.getAttribute('errno')
            reason = results.getAttribute('reason')
            raise errors.APIFailure(errno, reason)

        self._log.debug(results.toprettyxml())

        value = {}
        for field in fields:
            value[field.name] = field.get_value(results)
        return value

    def __get_connection(self):
        """Returns a HTTP/HTTPS connection instance to the filer."""
        if self._settings['style'] == constants.CERTIFICATE:
            return na_http.HTTPSCaConnection(self._filer,
                                             self._settings['port'],
                                             self._settings['cert_file'],
                                             self._settings['ca_file'],
                                             self._settings['cert_required'])

        conn_cls = na_http.HTTPConnection
        if self._settings['transport_type'] == constants.HTTPS:
            conn_cls = na_http.HTTPSConnection

        return conn_cls(self._filer, self._settings['port'])

    def __get_ontapi_version(self):
        """Invokes API call `system-get-ontapi-version` to get the ONTAPI
        version.
        """
        system_api = system.System(self)
        return system_api.get_ontapi_version()

    # ---------------------------PRIVATE METHODS-------------------------------

    def __handle_servertype(self):
        """Set url and port according to :attr:`settings['server_type']`."""
        if self._settings['port'] is None:
            if self._settings['transport_type'] == constants.HTTPS:
                if self._settings['server_type'] == 'DFM':
                    self._settings['port'] = 8488
                else:
                    self._settings['port'] = 443
            else:
                self._settings['port'] = \
                    constants.PORTS[self._settings['server_type']]
        self._settings['url'] = constants.URLS[self._settings['server_type']]

    def __test_https(self):
        """Test if a HTTPS connection is possible for this filer."""
        server_socket = socket.socket()
        server_socket.settimeout(0.25)

        try:
            server_socket.connect((self._filer, 443))
            server_socket.close()
            self._log.debug('HTTPS test was successful')
            self._settings['transport_type'] = constants.HTTPS
        except socket.error:
            if self._settings['transport_type'] == constants.HTTPS:
                msg = "Fall back to HTTP for filer <%s>; HTTPS was specified!"
                self._log.warning(msg, self._filer)
                self._settings['transport_type'] = constants.HTTP

    def __test_settings(self, settings):
        """Check the settings for plausibility."""
        test_dict = {
            'style': constants.STYLES,
            'server_type': constants.SERVER_TYPES,
            'transport_type': constants.TRANSPORT_TYPES,
        }

        for key, value_list in test_dict.items():
            # Test if kwargs values are valid
            if key in settings and settings[key] not in value_list:
                msg = "%s is not a valid value for %s" % (settings[key], key)
                self._log.error(msg)
                raise ValueError(msg)