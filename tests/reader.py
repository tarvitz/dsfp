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

    def test_read_ds_file(self):
        """ test get character dark souls file slots """

        ds = DSSaveFileParser(filename=self.filename)
        data = ds.get_slots()
        self.assertEqual(data, self.valid_slots)

    def test_read_ds_slot_stats(self):
        ds = DSSaveFileParser(filename=self.filename)
        data = ds.get_stats()
        for (idx, slot) in enumerate(data):
            self.assertEqual(slot['deaths'], self.slots[idx]['deaths'])
            self.assertEqual(slot['name'], self.slots[idx]['name'])