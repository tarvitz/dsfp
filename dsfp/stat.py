#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import struct

CLASSES = {
    0: 'Warrior',
    1: 'Knight',
    2: 'Wanderer',
    3: 'Thief',
    4: 'Bandit',
    5: 'Hunter',
    6: 'Sorcerer',
    7: 'Pyromancer',
    8: 'Cleric',
    9: 'Deprived'
}


BLOCK_INDEX = 0x2c0
BLOCK_SIZE = 0x60190
DEBUG = True

# time stored as seconds with unsigned int
# time: 0x3c12c0 (1 slot)
# time: 0x3c1430 (2 slot) (0x170 offset between game times)
TIME_INDEX = 0x3c12c0
TIME_BLOCK_SIZE = 0x170


data_map = [
    {'offset': 0x70, 'type': 'i', 'field': 'hp', 'size': 4},
    {'offset': 0x6c, 'type': 'i', 'field': 'hp_current', 'size': 4},
    {'offset': 0x70, 'type': 'i', 'field': 'hp', 'size': 4},
    # what's the difference?
    {'offset': 0x74, 'type': 'i', 'field': 'hp2', 'size': 4},
    # unrevealed
    {'offset': 0x78, 'type': 'i', 'field': '0x78', 'size': 4},
    #{'offset': 0x7c, 'type': 'i', 'field': '0x7c', 'size': 4},  # same as 0x78
    #{'offset': 0x80, 'type': 'i', 'field': '0x80', 'size': 4},  # same as 0x78
    #
    # 4 bytes space between chars stats
    {'offset': 0x88, 'type': 'i', 'field': 'stamina', 'size': 4},
    {'offset': 0x8c, 'type': 'i', 'field': 'stamina2', 'size': 4},
    {'offset': 0x90, 'type': 'i', 'field': 'stamina3', 'size': 4},
    {'offset': 0x98, 'type': 'i', 'field': 'vitality', 'size': 4},
    {'offset': 0xa0, 'type': 'i', 'field': 'attunement', 'size': 4},
    {'offset': 0xa8, 'type': 'i', 'field': 'endurance', 'size': 4},
    {'offset': 0xb0, 'type': 'i', 'field': 'strength', 'size': 4},
    {'offset': 0xb8, 'type': 'i', 'field': 'dexterity', 'size': 4},
    {'offset': 0xc0, 'type': 'i', 'field': 'intelligence', 'size': 4},
    {'offset': 0xc8, 'type': 'i', 'field': 'faith', 'size': 4},
    {'offset': 0xd0, 'type': 'i', 'field': '0xd4', 'size': 4},
    {'offset': 0xd8, 'type': 'i', 'field': 'humanity', 'size': 4},
    {'offset': 0xe0, 'type': 'i', 'field': 'resistance', 'size': 4},
    {'offset': 0xe8, 'type': 'i', 'field': 'level', 'size': 4},
    {'offset': 0xec, 'type': 'i', 'field': 'souls', 'size': 4},
    # could be exp
    {'offset': 0xf0, 'type': 'i', 'field': 'earned', 'size': 4},
    # 28 bytes, 2*13 + finishing zero for char name

    {'offset': 0x100, 'type': 'c', 'field': 'name', 'size': 32},
    {'offset': 0x122, 'type': '?', 'field': 'male', 'size': 1},
    # enums
    {'offset': 0x126, 'type': 'B', 'field': 'class', 'size': 1},
    {'offset': 0x127, 'type': 'B', 'field': 'body', 'size': 1},
    {'offset': 0x128, 'type': 'B', 'field': 'gift', 'size': 1},
    {'offset': 0x16c, 'type': 'B', 'field': 'face', 'size': 1},
    {'offset': 0x16d, 'type': 'B', 'field': 'hairs', 'size': 1},
    {'offset': 0x16e, 'type': 'B', 'field': 'color', 'size': 1},
    {'offset': 0x1f128, 'type': 'i', 'field': 'deaths', 'size': 4},
]


class FileTypeException(Exception):
    def __init__(self, *args):
        self.args = args


class DSSaveFileParser(object):
    """ Dark Souls save file parser
    original gist: https://gist.github.com/infuasto/8382836
    """
    def __init__(self, filename):
        self.filename = filename
        self._fo = open(self.filename, 'rb')
        # check if it's a dark souls save file
        self._fo.seek(0)
        fmt = self._fo.read(4)
        self._fo.seek(0x18)
        version = self._fo.read(8)
        self._fo.seek(0)
        if fmt != 'BND4' and version != '000000001':
            raise FileTypeException("Not an Dark Souls save file")
        self.slots = []

    def get_data(self, reload=False):
        if self.slots and not reload:
            return self.slots

        fo = self._fo
        fo.seek(BLOCK_INDEX, 0)
        slots = []

        for slot in range(0, 10):
            _offset = BLOCK_INDEX + BLOCK_SIZE * slot
            _time_offset = TIME_INDEX + TIME_BLOCK_SIZE * slot
            fo.seek(_offset, 0)
            storage = {}
            for item in data_map:
                fo.seek(_offset + item['offset'], 0)
                data = fo.read(item['size'])
                if item['type'] == 'c':
                    encoded = data.decode('utf-16').split('\00')[0]
                elif item['type'] == 'i':
                    encoded = struct.unpack(item['type'], data)[0]
                else:
                    encoded = struct.unpack(item['type'], data)[0]
                storage.update({item['field']: encoded})
            # process time
            fo.seek(_time_offset, 0)
            storage.update({
                'time': struct.unpack('i', fo.read(4))[0]
            })
            slots.append(storage)
        self.slots = slots
        return self.slots

    def get_death_stats(self):
        """ returns dict for death chars stat, the old one """
        stats = []

        self._fo.seek(0x2c0, 0)
        for slot in range(0, 10):
            self._fo.seek(0x100, 1)
            name = self._fo.read(32)
            if name[0] != '\00':
                self._fo.seek(-0x120, 1)
                self._fo.seek(0x1f128, 1)
                deaths = self._fo.read(4)
                self._fo.seek(-0x04, 1)
                self._fo.seek(-0x1f128, 1)
                stats.append({
                    'name': name.decode('utf-16').split('\00')[0],
                    'deaths': struct.unpack('i', deaths)[0]
                })
            else:
                self._fo.seek(-0x120, 1)
            self._fo.seek(0x60190, 1)
        return stats


def usage():
    print("%s <filename.sl2>" % sys.argv[0])
    sys.exit(0)


def main():
    filename = sys.argv[1]
    ds = DSSaveFileParser(filename)
    for slot in ds.get_data():
        if slot['name']:
            print("Name: %(name)s, deaths: %(deaths)s" % slot)
            if DEBUG:
                print(slot)


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        usage()
    main()
