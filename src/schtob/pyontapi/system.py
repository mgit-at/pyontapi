# -*- coding: utf-8 -*-
"""
    schtob.pyontapi.system
    ~~~~~~~~~~~~~~~~~~~~~~

    System API.

    :copyright: 2010-2015 Schaefer & Tobies SuC GmbH.
    :author: Markus Grimm <mgr@schaefer-tobies.de>;
             Uwe W. Schaefer <uws@schaefer-tobies.de>
    :license: LGPL, see LICENSE for details.
"""

from schtob.pyontapi.api import BaseAPI, NaArgument, NaField
from schtob.pyontapi.api import NaNamedType, NaTypeElement

_verbose = False


class System(BaseAPI):
    """System API class for base system calls."""

    def get_ontapi_version(self):
        """Invoke `system-get-ontapi-version`."""
        if _verbose:
            print("get_ontapi_version")
        fields = (
            NaField({'name': 'major-version', 'type': int}),
            NaField({'name': 'minor-version', 'type': int}),
        )
        return self._filer.do_api_call('system-get-ontapi-version', (),
                                       fields)

    def api_get_elements(self, api_list):
        """Invoke `system-api-get-elements`."""
        if _verbose:
            print("api_get_elements: api_list", api_list)
        args = (
            NaArgument(api_list, {
                'name': 'api-list',
                'type': NaNamedType('api-list-info', [
                    NaTypeElement({'name': '', 'type': str})]),
                'is-array': True,
            }),
        )
        fields = (
            NaField({
                'name': 'api-entries',
                'is-array': True,
                'type': NaNamedType('system-api-entry-info', [
                    NaTypeElement({'name': 'name', 'type': str}),
                    NaTypeElement({
                        'name': 'api-elements',
                        'is-array': True,
                        'type': NaNamedType('system-api-element-info', [
                            NaTypeElement({
                                'name': 'encrypted',
                                'type': str,
                                'is-optional': True,
                            }), NaTypeElement({
                                'name': 'is-nonempty',
                                'type': bool,
                                'is-optional': True,
                            }), NaTypeElement({
                                'name': 'is-optional',
                                'type': bool,
                                'is-optional': True,
                            }), NaTypeElement({
                                'name': 'is-output',
                                'type': bool,
                                'is-optional': True,
                            }), NaTypeElement({
                                'name': 'is-validated',
                                'type': bool,
                                'is-optional': True,
                            }), NaTypeElement({
                                'name': 'name',
                                'type': str,
                            }), NaTypeElement({
                                'name': 'type',
                                'type': str,
                            }),
                        ])})
                ])}),
        )
        return self._filer.do_api_call('system-api-get-elements', args,
                                       fields)

    def api_list(self):
        """Invoke `system-api-list`."""
        if _verbose:
            print("api_list")
        fields = (
            NaField({
                'name': 'apis', 'is-array': True,
                'type': NaNamedType('system-api-info', [
                    NaTypeElement({
                        'name': 'is-streaming',
                        'type': bool,
                        'is-optional': True,
                    }),
                    NaTypeElement({
                        'name': 'license',
                        'type': str,
                        'is-optional': True,
                    }),
                    NaTypeElement({
                        'name': 'name',
                        'type': str,
                    }),
                ]),
            }),
        )
        if _verbose:
            api_list_info = self._filer.do_api_call('system-api-list', (),
                                                    fields)
            print("api_list: api_list_info", api_list_info)
            for info in api_list_info['apis']:
                print("function: %s" % info['name'])

            return api_list_info
        else:
            return self._filer.do_api_call('system-api-list', (), fields)

    def get_api_list_types(self):
        """Invoke `system-api-list-types`."""
        if _verbose:
            print("get_api_list_types")
        fields = (
            NaField({
                'name': 'type-entries',
                'is-array': True,
                'type': NaNamedType('system-api-type-entry-info', [
                    NaTypeElement({'name': 'name', 'type': str}),
                    NaTypeElement({
                        'name': 'type-elements',
                        'is-array': True,
                        'type': NaNamedType(
                            'system-api-element-info', [
                                NaTypeElement({
                                    'name': 'encrypted',
                                    'type': str,
                                    'is-optional': True,
                                }), NaTypeElement({
                                    'name': 'is-nonempty',
                                    'type': bool,
                                    'is-optional': True,
                                }), NaTypeElement({
                                    'name': 'is-optional',
                                    'type': bool,
                                    'is-optional': True,
                                }), NaTypeElement({
                                    'name': 'is-output',
                                    'type': bool,
                                    'is-optional': True,
                                }), NaTypeElement({
                                    'name': 'is-validated',
                                    'type': bool,
                                    'is-optional': True,
                                }), NaTypeElement({
                                    'name': 'name',
                                    'type': str,
                                }), NaTypeElement({
                                    'name': 'type',
                                    'type': str,
                                }),
                            ])}),
                ])}),
        )
        if _verbose:
            api_types = self._filer.do_api_call('system-api-list-types', (),
                                                fields)
            print("get_api_list_types: api_types", api_types.keys())
            for t in api_types:
                for n in api_types[t]:
                    print(n)
            return api_types
        else:
            return self._filer.do_api_call('system-api-list-types', (), fields)
