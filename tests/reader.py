# coding: utf-8
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
                              2362400, 2756016, 3149632, 3543248, 3936864]
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
        for idx, header in enumerate(metadata):
            self.assertEqual(header.block_start_offset,
                             self.metadata['start_offsets'][idx])
