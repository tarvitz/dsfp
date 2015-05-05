# -*- coding: utf-8 -*-
import sys
import logging
import argparse
import struct

from ctypes import (
    c_ulong, byref,
    get_last_error, create_string_buffer
)
from ctypes.wintypes import windll

logger = logging.getLogger(__file__)

OpenProcess = windll.kernel32.OpenProcess
ReadProcessMemory = windll.kernel32.ReadProcessMemory
CloseHandle = windll.kernel32.CloseHandle

PROCESS_ALL_ACCESS = 0x1F0FFF


def memory_read(pid, address, size):
    """
    read process memory

    :param int pid: process id for investigating
    :param int address: start memory address
    :param int size: block size to read
    :rtype: None
    :return: None
    """
    read_buffer = create_string_buffer(size)  # c_char_p("data to read")
    buffer_size = c_ulong(size)
    bytes_read = c_ulong(0)

    process_handle = OpenProcess(PROCESS_ALL_ACCESS, False, pid)
    if not process_handle:
        print("Process can not be opened: %d" % get_last_error())
        return

    state = ReadProcessMemory(process_handle, address, read_buffer,
                              buffer_size, byref(bytes_read))

    if state:
        # print("state: %d" % state)
        # print("something found: %s" % read_buffer.raw)
        print("bytes read: %d" % buffer_size.value)
        if bytes_read.value == size and len(read_buffer.raw) == size:
            data = struct.unpack('I' * (size / 4), read_buffer.raw)
            print(" ".join(['0x%08x' % x for x in data]))
        else:
            pass
    else:
        print("fail, get last error: %d, state: %d" % (
            get_last_error(), (state or 0)))
    CloseHandle(process_handle)


def main(ns):
    address = int(ns.address, 16)
    params = {
        'address': address,
        'pid': ns.pid,
        'size': ns.size
    }
    memory_read(**params)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Searches some data inside memory block.'
    )
    parser.add_argument('-a', '--address', dest="address",
                        type=str,
                        help='address', required=True)
    parser.add_argument('-p', '--pid', dest='pid',
                        type=int,
                        help='process pid')
    parser.add_argument('-s', '--size', dest='size',
                        type=int,
                        help="block size to read")

    arguments = parser.parse_args(sys.argv[1:])
    main(arguments)
