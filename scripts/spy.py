# -*- coding: utf-8 -*
""" DSFP modifications spy, looks for save file modifications

.. module:: watcher
    :platform: Linux, Windows, MacOS X
    :synopsis: watches for dark souls save file modifications and prints
        any modified data in console
.. moduleauthor:: Tarvitz<tarvitz@blacklibrary.ru>
"""

from __future__ import unicode_literals
from time import sleep
from datetime import datetime
import struct
import sys
import os
import six
import textwrap

PROJECT_ROOT = os.path.pardir


def rel(path):
    return os.path.join(PROJECT_ROOT, path)

sys.path.insert(0, os.path.join(PROJECT_ROOT, 'dsfp'))

import simplejson as json
import argparse


class Node(object):
    def __init__(self):
        self.children = []

    def add(self, element):
        self.children.append(element)


class Leaf(Node):
    __slots__ = ['start', 'size']

    def __init__(self, start, size, old, new):
        super(Leaf, self).__init__()
        self.start = start
        self.size = size
        self.old = old
        self.new = new

    def add(self, element):
        """
        nothing to do as this is leaf
        :param element:
        :return: None
        """

    @staticmethod
    def unpack(value, fmt='I'):
        return struct.unpack(fmt, value)[0]

    def __str__(self):
        new = self.unpack(self.new)
        old = self.unpack(self.old)
        fmt = (
            "0x%(addr)08x[%(saddr)10s] %(value)10s 0x%(hex)08x "
            "%(follow)5s %(old)10s 0x%(old_hex)08x" % {
                'addr': self.start,
                'saddr': self.start,
                'value': new,
                'hex': new,
                'old': old,
                'old_hex': old,
                'follow': '<-'
            }
        )
        return fmt

    def __repr__(self):
        return "<Leaf: 0x%08x>" % self.start

class NewDiff(object):
    """

    """
    def __init__(self, new_stream, old_stream, watchers):
        self.new_stream = new_stream
        self.old_stream = old_stream
        self.watchers = watchers

    def read_stream(self, stream, block):
        """
        read stream withing given block

        :param stream: stream to read
        :type stream: six.BytesIO
        :param dict block: start offset, size to read
        :rtype: str
        :return: raw data
        """
        start = int(block['start'], 16)
        size = int(block['size'], 16)
        stream.seek(start)
        return stream.read(size)

    def process_diff(self, word_size=4):
        """
        processes diff

        :param int word_size: word size for diff processing
        :rtype: list[Leaf]
        :return: diffs
        """
        nodes = []
        for table in self.watchers:
            for block in table.get('WATCH', []):
                old_data = self.read_stream(self.old_stream, block)
                new_data = self.read_stream(self.new_stream, block)
                for idx, (old, new) in enumerate(
                        zip(textwrap.wrap(old_data, word_size),
                            textwrap.wrap(new_data, word_size))
                ):
                    size = int(block['size'], 16) + idx * word_size
                    start = int(block['start'], 16) + idx * word_size
                    if old == new:
                        continue
                    nodes.append(
                        Leaf(start, size, old, new)
                    )
        return nodes


class Spy(object):
    """ Changes spy

    :param str filename: path inspected filename
    :keyword int slot: character slot
    :keyword dict skip_table: skip some data which is represented in table
        stored in dict
    :keyword bool use_curses: use curses interface instead of standard cli
    :keyword int start_offset: start inspections with given offset
    :keyword int start_offset: end inspections with given offset
    """
    def __init__(self, filename, watchers=None):
        self.filename = filename
        self.watchers = watchers

    def read(self):
        fo = open(self.filename, 'rb')
        return six.BytesIO(fo.read())

    @staticmethod
    def log(out):
        """
        log into the main window
        :keyword bool refresh: True if should be refreshed
        """
        print(out)

    def run(self):
        modified = 0
        old_stat = os.lstat(self.filename)
        old_stream = self.read()

        while 1:
            sleep(1)
            stat = os.lstat(self.filename)
            if stat.st_mtime == old_stat.st_mtime:
                continue
            now = datetime.now()
            print("modified: %s [%s]" % (modified, now.strftime('%H:%M:%S')))
            old_stat = stat
            new_stream = self.read()
            diff = NewDiff(old_stream=old_stream,
                           new_stream=new_stream,
                           watchers=self.watchers)
            for node in diff.process_diff():
                print(node)
            modified += 1


def main(ns):
    filename = ns.filename
    watchers = []
    if ns.watch_table:
        for stream in ns.watch_table:
            watchers.append(json.loads(stream.read()))
    watcher = Spy(filename=filename, watchers=watchers)
    try:
        watcher.run()
    except KeyboardInterrupt:
        print("\nCatch Ctrl+C, exiting ..")
    finally:
        sys.exit(0)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Prints changes for darksouls save file.'
    )
    parser.add_argument('-f', '--filename', metavar='draks0005.sl2',
                        type=str, dest='filename',
                        help='save file', required=True)
    parser.add_argument('-w', '--watch-table',
                        dest='watch_table',
                        metavar='table.json,table2.json',
                        nargs='+',
                        type=argparse.FileType('r'),
                        help=(
                            'use data inside of json file for choosing what to'
                            ' diff check inside of block with given offsets'),
                        required=True)
    arguments = parser.parse_args(sys.argv[1:])
    main(arguments)
