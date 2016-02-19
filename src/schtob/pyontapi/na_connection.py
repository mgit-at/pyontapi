# -*- coding: utf-8 -*-
"""
    schtob.pyontapi.na_connection
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module is intended to be used for handling a bunch of
    :class:`schtob.pyontapi.NaFiler` objects in an environment where you have
    a single user, which is allowed to run API commands on all your filers.
    Instead of manually creating multiple :class:`NaFiler` objects, you can
    use the :class:`Filers` class which encapsulates all the required
    connection and authentication settings for each filer. The only thing you
    have to do is defining the `NA_CONFIG` dict in
    :mod:`schtob.pyontapi.settings`. See :ref:`configuration` for more details.

    :copyright: 2010-2015 Schaefer & Tobies SuC GmbH.
    :author: Markus Grimm <mgr@schaefer-tobies.de>;
             Uwe W. Schaefer <uws@schaefer-tobies.de>
    :license: LGPL, see LICENSE for details.
"""

import copy

from schtob.pyontapi.na_filer import NaFiler


class Filers(object):
    """Connections to multiple filers.

    Use it in a static way like this::

        >>> Filers('my-filer').volume.list_info()
    """

    __filers = {}
    __config = {}
    __unset = True

    def __new__(cls, name, role='default'):
        # you can access a connection by typing Filers(filername).foo
        # Connection is created with default params, defined in NA_CONFIG
        return cls.get_connection(name, role)

    def setup_config(cls, config):
        """Setup the configuration for all your Filers.

        .. versionadded:: 0.2.2
        """
        cls.__config = config
        cls.__unset = False

    setup_config = classmethod(setup_config)

    def get_connection(cls, name, role='default'):
        """Get connection to filer `name`.

        .. versionadded:: 0.2.2
            The role parameter was added.
        """
        if (name, role) not in cls.__filers:
            if cls.__unset:
                cls.__config = __import__(
                    'schtob.pyontapi.settings', {}, {}, ['NA_CONFIG']
                ).NA_CONFIG
                cls.__unset = False
            roles = copy.deepcopy(cls.__config['roles'])
            filer_roles = cls.__config.get('filer-roles', {})

            rolesettings = roles['default']

            if name in filer_roles and 'default' in filer_roles[name]:
                rolesettings.update(filer_roles[name]['default'])

            if role in roles:
                rolesettings.update(roles[role])

            if name in filer_roles and role in filer_roles[name]:
                rolesettings.update(filer_roles[name][role])

            return cls.create_connection(name, rolesettings, role)
        return cls.__filers[(name, role)]

    get_connection = classmethod(get_connection)

    def create_connection(cls, name, settings, role='default'):
        """Create a connection to filer `name` with `settings`.

        Use this to instantiate a "special" connection where settings differ
        from `NA_CONFIG` instead of just using Filers(name).

        .. versionadded:: 0.2.2
            The role parameter was added.
        """
        cls.__filers[(name, role)] = NaFiler(name, settings)
        return cls.__filers[(name, role)]

    create_connection = classmethod(create_connection)

    def drop_connection(cls, name, role='default'):
        """Drops connection to filer `name`."""
        if (name, role) in cls.__filers:
            cls.__filers.pop((name, role))

    drop_connection = classmethod(drop_connection)