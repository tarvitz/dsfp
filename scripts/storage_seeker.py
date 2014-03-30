# -*- coding: utf-8 -*
""" Dark Souls save file analyze tools

.. module:: watcher
    :platform: Linux, Windows, MacOS X
    :synopsis: seeks for the end and the begin dark souls item storage
    inside of save file with given character slots param
.. moduleauthor:: Tarvitz<tarvitz@blacklibrary.ru>
"""
import six
import os
import sys
import argparse
import struct


PROJECT_ROOT = os.path.pardir

rel = lambda path: os.path.join(PROJECT_ROOT, path)
sys.path.insert(0, rel('dsfp'))
from dsfp import DSSaveFileParser
from dsfp.dsfp import ItemStructure


def main(ns):
    start = int(ns.start_offset or '0xb84', 16)
    formation = ns.formation or 'forward'
    slot = ns.slot[0] - 1
    ds = DSSaveFileParser(filename=ns.filename[0])
    block = six.BytesIO(ds.read_slot_data(slot=slot))
    ds.close()
    block.seek(start)
    # validate item storage process
    offset = start

    while 1:
        block.seek(offset)
        block_size = 4 * 7
        encoded = struct.unpack('I' * 7, block.read(block_size))
        item = ItemStructure(*encoded)
        print(
            "0x%08x: store: 0x%08x, type: %d, amount: %d, (%d) "
            "have: %d, durability: %d:%d" % ((offset, ) + encoded)
        )
        if (item.stored in (0xffffffff, 0x00000000, 0x10000000, 0x20000000,
                            0x30000000, 0x40000000)
                and item.type != 0):
            if formation == 'backward':
                offset -= block_size
            else:
                offset += block_size
        else:
            break
    print("offset discovered: 0x%08x" % offset)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description=(
            'Searches data blocks with item storage '
            'inside dark souls save file for darksouls save file.')
    )
    parser.add_argument('-f', '--filename', metavar='draks0005.sl2',
                        type=str, nargs=1,
                        help='save file', required=True)
    parser.add_argument('-s', '--slot', metavar='N', type=int, nargs=1,
                        default=1, required=True,
                        help='character slot')
    parser.add_argument('-B', '--start-offset',
                        type=str, required=False,
                        help='start offset for inspections')
    parser.add_argument('-F', '--formation',
                        choices=['forward', 'backward'],
                        default='forward', required=False)

    arguments = parser.parse_args(sys.argv[1:])
    main(arguments)
