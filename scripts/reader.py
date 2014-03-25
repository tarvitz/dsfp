#!/usr/bin/env python
# coding: utf-8
import argparse
import sys
from dsfp import DSSaveFileParser
import simplejson as json

DEBUG = True


def main(ns):
    filename = ns.filename[0]
    slot = ns.slot
    table = []
    if ns.table:
        table = json.loads(ns.table[0].read())

    ds = DSSaveFileParser(filename)
    for slot in ds.get_stats():
        print("Name: %(name)s, deaths: %(deaths)s" % slot)
        if table:
            for item in table:
                print('%s: %s' % (item, slot[item]))
        else:
            for key, value in slot.items():
                print('%s: %s' % (key, value))
    #items = ds.get_items(slot=slot)
    #for item in items:
    #    print("name: %(name)s, %(type)s:%(amount)s" % {
    #        'name': item['name'],
    #        'type': item['data'].type,
    #        'amount': item['data'].amount
    #    })


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Prints slot data in dict format.'
    )
    parser.add_argument('-f', '--filename', metavar='draks0005.sl2',
                        type=str, nargs=1,
                        help='save file', required=True)
    parser.add_argument('-s', '--slot', metavar='N', type=int, nargs=1,
                        default=0,
                        help='character slot')
    parser.add_argument('-T', '--table', metavar='table.json', type=file,
                        nargs=1,
                        help='json table with slot stats filter params')
    args = parser.parse_args(sys.argv[1:])

    main(args)
