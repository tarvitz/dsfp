# -*- coding: utf-8 -*-
""" DSFP constants and routines

.. module:: dsfp.constants
    :platform: Linux, Windows, MacOS X
    :synopsis: utils for routines
.. moduleauthor:: Tarvitz<tarvitz@blacklibrary.ru>
"""

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

    {'offset': 0x54, 'type': 'I', 'field': '0x54', 'size': 4},
    {'offset': 0x58, 'type': 'I', 'field': '0x58', 'size': 4},
    {'offset': 0x5c, 'type': 'I', 'field': '0x5c', 'size': 4},
    {'offset': 0x60, 'type': 'I', 'field': '0x60', 'size': 4},
    {'offset': 0x6c, 'type': 'I', 'field': 'hp_current', 'size': 4},
    {'offset': 0x70, 'type': 'I', 'field': 'hp', 'size': 4},
    # what's the difference?
    {'offset': 0x74, 'type': 'I', 'field': 'hp2', 'size': 4},
    # unrevealed
    {'offset': 0x78, 'type': 'I', 'field': '0x78', 'size': 4},
    # same as 0x78
    # {'offset': 0x7c, 'type': 'I', 'field': '0x7c', 'size': 4},
    # same as 0x78
    # {'offset': 0x80, 'type': 'I', 'field': '0x80', 'size': 4},

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

    {'offset': 0x100, 'type': 'c', 'field': 'name', 'size': 14 * 2},
    {'offset': 0x122, 'type': '?', 'field': 'male', 'size': 1},
    # enums
    {'offset': 0x126, 'type': 'B', 'field': 'class', 'size': 1},
    {'offset': 0x127, 'type': 'B', 'field': 'body', 'size': 1},
    {'offset': 0x128, 'type': 'B', 'field': 'gift', 'size': 1},
    {'offset': 0x16c, 'type': 'B', 'field': 'face', 'size': 1},
    {'offset': 0x16d, 'type': 'B', 'field': 'hairs', 'size': 1},
    {'offset': 0x16e, 'type': 'B', 'field': 'color', 'size': 1},
    {'offset': 0x2c0, 'type': 'I', 'field': 'slot_1', 'size': 4},
    {'offset': 0x2c4, 'type': 'I', 'field': 'slot_2', 'size': 4},
    {'offset': 0x2c8, 'type': 'I', 'field': 'slot_3', 'size': 4},
    {'offset': 0x2cc, 'type': 'I', 'field': 'slot_4', 'size': 4},
    {'offset': 0x2d0, 'type': 'I', 'field': 'slot_5', 'size': 4},
    {'offset': 0x1f128, 'type': 'I', 'field': 'deaths', 'size': 4},
]

ITEMS_MAP = [
    # 0x448 - items start offset
    # {'offset': 0xba4, 'type': 'ii', 'size': 8, 'name': 'estus'}
    # {'offset': 0xb1c, 'type': 'ii', 'size': 8, 'name': 'estus'}
]
