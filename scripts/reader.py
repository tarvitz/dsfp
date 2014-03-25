#!/usr/bin/env python
# coding: utf-8
import argparse
import sys
from dsfp import DSSaveFileParser
DEBUG = True


def main(ns):
    filename = ns.filename[0]
    slot = ns.slot

    ds = DSSaveFileParser(filename)
    for slot in ds.get_stats():
        print("Name: %(name)s, deaths: %(deaths)s" % slot)
        if DEBUG:
            print(slot)
            for key, value in slot.items():
                if key.startswith('smth'):
                    print("%s: %s" % (key, value))
    items = ds.get_items(1)
    for item in items:
        print("name: %(name)s, %(type)s:%(amount)s" % {
            'name': item['name'],
            'type': item['data'].type,
            'amount': item['data'].amount
        })


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Prints slot data in dict format.'
    )
    parser.add_argument('-f', '--filename', metavar='draks0005.sl2',
                        type=str, nargs=1,
                        help='save file', required=True)
    parser.add_argument('-s', '--slot', metavar='N', type=int, nargs=1,
                        default=1,
                        help='character slot')
    args = parser.parse_args(sys.argv[1:])

    main(args)
