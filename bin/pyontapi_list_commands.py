#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    pyontapi_list_commands
    ~~~~~~~~~~~~~~~~~~~~~~

    Command-Line tool for listing API commands for filer.

    :copyright: 2010-2012 Schaefer & Tobies SuC GmbH.
    :author: Markus Grimm <mgr@schaefer-tobies.de>
    :license: LGPL, see LICENSE for details.
"""

import os
import sys
import logging
logging.basicConfig()


def main(args):
    """List packages and commands.

    :param args Commandline arguments minus program name

    Example:
    ./pyontapi_list_commands.py FILER-HOSTNAME USER port=80 vfiler=VFILER-NAME
    """
    pw = os.environ.get('PW')

    filer_name = args[0]
    user = args[1]

    cfg = {"user": user}
    cfg.update([ i.split('=',1) for i in args[2:]])
    if pw == None:
        cfg.pop("password") # password should NEVER be on the commandline as it can be seen system wide!
    else:
        cfg["password"] = pw

    print('listing packages on "%s" using role "%s" with password:%s' % (filer_name, user, pw != None))

    try:
        filer = NaFiler(filer_name, cfg)
        result = filer.call('system-api-list')
    except errors.APIFailure, exc:
        print(exc)
        sys.exit(1)
    packages = {}
    commands = []
    for api in result['apis']:
        package = api['name'].split('-')[0]
        commands.append(api['name'])
        if not package in packages:
            packages[package] = []
            print(' - ' + package)
        packages[package].append(api['name'])

    while True:
        entry = raw_input('Enter package or command (leave empty to exit): ')
        if not entry:
            break
        elif entry not in packages and entry not in commands:
            print('no such package or command...')
        elif entry in commands:
            print_command(filer, entry)
        else:
            for api in packages[entry]:
                print(api)


def print_command(filer, command):
    """Print input and output fields for command `command`."""
    result = filer.call('system-api-get-elements', api_list=[command])
    output = []
    print('Input fields:')
    for entry in result['api-entries'][0]['api-elements']:
        if entry.get('is-output', False):
            output.append(entry)
        else:
            print(' - %s:%s optional:%s' % (
                entry['name'], entry['type'],
                entry.get('is-optional', False) is True
            ))
    if output:
        print('Output fields:')
        for entry in output:
            print(' - %s:%s' % (entry['name'], entry['type']))


def setup_path():
    """Try to add the pyontapi base dir to `sys.path`."""
    basedir = os.path.join(os.path.dirname(__file__), os.pardir, 'src')
    try:
        __import__('schtob.pyontapi')
    except ImportError:
        sys.path.append(basedir)


if __name__ == '__main__':
    setup_path()
    from schtob.pyontapi import NaFiler, errors

    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        print('')
    except EOFError:
        print('')
