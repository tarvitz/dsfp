# coding: utf-8
from unittest import TestCase
from dsfp.utils import get_structure_fmt
from dsfp.dsfp import SlotHeaderStructure

__all__ = ['TestUtils', ]


class TestUtils(TestCase):
    """Utils tests """
    maxDiff = None
    fmt_slot_header = 'IIQIIII'  # 4, 4, 8, 4, 4, 4, 4
    block_size_slot_header = 4 + 4 + 8 + 4 * 4

    def setUp(self):
        pass

    def test_get_structure_fmt(self):
        """ test ``utils.get_structure_fmt`` routine function """
        fmt, block_size = get_structure_fmt(SlotHeaderStructure)
        self.assertEqual(fmt, self.fmt_slot_header)
        self.assertEqual(block_size, self.block_size_slot_header)