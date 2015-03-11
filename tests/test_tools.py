# coding: utf-8
import six
from unittest import TestCase
from dsfp.tools import BinDiff

__all__ = ['TestBinDiff', ]


class TestBinDiff(TestCase):
    """Tools tests """
    maxDiff = None
    diff_a = six.b('\x00\x01\x00\x04\x44\x53\x60\x34\x90\x88\x13\x08')
    diff_b = six.b('\x01\x00\x00\x04\x42\x53\x61\x34\x93\x88\x13\x08')
    skip_tables = (
        {
            'SKIP_TABLE': [
                {"comment": "unknown data", "offset": 0, "size": 2},
            ]
        },
    )
    diff = [
        {'diff': [0, 1], 'offset': 0},
        {'diff': [0, 2], 'offset': 4},
        {'diff': [0], 'offset': 8}
    ]
    diff_patched = [
        {'diff': [0, 2], 'offset': 4},
        {'diff': [0], 'offset': 8}
    ]

    def setUp(self):
        pass

    def test_bin_diff_match(self):
        diff_obj = BinDiff(self.diff_a, self.diff_b)
        diff = diff_obj.process_diff()
        self.assertEqual(diff, self.diff)

    def test_bin_diff_patch_table(self):
        diff_obj = BinDiff(self.diff_a, self.diff_b,
                           skip_tables=self.skip_tables)
        diff = diff_obj.process_diff()
        self.assertEqual(diff, self.diff_patched)