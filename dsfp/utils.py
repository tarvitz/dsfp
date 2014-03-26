# coding: utf-8
""" DSFP utils for some routines

.. module:: dsfp.utils
    :platform: Linux, Windows, MacOS X
    :synopsis: utils for routines
.. moduleauthor:: Tarvitz<tarvitz@blacklibrary.ru>
"""

from ctypes import *

__all__ = ['get_structure_fmt', ]


def get_structure_fmt(structure_class):
    """get structure format for further struct extraction

    :param structure_class: ``ctypes`` ``Structure`` instances
    :return: tuple of (``format_string``, ``block_size``)

    .. code-block:: python

        >>> class SomeStructure(Structure):
            _fields_ = [
                ('data', c_ulong), # 8 bytes
                ('amount', c_uint32) # 4 bytes
            ]
        >>> get_format_fmt(SomeStructure)
        ('QI', 12)
    """
    fmt = ''
    block_size = 0

    # if not isinstance(structure_class, Structure):
    #     raise TypeError("not a `ctype` ``Structure`` class based")

    for _type in structure_class._fields_:
        if _type[1] == c_uint32:
            fmt += 'I'
            block_size += 4
        elif _type[1] == c_ulong:
            fmt += 'Q'
            block_size += 8
        elif issubclass(_type[1], (Union, Structure)):
            pass
        else:
            fmt += 'I'
            block_size += 4
    return fmt, block_size
