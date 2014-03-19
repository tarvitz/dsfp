""" DSFP utils for some routines

.. module:: dsfp.exceptions
    :platform: Linux, Windows, MacOS X
    :synopsis: general exceptions for inner routines
.. moduleauthor:: Tarvitz<tarvitz@blacklibrary.ru>
"""

class FileTypeException(Exception):
    """ not a DarkSouls save file exception """
    def __init__(self, *args):
        self.args = args
