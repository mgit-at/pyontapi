# -*- coding: utf-8 -*-
"""
    schtob.pyontapi.errors
    ~~~~~~~~~~~~~~~~~~~~~~

    Pyontapi Exception classes.

    :copyright: 2010-2015 Schaefer & Tobies SuC GmbH.
    :author: Markus Grimm <mgr@schaefer-tobies.de>;
             Uwe W. Schaefer <uws@schaefer-tobies.de>
    :license: LGPL, see LICENSE for details.
"""

from schtob.pyontapi.na_errno import NA_ERRNO


class PyontapiError(Exception):
    """Base class for Pyontapi Exceptions."""
    pass


class APIFailure(PyontapiError):
    """Exception class for unsuccessful ONTAPI calls."""

    def __init__(self, errno, reason):
        PyontapiError.__init__(self)
        self.errno = errno
        self.reason = reason
        self.errname = ""
        if self.errno in NA_ERRNO:
            self.errname = NA_ERRNO[self.errno]

    def get_error(self):
        """Returns an error message."""
        if self.errno > -1:
            return '%(reason)s (Err Nr. %(errno)s - %(errname)s)' % {
                'errname': self.errname,
                'reason': self.reason,
                'errno': self.errno,
            }
        return self.reason

    def get_errno(self):
        """Returns the error number."""
        return self.errno

    def __str__(self):
        return self.get_error()


class UnknownOntapiVersionError(APIFailure):
    """Cannot get ONTAPI version."""
    pass


class OntapiVersionError(APIFailure):
    """Cannot get informations to API commands and type elements."""
    pass


class APIGenerationError(APIFailure):
    """API generation was not successful."""
    pass


class UnknownCommandError(APIFailure):
    """No such api command exception."""
    pass


class CertificateError(PyontapiError):
    """Server certificate verification failed."""
