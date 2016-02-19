# -*- coding: utf-8 -*-
"""
    schtob.pyontapi.py_gen
    ~~~~~~~~~~~~~~~~~~~~~~

    Generate API commands for all commands available on the storage system.

    :copyright: 2010-2015 Schaefer & Tobies SuC GmbH.
    :author: Markus Grimm <mgr@schaefer-tobies.de>;
             Uwe W. Schaefer <uws@schaefer-tobies.de>
    :license: LGPL, see LICENSE for details.
"""

import sys

from schtob.pyontapi import errors, api, system

_verbose = False


def generate(filer):
    """Generate API commands for `filer`'s version."""

    package = system.System(filer)
    typedefs = gen_typedefs(package)
    if _verbose:
        print("generate: Filer settings: <%s>" % filer.settings)
    if 'cmd_list' in filer.settings:
        return get_api_command_packages(package, typedefs,
                                        cmd_list=filer.settings['cmd_list'])
    else:
        return get_api_command_packages(package, typedefs)


def gen_typedefs(package):
    """Generate typedef classes."""
    typedefs = {}
    try:
        result = package.get_api_list_types()
    except errors.APIFailure:
        exc = sys.exc_info()[1]
        raise errors.APIGenerationError(exc.errno,
                                        'cannot get api types! Error was:\n%s' %
                                        exc.reason)

    for element in result['type-entries']:
        typedefs[element['name']] = api.NamedType(
            element['name'], element['type-elements']
        )

    for typedef in typedefs.values():
        elements = []
        for element in typedef.elements:
            if element['type'] is None:
                element['type'] = 'string'
            var_type = element['type'].replace('[]', '')
            if var_type in api.GENERIC_TYPEDEFS:
                var_type = api.GENERIC_TYPEDEFS[var_type]
            else:
                var_type = typedefs[var_type]
            _element = api.TypeDef(element, var_type)
            elements.append(_element)
        typedef.elements = elements
    return typedefs


def get_api_command_packages(package, typedefs, cmd_list=None):
    """Get all api commands for `filer`. Returns a dict containing all
    packages.
    If cmd_list is given, we do not ask for all commands;
    only for the given commands in the cmd_list
    """

    if not cmd_list:
        try:
            result = package.api_list()
        except errors.APIFailure:
            exc = sys.exc_info()[1]
            raise errors.OntapiVersionError(
                exc.errno, 'Can not run system-api-list. Error was:\n%s' %
                exc.reason)
        cmd_list = [child['name'] for child in result['apis']]
    elif _verbose:
        print("get_api_command_packages: cmd_list given\n", cmd_list)

    try:
        result = package.api_get_elements(cmd_list)
    except errors.APIFailure:
        exc = sys.exc_info()[1]
        raise errors.OntapiVersionError(
            exc.errno, 'Can not get api elements. Error was:\n%s' % exc.reason)

    packages = {}

    for child in result['api-entries']:
        name = child['name']
        elements = []
        if 'api-elements' in child:
            for element_info in child['api-elements']:
                info = {}
                for key, value in element_info.items():
                    info[key] = value
                var_type = info['type'].replace('[]', '')
                if var_type in api.GENERIC_TYPEDEFS:
                    var_type = api.GENERIC_TYPEDEFS[var_type]
                else:
                    var_type = typedefs[var_type].duplicate()
                typedef = api.TypeDef(info, var_type)
                if isinstance(var_type, api.NamedType):
                    var_type.set_output_value_for_childs(
                        typedef.is_optional
                    )
                elements.append(typedef)
        api_command = api.APICommand(name, elements)
        if not api_command.get_package() in packages:
            packages[api_command.get_package()] = []
        packages[api_command.get_package()].append(api_command)
    return packages