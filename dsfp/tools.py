# -*- coding: utf-8 -*
from StringIO import StringIO
from .exceptions import ImproperlyConfigured


class BinDiff(object):
    """ Binary difference class """

    def __init__(self, stream_a, stream_b, skip_table=[], start_offset=0x0,
                 end_offset=None):
        self.skip_table = skip_table
        self.stream_a = self.patch_table(
            StringIO(stream_a)
            if isinstance(stream_a, basestring)
            else stream_a
        )
        self.stream_b = self.patch_table(
            StringIO(stream_b)
            if isinstance(stream_b, basestring)
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
        diff = map(lambda x, y: x is y, item_a, item_b)

        difference = {
            'offset': offset,
            'diff': []
        }
        for idx, item in enumerate(diff):
            if not item:
                difference['diff'].append(idx)
        return difference

    def patch_table(self, stream, offset=0x0):
        """replace data in stream with \x00 sequence according to
        skip table records for diff issues

        :param stream: file or cStringIO compatible object with seek, write
            methods
        :keyword int offset: fixed offset in the stream
        :return: stream
        :rtype: stream
        """

        if self.skip_table:
            for item in self.skip_table:
                stream.seek(item['offset'] + offset)
                stream.write('\x00' * item['size'])
        return stream

    def process_diff(self, start_offset=0x0, alignment=0x4):
        """ process difference between old and new stream

        :param int start_offset: start offset reading file
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
        return filter(lambda x: x['diff'], indexes)