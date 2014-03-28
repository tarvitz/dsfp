#!/usr/bin/env python
# -*- coding: utf-8 -*-
import bz2
import six

import struct
from ctypes import *

from .utils import *
from .exceptions import *
from .constants import *


class SlotDataHeaderStructure(Structure):
    """ Character Slot Data possible container"""
    _fields_ = [
        ('block_stat_size', c_uint32),
        ('block_data_size', c_uint32)
    ]


class SlotHeaderStructure(Structure):
    """ Characters containers slots header structure """
    #_anonymous_ = ("slot_data",)
    _fields_ = [
        ('block_metadata_high', c_uint32),    # hex(0x50000000)
        ('block_metadata_low', c_uint32),     # hex(0xFFFFFFFF)
        ('block_size', c_ulong),
        ('block_start_offset', c_uint32),
        ('block_unknown_data_1', c_uint32),  # random
        ('block_skip_bytes', c_uint32),  # byte skipping amount
        ('end_of_block', c_uint32),
        ('slot_data', SlotDataHeaderStructure)
    ]


class ItemStructure(Structure):
    """ Character item storage structure """
    _fields_ = [
        # stored, 0xFFFFFFFF - not in inventory
        # 0x00000000 - weapon, bolts/arrows, stored in inventory
        # 0x10000000 - armour, you know what ;)
        # 0x20000000 - rings
        # 0x30000000 - ?
        # 0x40000000 - item, stored in inventory
        ('stored', c_uint32),
        ('type', c_uint32),             # item type
        ('amount', c_uint32),           # item amount stored in your backpack
        ('position', c_uint32),         # inventory position
        ('have', c_uint32),             # item is stored in inventory 1 or 0
        ('durability', c_uint32),       # item durability
        ('durability_hits', c_uint32),  # 0->9 than -1 of durability
    ]


class DSSaveFileParser(object):
    """ Dark Souls save file parser
    original gist: https://gist.github.com/infuasto/8382836

    :param filename: bz2.BZ2File or StringIO instances
    """
    _errors = {
        "slot_error": (
            "Dark Souls save file supports only 10 save slots: 0 up to 9")
    }

    def __init__(self, filename):
        self.filename = filename
        if isinstance(self.filename, six.string_types):
            self._fo = open(self.filename, 'r+b')
        elif isinstance(self.filename, bz2.BZ2File):
            self._fo = self.filename
        elif isinstance(self.filename, six.StringIO):
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

        if fmt != six.b('BND4') and version != six.b('000000001'):
            raise FileTypeException("Not an Dark Souls save file")
        self.slots = []

    def _seek(self, slot=0):
        """ seek dark souls file handler to slot position in the file """
        offset = BLOCK_INDEX + BLOCK_SIZE * slot
        self._fo.seek(offset)
        return offset

    def close(self):
        """ close all instances """
        self._fo.close()

    def get_blocks_metadata(self, update=False):
        """ Get save file blocks metadata

        :keyword bool update: runs re-read blocks metadata process,
            if False returns back cached list
        :return: ``SlotHeaderStructure`` instances
        :rtype: list

        """
        if self._block_slots_metadata and not update:
            return self._block_slots_metadata

        self._fo.seek(SLOTS_AMOUNT_OFFSET)
        self._block_slots_amount = struct.unpack('I', self._fo.read(4))[0]

        self._fo.seek(SLOTS_METADATA_OFFSET)

        fmt, block_size = get_structure_fmt(SlotHeaderStructure)

        for slot in range(0, self._block_slots_amount):
            encoded = struct.unpack(fmt, self._fo.read(block_size))
            slot = SlotHeaderStructure()
            for idx, field in enumerate(SlotHeaderStructure._fields_):
                if field[1] in (c_uint32, c_ulong,):
                    setattr(slot, field[0], encoded[idx])
            self._block_slots_metadata.append(slot)

        # update slot data
        for slot in self._block_slots_metadata:
            self._fo.seek(slot.block_start_offset + slot.block_skip_bytes * 4)
            block_size = struct.unpack('I', self._fo.read(4))[0]
            slot_data = SlotDataHeaderStructure()
            slot_data.block_stat_size = slot.block_size - block_size
            slot_data.block_data_size = block_size
            slot.slot_data = slot_data
        return self._block_slots_metadata

    def get_active_slots_amount(self):
        """get active slots count, could be 0 up to 9

        :return: active characters' slots amount
        :rtype: int

        .. code-block:: python

            >>> instance = DSSaveFileParser('saves/DRAKS0005.sl2')
            >>> instance.get_active_slots_amount()
            2 # means that only 2 active characters stored in save file
        """

        slots = 0
        for idx, header in enumerate(self.get_blocks_metadata()):
            self._fo.seek(header.block_start_offset + BLOCK_DATA_OFFSET, 0)
            data = self._fo.read(1)
            if data == six.b('\x00'):
                break
            slots += 1
        self._active_slots = slots
        return self._active_slots

    def get_stats(self):
        """ get character stats data

        :return: dicts
        :rtype: list

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
        for slot in range(self._active_slots or 0):
            _offset = BLOCK_INDEX + BLOCK_SIZE * slot
            _time_offset = TIME_INDEX + TIME_BLOCK_SIZE * slot
            fo.seek(_offset, 0)
            storage = {}
            for item in DATA_MAP:
                fo.seek(_offset + item['offset'], 0)
                data = fo.read(item['size'])
                if item['type'] == 'c':
                    encoded = data.decode('utf-16').split('\x00')[0]
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
        """ get character's item list, don't work proper for now

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

    def read_slot_data(self, slot=0):
        """ read raw data of given slot

        :keyword int slot: character slot
        :return: character block bytes
        :rtype: str
        """
        if not self._block_slots_metadata:
            self.get_blocks_metadata()
        slot_block = self._block_slots_metadata[slot]
        self._fo.seek(slot_block.block_start_offset)
        return self._fo.read(slot_block.block_size)

    def __store_data(self, slot, data=None):
        """ store data in DarkSouls save file.

        Please not that you should control write process because you can
        easily spoil save file with wrong store data on right address or vise
        versa.

        :param int slot: slot number, could be 0 up to 9
        :keyword dict data: dict of data should be stored
        :return: None
        :rtype: None

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
