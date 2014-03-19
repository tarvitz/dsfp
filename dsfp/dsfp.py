#!/usr/bin/env python
# -*- coding: utf-8 -*-
import bz2
from StringIO import StringIO
import sys
import struct
from ctypes import *
from .utils import *
from .exceptions import *

CLASSES = {
    0: 'Warrior', 1: 'Knight', 2: 'Wanderer', 3: 'Thief', 4: 'Bandit',
    5: 'Hunter', 6: 'Sorcerer', 7: 'Pyromancer', 8: 'Cleric', 9: 'Deprived'
}

BLOCK_SIZE = 0x60190
BLOCK_INDEX = 0x2c0
BLOCK_DATA_OFFSET = 0x14
SLOTS_AMOUNT_OFFSET = 0xC
SLOTS_METADATA_OFFSET = 0x40
DEBUG = True

# time stored as seconds with unsigned int
# time: 0x3c12c0 (1 slot)
# time: 0x3c1430 (2 slot) (0x170 offset between game times)
TIME_INDEX = 0x3c12c0
TIME_BLOCK_SIZE = 0x170


DATA_MAP = [
    #{'offset': 0x1f, 'type': 'I', 'field': '0x1f', 'size': 4},  # 393216 all
    #{'offset': 0x14, 'type': 'I', 'field': '0x14', 'size': 4}, # 57 all
    #{'offset': 0x18, 'type': 'I', 'field': '0x18', 'size': 4},
    #{'offset': 0x1c, 'type': 'I', 'field': '0x1c', 'size': 4},
    #{'offset': 0x20, 'type': 'I', 'field': '0x20', 'size': 4},  # 84 all
    #{'offset': 0x24, 'type': 'I', 'field': '0x24', 'size': 4},  # 127185 all
    #{'offset': 0x28, 'type': 'I', 'field': '0x28', 'size': 4},  # 84 all
    #{'offset': 0x2c, 'type': 'I', 'field': '0x2c', 'size': 4},  # 123888 all
    #{'offset': 0x30, 'type': 'I', 'field': '0x30', 'size': 4},  # 124186 all
    #{'offset': 0x34, 'type': 'I', 'field': '0x34', 'size': 4},  # 64 all
    #{'offset': 0x38, 'type': 'I', 'field': '0x38', 'size': 4},  # 124036 all
    #{'offset': 0x3c, 'type': 'I', 'field': '0x3c', 'size': 4},  # 142 all
    #{'offset': 0x40, 'type': 'I', 'field': '0x40', 'size': 4},  # 124178 all
    #{'offset': 0x44, 'type': 'I', 'field': '0x44', 'size': 4},  # 8 all
    #{'offset': 0x48, 'type': 'I', 'field': '0x48', 'size': 4},  # 127269 all
    #{'offset': 0x4c, 'type': 'I', 'field': '0x4c', 'size': 4},  # 93441 all
    #{'offset': 0x50, 'type': 'I', 'field': '0x50', 'size': 4},  # 220710 all
    {'offset': 0x54, 'type': 'I', 'field': '0x54', 'size': 4},
    {'offset': 0x58, 'type': 'I', 'field': '0x58', 'size': 4},
    {'offset': 0x5c, 'type': 'I', 'field': '0x5c', 'size': 4},
    {'offset': 0x60, 'type': 'I', 'field': '0x60', 'size': 4},
    #{'offset': 0x64, 'type': 'I', 'field': '0x64', 'size': 4},  # 131076 all
    {'offset': 0x6c, 'type': 'I', 'field': 'hp_current', 'size': 4},
    {'offset': 0x70, 'type': 'I', 'field': 'hp', 'size': 4},
    # what's the difference?
    {'offset': 0x74, 'type': 'I', 'field': 'hp2', 'size': 4},
    # unrevealed
    {'offset': 0x78, 'type': 'I', 'field': '0x78', 'size': 4},
    #{'offset': 0x7c, 'type': 'I', 'field': '0x7c', 'size': 4},  # same as 0x78
    #{'offset': 0x80, 'type': 'I', 'field': '0x80', 'size': 4},  # same as 0x78
    #
    # 4 bytes space between chars stats
    {'offset': 0x88, 'type': 'I', 'field': 'stamina', 'size': 4},
    {'offset': 0x8c, 'type': 'I', 'field': 'stamina2', 'size': 4},
    {'offset': 0x90, 'type': 'I', 'field': 'stamina3', 'size': 4},
    {'offset': 0x98, 'type': 'I', 'field': 'vitality', 'size': 4},
    {'offset': 0xa0, 'type': 'I', 'field': 'attunement', 'size': 4},
    {'offset': 0xa8, 'type': 'I', 'field': 'endurance', 'size': 4},
    {'offset': 0xb0, 'type': 'I', 'field': 'strength', 'size': 4},
    {'offset': 0xb8, 'type': 'I', 'field': 'dexterity', 'size': 4},
    {'offset': 0xc0, 'type': 'I', 'field': 'intelligence', 'size': 4},
    {'offset': 0xc8, 'type': 'I', 'field': 'faith', 'size': 4},
    {'offset': 0xd0, 'type': 'I', 'field': '0xd4', 'size': 4},
    {'offset': 0xd8, 'type': 'I', 'field': 'humanity', 'size': 4},
    {'offset': 0xe0, 'type': 'I', 'field': 'resistance', 'size': 4},
    {'offset': 0xe8, 'type': 'I', 'field': 'level', 'size': 4},
    {'offset': 0xec, 'type': 'I', 'field': 'souls', 'size': 4},
    # could be exp
    {'offset': 0xf0, 'type': 'I', 'field': 'earned', 'size': 4},
    # 28 bytes, 2*13 + finishing zero for char name

    {'offset': 0x100, 'type': 'c', 'field': 'name', 'size': 14*2},
    {'offset': 0x122, 'type': '?', 'field': 'male', 'size': 1},
    # enums
    {'offset': 0x126, 'type': 'B', 'field': 'class', 'size': 1},
    {'offset': 0x127, 'type': 'B', 'field': 'body', 'size': 1},
    {'offset': 0x128, 'type': 'B', 'field': 'gift', 'size': 1},
    {'offset': 0x16c, 'type': 'B', 'field': 'face', 'size': 1},
    {'offset': 0x16d, 'type': 'B', 'field': 'hairs', 'size': 1},
    {'offset': 0x16e, 'type': 'B', 'field': 'color', 'size': 1},
    {'offset': 0x1f128, 'type': 'I', 'field': 'deaths', 'size': 4},
]

ITEMS_MAP = [
    # 0x448 - items start offset
    #{'offset': 0xba4, 'type': 'ii', 'size': 8, 'name': 'estus'}
    #{'offset': 0xb1c, 'type': 'ii', 'size': 8, 'name': 'estus'}
]


class ItemStructure(Structure):
    """ Characters items structure """
    _fields_ = [
        ('type', c_uint32),
        ('amount', c_uint32)
    ]


class SlotHeaderStructure(Structure):
    """ Characters containers slots header structure """
    _fields_ = [
        ('block_metadata_high', c_uint32),    # hex(0x50000000)
        ('block_metadata_low', c_uint32),     # hex(0xFFFFFFFF)
        ('block_size', c_ulong),
        ('block_start_offset', c_uint32),
        ('block_unknown_data_1', c_uint32),  # random
        ('block_unknown_data_2', c_uint32),  # 0x4
        ('end_of_block', c_uint32),
    ]


class DSSaveFileParser(object):
    """ Dark Souls save file parser
    original gist: https://gist.github.com/infuasto/8382836

    :param filename: basestring, bz2.BZ2File or StringIO instances
    """
    _errors = {
        "slot_error": (
            "Dark Souls save file supports only 10 save slots: 0 up to 9")
    }

    def __init__(self, filename):
        self.filename = filename
        if isinstance(self.filename, basestring):
            self._fo = open(self.filename, 'r+b')
        elif isinstance(self.filename, bz2.BZ2File):
            self._fo = self.filename
        elif isinstance(self.filename, StringIO):
            self._fo = self.filename
        else:
            raise FileTypeException("Not supported file format")
        self._active_slots = None
        self._block_slots_amount = None
        self._block_slots_metadata = []

        # check if it's a dark souls save file
        self._fo.seek(0)
        fmt = self._fo.read(4)
        self._fo.seek(0x18)
        version = self._fo.read(8)
        self._fo.seek(0)
        if fmt != 'BND4' and version != '000000001':
            raise FileTypeException("Not an Dark Souls save file")
        self.slots = []

    def _read(self, offset=0x0, size=4):
        self._fo.seek(offset)
        return self._fo.read(size)

    def _seek(self, slot=0):
        """ seek dark souls file handler to slot position in the file
        """
        offset = BLOCK_INDEX + BLOCK_SIZE * slot
        self._fo.seek(offset)
        return offset

    def get_blocks_metadata(self, update=False):
        """ get save file blocks metadata metadata

        :param update: runs re-read blocks metadata process, if False returns
            back cached list
        :return: list of ``SlotHeaderStructure`` instances
        """
        if self._block_slots_metadata and not update:
            return self._block_slots_metadata

        self._fo.seek(SLOTS_AMOUNT_OFFSET)
        self._block_slots_amount = struct.unpack('I', self._fo.read(4))[0]

        self._fo.seek(SLOTS_METADATA_OFFSET)

        fmt, block_size = get_structure_fmt(SlotHeaderStructure)

        for slot in range(0, self._block_slots_amount):
            encoded = struct.unpack(fmt,
                                    self._fo.read(block_size))
            slot = SlotHeaderStructure(*encoded)
            self._block_slots_metadata.append(slot)
        return self._block_slots_metadata

    def get_active_slots_amount(self):
        """ get active slots count, could be 0 up to 9

        :return: active characters' slots amount
        .. code-block:: python

            >>> instance = DSSaveFileParser('saves/DRAKS0005.sl2')
            >>> instance.get_active_slots_amount()
            2 # means that only 2 active characters stored in save file
        """
        slots = 0
        for idx, header in enumerate(self.get_blocks_metadata()):
            self._fo.seek(header.block_start_offset + BLOCK_DATA_OFFSET, 0)
            data = self._fo.read(1)
            if data == '\x00':
                break
            slots += 1
        self._active_slots = slots
        return self._active_slots

    def get_stats(self):
        """ get character stats data

        :return: list of dicts

        .. code-block:: python

            >>> ds = DSSaveFileParser('saves/DRAKS0005.sl2')
            >>> ds.get_stats()[0]
            {'attunement': 11, 'body': 0, 'class': 2, 'color': 7,
             'deaths': 155, 'dexterity': 21, 'earned': 4037210,
             'endurance': 54, 'face': 1, 'faith': 9, 'gift': 1, 'hairs': 5,
             'hp': 1100, 'hp2': 1100, 'hp_current': 1100, 'humanity': 2,
             'intelligence': 11, 'level': 115, 'male': True,
             'name': u'\u041a\u0430\u0440\u043b', 'resistance': 12,
             'souls': 39848, 'stamina': 160, 'stamina2': 160, 'stamina3': 160,
             'strength': 50, 'time': 218834, 'vitality': 30}]

        """
        fo = self._fo
        fo.seek(BLOCK_INDEX, 0)
        slots = []
        if self._active_slots is None:
            self.get_active_slots_amount()
        for slot in range(self._active_slots):
            _offset = BLOCK_INDEX + BLOCK_SIZE * slot
            _time_offset = TIME_INDEX + TIME_BLOCK_SIZE * slot
            fo.seek(_offset, 0)
            storage = {}
            for item in DATA_MAP:
                fo.seek(_offset + item['offset'], 0)
                data = fo.read(item['size'])
                if item['type'] == 'c':
                    encoded = data.decode('utf-16').split('\00')[0]
                elif item['type'] == 'I':
                    encoded = struct.unpack(item['type'], data)[0]
                else:
                    encoded = struct.unpack(item['type'], data)[0]
                storage.update({item['field']: encoded})
            # process time
            fo.seek(_time_offset, 0)
            storage.update({
                'time': struct.unpack('I', fo.read(4))[0]
            })
            slots.append(storage)
        self.slots = slots
        return self.slots

    def get_items(self, slot=0):
        """ get character's item list

        :param slot: character save slot (0 up to 9)
        :return: list of dicts
        """
        if 0 < slot > 9:
            raise IndexError(self._errors["slot_error"])

        offset = self._seek(slot)
        items = []
        for item in ITEMS_MAP:
            self._fo.seek(offset + item['offset'], 0)
            data = self._fo.read(item['size'])
            encoded = struct.unpack(item['type'], data)
            item = {
                'name': item['name'],
                'data': ItemStructure(*encoded)
            }
            items.append(item)
        return items

    def __store_data(self, slot, data=None):
        """ store data in DarkSouls save file.

        Please not that you should control write process because you can
        easily spoil save file with wrong store data on right address or vise
        versa.

        :param slot: slot number, could be 0 up to 9
        :param data: dict of data should be stored

        ``data`` param example:

        .. code-block:: python

            data = {"offset": 0xec, "type": "i", "data": 666}
        """
        if not data:
            data = {}
        if 0 < slot > 9:  # slot < 0 and slot > 9
            raise IndexError(self._errors['slot_error'])
        offset = BLOCK_INDEX + BLOCK_SIZE * slot
        self._fo.seek(offset)
        self._fo.seek(data['offset'], 1)
        store_data = struct.pack(data['type'], data['data'])
        self._fo.write(store_data)


def usage():
    print("%s <filename.sl2>" % sys.argv[0])
    sys.exit(0)


def main():
    filename = sys.argv[1]
    ds = DSSaveFileParser(filename)
    for slot in ds.get_stats():
        slot['skill'] = (
            1
            #300 / (slot['deaths'] or 1) +
            #slot['level']
            #3600 * 3 / float(slot['time']) +
            #850.0 / slot['hp']

        )
        print("Name: %(name)s, deaths: %(deaths)s, skill: %(skill)s" % slot)
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
    if len(sys.argv) <= 1:
        usage()
    main()
