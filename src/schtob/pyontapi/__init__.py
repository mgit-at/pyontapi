# -*- coding: utf-8 -*-
"""
    schtob.pyontapi
    ~~~~~~~~~~~~~~~

    Python NetApp ONTAPI Implementation.

    :copyright: 2010-2015 Schaefer & Tobies SuC GmbH.
    :author: Markus Grimm <mgr@schaefer-tobies.de>;
             Uwe W. Schaefer <uws@schaefer-tobies.de>
    :license: LGPL, see LICENSE for details.
"""

VERSION = '0.3.2'

from schtob.pyontapi.na_connection import Filers
from schtob.pyontapi.na_filer import NaFiler

__all__ = ('NaFiler', 'Filers')
