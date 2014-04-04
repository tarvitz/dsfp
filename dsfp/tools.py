# -*- coding: utf-8 -*
""" DSFP tools

.. module:: dsfp.tools
    :platform: Linux, Windows, MacOS X
    :synopsis: general exceptions for inner routines
.. moduleauthor:: Tarvitz<tarvitz@blacklibrary.ru>
"""
import sys
import six


class BinDiff(object):
    """ Binary difference class """

    def __init__(self, stream_a, stream_b, skip_tables=None,
                 start_offset=0x0,
                 end_offset=None):
        self.skip_tables = skip_tables or []

        self.stream_a = self.patch_table(
            six.BytesIO(stream_a)
            if isinstance(stream_a, (six.string_types, six.binary_type))
            else stream_a
        )
        self.stream_b = self.patch_table(
            six.BytesIO(stream_b)
            if isinstance(stream_b, (six.string_types, six.binary_type))
            else stream_b
        )
        self.end_offset = end_offset
        self.start_offset = start_offset

    @staticmethod
    def index(item_a, item_b, offset=0x0):
        """ item_a item_b simple difference
        :param str item_a:
        :param str item_b:
        :return: dict of difference
        :rtype: dict
        """
        # 0 if items are equal to each other
        # other values mean items are not equal: [0, -1, 0, 5]
        if sys.version_info.major == 2:
            # pylint: disable=W0141
            # noinspection PyUnresolvedReferences
            diff = map(cmp, item_a, item_b)
        else:
            diff = map(lambda x, y: x != y, item_a, item_b)
        difference = {
            'offset': offset,
            'diff': []
        }
        for idx, item in enumerate(diff):
            if item:
                difference['diff'].append(idx)
        return difference

    def patch_table(self, stream, offset=0x0):
        """replace data in stream with \x00 sequence according to
        skip table records for diff issues

        :param stream: file or StringIO compatible object with seek, write
            methods
        :keyword int offset: fixed offset in the stream
        :return: stream
        :rtype: stream
        """

        if self.skip_tables:
            for tbl in self.skip_tables:
                for item in tbl['SKIP_TABLE']:
                #for item in self.skip_tables:
                    stream.seek(item['offset'] + offset)
                    stream.write(six.b('\x00' * item['size']))
        return stream

    def process_diff(self, alignment=0x4):
        """ process difference between old and new stream

        :keyword alignment: alignment read
        :return: modified stream with patched data
        :rtype: file stream
        """
        indexes = []
        offset = self.start_offset
        self.stream_a.seek(self.start_offset)
        self.stream_b.seek(self.start_offset)

        end_block = self.end_offset or self.start_offset - self.start_offset
        while 1:
            data = self.stream_a.read(alignment)
            new_data = self.stream_b.read(alignment)
            if not data:
                break

            indexes.append(self.index(data, new_data, offset=offset))
            offset += alignment

            if end_block:
                if offset >= end_block:
                    break
        return [item for item in indexes if item['diff']]
