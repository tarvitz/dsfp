# coding: utf-8
""" DSFP watch for some routines

.. module:: dsfp.watch
    :platform: Linux, Windows, MacOS X
    :synopsis: utils for routines
.. moduleauthor:: Tarvitz<tarvitz@blacklibrary.ru>
"""
import collections
from itertools import islice

from ctypes import Structure, c_uint32, c_ulong, Union

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
        >>> get_structure_fmt(SomeStructure)
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


def chunks(data, size=20000):
    """
    chunk/slice dictionary for small instances

    :param data: dict to be sliced
    :type data: list | dict | collections.Iterable
    :param int size: maximum items size for chunk
    :rtype: generator
    :return: list of smaller dictionaries

    >>> data = {1: 1, 2: 2, 3: 3, 4:4, 5:5, 6:7, 7:6, 8:9, 9:0, 0:9}
    >>> list(chunks(data, size=2))
    [{0: 9, 1: 1}, {2: 2, 3: 3}, {4: 4, 5: 5}, {6: 7, 7: 6}, {8: 9, 9: 0}]
    >>> data = range(10)
    >>> list(chunks(data, size=5))
    [[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]
    """
    it = iter(data)
    if isinstance(data, dict):
        for i in range(0, len(data), size):
            yield {k: data[k] for k in islice(it, size)}
    elif isinstance(data, (tuple, list, )):
        for i in range(0, len(data), size):
            yield [k for k in islice(it, size)]
    elif isinstance(data, (collections.Iterable, )):
        chunk = []
        while 1:
            try:
                chunk.append(next(it))
            except StopIteration:
                if chunk:
                    yield chunk
                break
            if len(chunk) == size:
                yield chunk
                chunk = []
    else:
        raise TypeError("use dict or list/tuple instances to chunk")
