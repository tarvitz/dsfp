# coding: utf-8
from unittest import TestCase
from dsfp.tools import BinDiff

__all__ = ['TestBinDiff', ]


class TestBinDiff(TestCase):
    """Tools tests """
    maxDiff = None
    diff_a = '\x00\x01\x00\x04\x44\x53\x60\x34\x90\x88\x13\x08'
    diff_b = '\x01\x00\x00\x04\x42\x53\x61\x34\x93\x88\x13\x08'
    skip_table = {}
    diff = [
        {'diff': [0, 1], 'offset': 0},
        {'diff': [0, 2], 'offset': 4},
        {'diff': [0], 'offset': 8}
    ]

    def setUp(self):
        pass

    def test_bin_diff_match(self):
        diff_obj = BinDiff(self.diff_a, self.diff_b)
        diff = diff_obj.process_diff()
        self.assertEqual(diff, self.diff)