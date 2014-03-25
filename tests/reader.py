# coding: utf-8
""" DSFP core file

.. module:: dsfp.dsfp
    :platform: Linux, Windows, MacOS X
    :synopsis: utils for routines
.. moduleauthor:: Tarvitz<tarvitz@blacklibrary.ru>
"""

from unittest import TestCase
from dsfp import DSSaveFileParser
import bz2

__all__ = ['TestDSFPReader', ]


class TestDSFPReader(TestCase):
    """DSFP parser reader unit tests"""
    maxDiff = None

    def setUp(self):
        self.filename = bz2.BZ2File('saves/DRAKS0005.sl2.bz2')
        # slots starts with 0
        self.valid_slots = 2
        self.slots = [
            {
                'deaths': 155,
                'name': u'Карл',
            },
            {
                'deaths': 0,
                'name': u'Максимилиантр'
            },
            {
                'deaths': 0,
                'name': 'Smithy'
            }
        ]
        self.metadata = {
            'slots': 11,
            # it's always constant because of fixed block size
            # but there's a header that contains block offsets inside of
            # meta data block so we should check it
            'start_offsets': [704, 394320, 787936, 1181552, 1575168, 1968784,
                              2362400, 2756016, 3149632, 3543248, 3936864],
            'block_stat_size': [396, 396, 396, 396, 396, 396, 396, 396,
                                396, 396, 396]
        }

    def test_read_ds_file(self):
        """ test get character dark souls file slots """

        ds = DSSaveFileParser(filename=self.filename)
        data = ds.get_active_slots_amount()
        self.assertEqual(data, self.valid_slots)

    def test_read_ds_slot_stats(self):
        ds = DSSaveFileParser(filename=self.filename)
        data = ds.get_stats()
        for (idx, slot) in enumerate(data):
            self.assertEqual(slot['deaths'], self.slots[idx]['deaths'])
            self.assertEqual(slot['name'], self.slots[idx]['name'])

    def test_read_ds_file_metadata(self):
        """ read file metadata """
        ds = DSSaveFileParser(filename=self.filename)
        metadata = ds.get_blocks_metadata()

        self.assertEqual(len(metadata), self.metadata['slots'])
        messages = []
        for idx, header in enumerate(metadata):
            self.assertEqual(header.block_start_offset,
                             self.metadata['start_offsets'][idx])
            try:
                self.assertEqual(header.slot_data.block_stat_size,
                                 self.metadata['block_stat_size'][idx])
            except AssertionError as err:
                messages.append({'err': err, 'msg': 'Got error'})

        if messages:
            for msg in messages:
                print("%(msg)s: %(err)s" % msg)
            raise AssertionError