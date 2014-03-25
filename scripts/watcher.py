import sys
import os
import struct
PROJECT_ROOT = os.path.pardir


def rel(path):
    return os.path.join(PROJECT_ROOT, path)

sys.path.insert(0, os.path.join(PROJECT_ROOT, 'dsfp'))

from datetime import datetime
from cStringIO import StringIO
from time import sleep
from dsfp import DSSaveFileParser
from dsfp.constants import *
from dsfp.tools import BinDiff
from dsfp.exceptions import ImproperlyConfigured
import simplejson as json
import argparse
import curses


SNAPSHOT_DIR = os.path.join(os.getcwdu(), 'snapshots')


class SimpleWatcher(object):
    """ Simple watcher

    :param str filename: path inspected filename
    :param int slot: character slot
    :param bool dumping: dump snapshots of inspected slot data
    :param dict namespace_load: namespace load
    """
    def __init__(self, filename, slot=0, dumping=False, namespace_load=None,
                 namespace_skip=None, skip_table=None, use_curses=False,
                 start_offset=0x0, end_offset=127384,
                 *args, **kwargs):
        self.filename = filename
        self.slot = slot
        self.dumping = dumping
        self.namespace_load = namespace_load
        self.namespace_skip = namespace_skip
        self.skip_table = skip_table
        self.use_curses = use_curses
        self.start_offset = start_offset
        self.end_offset = end_offset

        if self.use_curses:
            self.screen = curses.initscr()
            self.screen.border(0)
            self.screen.refresh()

            self.pos = self.screen.getmaxyx()

            self.console = curses.newpad(self.pos[0], 30)
            self.console.border(0)

    def close(self):
        """
        closes all instances and so on
        """
        if self.use_curses:
            self.screen.refresh()
            curses.endwin()

    def show_windows(self):
        """
        show startup windows
        """

        self.log("%s run" % self.__class__.__name__, refresh=True)
        self.log("prcess Ctrl+C to exit", self.pos[0] - 1, 2)

        self.log(
            ' %(addr)10s[%(saddr)10s] %(value)10s %(hex)10s %(follow)5s'
            '%(value_modified)10s %(hex_modified)10s' % {
                'addr': "Address",
                'saddr': 'Decimal',
                'value': 'Value',
                'hex': 'Hex',
                'value_modified': 'Value',
                'hex_modified': 'Hex',
                'follow': '<-'
            },
            x=0, y=0
        )

        self.console_log("[*] Console initiated")

    def log(self, out, x=1, y=1, refresh=True, clean=True):
        """
        log into the main window
        :keyword bool refresh: True if should be refreshed
        """
        if clean:
            pass

        if self.use_curses:
            self.screen.addstr(x, y, out)
            if refresh:
                self.screen.refresh()
        else:
            print(out)

    def console_log(self, out, x=1, y=1, clean=False):
        if self.use_curses:
            if clean:
                self.console.addstr(x, y, " " * 28)

            self.console.addstr(x, y, out)
            y = self.pos[1] - 30
            self.console.refresh(
                0, 0,
                0, y,
                self.pos[0], self.pos[1]
            )
        else:
            print(out)

    def run(self):
        #self.show_windows()

        modified = 0
        old_stat = os.lstat(self.filename)
        stat = os.lstat(self.filename)
        fo = open(self.filename, 'rb')
        fo.seek(BLOCK_INDEX + self.slot * BLOCK_SIZE)
        old_data = fo.read(BLOCK_SIZE)
        fo.close()

        while 1:
            sleep(1)
            stat = os.lstat(self.filename)
            if stat.st_mtime != old_stat.st_mtime:
                old_stat = stat
                t_modify = "%s modified (%s)" % (
                    datetime.now().strftime('%H:%M:%S'), modified)
                self.console_log(t_modify, clean=True)
                ds = DSSaveFileParser(self.filename)
                data = ds.read_slot_data(self.slot)
                ds.close()

                data_stream = StringIO(data)
                old_data_stream = StringIO(old_data)

                diff = BinDiff(data, old_data,
                               skip_table=self.skip_table['SKIP_TABLE'],
                               start_offset=self.start_offset,
                               end_offset=self.end_offset,)
                diff_log = diff.process_diff()

                self.console_log("Differences: %i" % len(diff_log), x=2)

                for idx, log in enumerate(diff_log):
                    data_stream.seek(log['offset'])
                    old_data_stream.seek(log['offset'])

                    diff_data = struct.unpack('I', data_stream.read(4))[0]
                    diff_data_old = struct.unpack(
                        'I', old_data_stream.read(4))[0]
                    fmt = (
                        "0x%(addr)08x[%(saddr)10s] %(value)10s 0x%(hex)08x "
                        "%(follow)5s %(old)10s 0x%(old_hex)08x" % {
                            'addr': log['offset'],
                            'saddr': log['offset'],
                            'value': diff_data,
                            'hex': diff_data,
                            'old': diff_data_old,
                            'old_hex': diff_data_old,
                            'follow': '<-'
                        }
                    )
                    self.log(fmt, x=idx + 1, refresh=True)

                old_data = data
                # process stat smth
                modified += 1

            #stat = os.stat(self.filename)

    def old_run(self):
        """ run watcher """
        self.show_windows()

        stat = os.stat(self.filename)
        old_time = stat.st_mtime
        snapshot = 1
        modified = 0

        while 1:
            sleep(1)
            stat = os.stat(self.filename)
            if stat.st_mtime != old_time:
                old_time = stat.st_mtime
                fmt = datetime.now().strftime('%H:%M:%S')
                #print("%(time)s modified" % {'time': fmt})
                self.console_log(
                    "%(time)s modified (%(amount)s)" % {
                        'time': fmt, 'amount': modified},
                    clean=True
                )

                ds = DSSaveFileParser(self.filename)

                snapshot_filename = (
                    'slot_%(slot)s_snapshot_%(snapshot)s.bin' % {
                        'slot': self.slot,
                        'snapshot': snapshot
                    }
                )

                data = ds.read_slot_data(self.slot)
                stream = StringIO(data)
                if self.dumping:
                    open(
                        os.path.join(
                            SNAPSHOT_DIR, snapshot_filename), 'wb'
                    ).write(data)

                if self.namespace_load:
                    x = 1
                    old_value = None
                    for offset in self.namespace_load['WATCH_OFFSETS']:
                        stream.seek(offset['offset'])
                        value = struct.unpack(offset['type'],
                                              stream.read(offset['size']))[0]

                        if old_value != value:
                            old_value = value
                        addr = '0x%(offset)08x' % {'offset': offset['offset']}
                        dec_value = '%(value)10s'
                        hex_value = '0x%(value)08x'

                        #print(out)
                        self.log(addr, x=x)
                        self.log(dec_value % {"value": value}, y=10, x=x)
                        self.log(hex_value % {"value": value}, y=25, x=x)
                        self.log(dec_value % {"value": old_value}, y=40, x=x)
                        self.log(hex_value % {"value": old_value}, y=55, x=x)
                        x += 1

                if self.skip_table:
                    pass

                modified += 1
                snapshot += 1
                ds._fo.close()


def main(ns):
    slot = ns.slot[0] - 1
    filename = ns.filename[0]
    use_dumping = ns.use_snapshots
    use_curses = ns.use_curses
    backup = ns.backup
    load = None
    skip = None
    skip_table = None
    start_offset = ns.start_offset
    end_offset = ns.end_offset

    if all([start_offset, end_offset]):
        try:
            start_offset = int(start_offset, 16)
            end_offset = int(end_offset, 16)
        except ValueError:
            raise ImproperlyConfigured("start should be int instance compatible")

    if ns.insert_json:
        load = json.loads(ns.insert_json.read())

    if ns.skip_json:
        skip = json.loads(ns.skip_json.read())

    if ns.skip_table:
        skip_table = json.loads(ns.skip_table.read())

    if use_dumping:
        print("Using snapshot dumping to `%s`" % SNAPSHOT_DIR)

    if not os.path.exists(SNAPSHOT_DIR):
        os.makedirs(SNAPSHOT_DIR)
    if backup:
        path = 'backups/draks0005.sl2_backup'
        open(path, 'wb').write(open(filename, 'rb').read())

    keywords = {}
    if all([start_offset, end_offset]):
        keywords.update({
            'start_offset': start_offset, 'end_offset': end_offset})

    watcher = SimpleWatcher(slot=slot, filename=filename,
                            use_dumping=use_dumping, namespace_load=load,
                            namespace_skip=skip,
                            skip_table=skip_table,
                            use_curses=use_curses,)
    try:
        watcher.run()
    except KeyboardInterrupt:
        watcher.close()
        print("\nCatch Ctrl+C, exiting ..")
        sys.exit(0)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Prints changes for darksouls save file.'
    )
    parser.add_argument('-f', '--filename', metavar='draks0005.sl2',
                        type=str, nargs=1,
                        help='save file', required=True)
    parser.add_argument('-s', '--slot', metavar='N', type=int, nargs=1,
                        default=1,
                        help='character slot')
    parser.add_argument('-u', '--use-snapshots',
                        action='store_true',
                        help='use dumping slot block if on')
    parser.add_argument('-i', '--insert-json', metavar='params.json',
                        type=file,
                        help='use whole data from json file',
                        required=False)
    parser.add_argument('-S', '--skip-json', metavar='params.json',
                        type=file,
                        help='use data inside of json file for skipping',
                        required=False)
    parser.add_argument('-T', '--skip-table', metavar='table.json',
                        type=file,
                        help=(
                            'use data inside of json file for skipping diff'
                            'check inside of block with given offsets'),
                        required=False)
    parser.add_argument('-c', '--use-curses', action='store_true',
                        help='use curses interface')
    parser.add_argument('-b', '--backup', action='store_true',
                        help='backup original file before it get accessed')
    parser.add_argument('-B', '--start-offset',
                        type=str, required=False,
                        help='start offset for inspections')
    parser.add_argument('-E', '--end-offset',
                        type=str, required=False,
                        help='end offset for inspections')

    arguments = parser.parse_args(sys.argv[1:])
    main(arguments)
